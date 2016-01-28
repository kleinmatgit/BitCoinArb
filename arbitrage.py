try:
    import exchange_utils as u
    from exchange import Exchange
    from logger_handler import loggerHandler
except ImportError:
    pass

#log arbitrage opportunites
#return an arbitrage tuple (pair,total_profit,profit repartition per exchange)
def log_arbitrage(exchanges,pairs,logger,profit_usd_min=10.0,details=False):

    try:
        resultDetails = 'Arbitrage opportunities details:\n'
        resultSummary = 'Arbitrage opportunities summary:\n'
        listResult = []
        
        #we are going to adjust exchanges after each potential buy/sell
        #so we need a copy here
        exchanges_copy = exchanges.copy()
        
        for pair in pairs:

            #we assume there is arb opportunity
            hasArb = True
            atLeastOne = False
            total_profit_usd = 0.0
            asset1,asset2 = u.getAssetsFromPair(pair)
            dicExchange = {}
            
            while hasArb:
            
                #search for lowest offer/higher bid
                bid,ask,vol_bid,vol_ask,bid_exch,ask_exch = searchBest(pair,exchanges_copy)
                volume = min(vol_bid,vol_ask)

                if bid==None or ask==None or volume==None:
                    break
                
                #profit in USD differs according to the pair:   
                #case XXX/USD (easiest)
                if asset2=='usd':
                    profit_usd = (bid-ask)*volume
                    order1 = 0
                    order2 = 1
                    
                else:
                    
                    #here we need btc-usd
                    btc_usd_fxrate = getAveragePrice(exchanges_copy,'btc-usd')
                    
                    #case XXX/BTC
                    if asset2=='btc':
                        profit_usd = (bid-ask)*volume*btc_usd_fxrate
                        order1 = 0
                        order2 = 1
                    
                    #case BTC/XXX
                    elif asset1=='btc':

                        #here we need to reverse pair from BTC/XXX to XXX/BTC
                        #to handle it the same way as previous case
                        bidtmp = bid
                        bid = 1/ask
                        ask = 1/bidtmp
                        exchtmp = bid_exch
                        bid_exch = ask_exch
                        ask_exch = exchtmp
                        order1 = 1
                        order2 = 0

                        profit_usd = (bid-ask)*volume*btc_usd_fxrate

                #if USD profit>0, we log and update the exchange accordingly
                if profit_usd > 0:
                    atLeastOne = True
                    total_profit_usd += profit_usd
                    resultDetails += (pair + ': ' +
                                     'buy ' + str(round(volume,4)) + ' ' + asset1 + ' from ' + ask_exch + ' @' + str(round(ask,4)) + ',' +
                                     ' sell it to ' + bid_exch + ' @' + str(round(bid,4)) +
                                     ' for a profit of $' + str(round(profit_usd,2)) +
                                     ' (total profit $' + str(round(total_profit_usd,2)) + ')\n')
                    u.getExchange(exchanges_copy,ask_exch).executeMarketOrder(order1,pair,volume)
                    u.getExchange(exchanges_copy,bid_exch).executeMarketOrder(order2,pair,volume)

                    updateDicExchangeCouple(dicExchange,ask_exch + '%%%' + bid_exch,profit_usd)
                    
                #if profit is negative, we are done with this pair..
                else:
                    hasArb = False
                    if atLeastOne:
                        resultDetails += '----------------------------------------------------------------------------------------------------\n'
            
            if total_profit_usd>profit_usd_min:
                exchange_couple_list = dicToList(dicExchange)
                exchange_couple_list.sort(reverse=True)
                listResult.append((total_profit_usd,pair,exchange_couple_list))
    
        #we log all info at the end of the procedure
        listResult.sort(reverse=True)
        if len(listResult)==0:
            resultSummary = 'There is no arbitrage opportunity superior to $' + str(round(profit_usd_min,2))
        else:
            for v in listResult:
                resultSummary += v[1] + ': $' + str(round(v[0],2))
                for t in v[2]:
                    exch_from,exch_to = getExchFromCouple(t[1])
                    resultSummary += ' [$' + str(round(t[0],2)) + ' from ' + exch_from + ' to ' + exch_to + ']'
                resultSummary += '\n'
        
        if details:
            logger.info('\n########################################################\n' +
                        resultSummary + '****************************************************\n' +
                        resultDetails,bPrint=True)
        else:
            logger.info('\n########################################################\n' +
                        resultSummary,bPrint=True)

        return listResult

    except Exception as e:
        logger.fatal(str(e))
        return None
            
#search best bid or offer among exchanges
def searchBest(pair,exchanges):

    best_bid = 0.0
    best_ask = 10e10
    best_vol_bid = 0.0
    best_vol_ask = 0.0
    best_bid_exch = ''
    best_ask_exch = ''

    for exchange in exchanges:
        if pair in exchange.pairs:
            bid,ask,vol_bid,vol_ask = exchange.getBestBidOffer(pair,withVolume=True)

            if ask!=None:
                if ask < best_ask:
                    best_ask = ask
                    best_vol_ask = vol_ask
                    best_ask_exch = exchange.name
            
            if bid!=None:
                if bid > best_bid:
                    best_bid = bid
                    best_vol_bid = vol_bid
                    best_bid_exch = exchange.name

    #volume = min(best_vol_bid,best_vol_ask)
    
    return (best_bid,best_ask,
            best_vol_bid,best_vol_ask,
            best_bid_exch,best_ask_exch)

#get the average price of a pair within the list of exchanges
def getAveragePrice(exchanges,pair):
    prices = []
    for exchange in exchanges:
        if pair in exchange.pairs:
            bid,ask = exchange.getBestBidOffer(pair)
            if bid!=None:
                prices.append(bid)
            if ask!=None:
                prices.append(ask)
    if len(prices)==0:
        raise Exception('getAveragePrice: could not find any price for pair ' + pair)
    try:
        sum_prices = sum(prices)
    except Exception as e:
        print('exception for pair ' + pair + ': ' + str(e))
        return None
    return sum(prices)/len(prices)        

#update dictionary of exchange couple (ie: btc-e%%%okcoin)
#by adding profit_usd to existing figure
def updateDicExchangeCouple(dicExch,exchange_couple,profit_usd):
    if exchange_couple not in dicExch:
        dicExch.update({exchange_couple:profit_usd})
    else:
        new_profit = dicExch.get(exchange_couple) + profit_usd
        dicExch.update({exchange_couple:new_profit})

#convert dictionary to list of tuple (profit,name)
def dicToList(dic):
    l = []
    for k in dic.keys():
        l.append((round(dic.get(k),2),k))
    return l

#convert dictionary of {pair:(prct,nbr,sum_profit,dicExchCouple)}
#to list of tuple (prct,pair,avg_profit,[avg_profit,exch_couple])
def dicToListArb(dic):
    l = []
    for k in dic.keys():
        prct,nbr,sum_profit,dicExchCouple = dic.get(k)
        avg_profit = sum_profit/nbr
        listExchCouple = dicExchCoupleToList(dicExchCouple)
        listExchCouple.sort(reverse=True)
        l.append((prct,k,round(avg_profit,2),listExchCouple))
    return l

#convert a list of tuple (profit,exchanges_couple)
#into a dic defined as: {exchange_couple:(nbr,sum_profit)}
def listExchCoupleToDic(l):
    dic = {}
    for t in l:
        dic.update({t[1]:(1,t[0])})
    return dic

#convert a dic defined as: {exchange_couple:(nbr,sum_profit)}
#into a list of tuple (avg_profit,exchange_couple)
def dicExchCoupleToList(dic):
    l = []
    for k in dic.keys():
        avg_profit = dic.get(k)[1]/dic.get(k)[0]
        l.append((round(avg_profit,2),k))
    return l
    
#return exchanges name from a string of type: 'btc-e%%%okcoin'
def getExchFromCouple(couple):
    idash = couple.index('%%%')
    return couple[:idash],couple[idash+3:]

#merge 2 dicExchCouple by suming profit
#dicExch contains the existing dicExch
#newDicExch contains the new dic which value we need to sum up
#a dicExchCouple is defined as: {exchange_couple:(nbr,sum_profit)}
def mergeDicExchCouple(dicExch,newDicExch):
    for exchCouple in newDicExch:
        profit = newDicExch.get(exchCouple)[1]
        if exchCouple not in dicExch:
            dicExch.update({exchCouple:(1,profit)})
        else:
            nbr,sum_profit = dicExch.get(exchCouple)
            nbr += 1
            sum_profit += profit
            dicExch.update({exchCouple:(nbr,sum_profit)})
 
#log stats about group of arbitrage
#to figure out what are the most reliable arb opportunities
def log_arbitrages_stats(arbitrages,logger):

    total_arb = len(arbitrages)

    if total_arb==0:
        msg = 'there was no arbitrage to get stats from'
        logger.warning(msg,bPrint=False)
        return msg
    
    #we are going to maintain a dic of pair containing tuple of:
    #prct (% of arb for given pair in regard of total # arb)
    #nbr (#arb total for given pair)
    #avg_profit (average profit in USD for given pair)
    #dicExchangesCouple (dictionary of exchanges couple to keep track of arb details)
    dicPair = {}

    for arbitrage in arbitrages:
        
        profit,pair,exchanges_couple = arbitrage
        dicExchangesCouple = listExchCoupleToDic(exchanges_couple)
        
        if pair not in dicPair:
            dicPair.update({pair:(1/total_arb,1,profit,dicExchangesCouple)})
        else:
            prct,nbr,sum_profit,dicExchCouple = dicPair.get(pair)
            nbr += 1
            prct = nbr/total_arb
            sum_profit += profit
            mergeDicExchCouple(dicExchCouple,dicExchangesCouple)
            dicPair.update({pair:(prct,nbr,sum_profit,dicExchCouple)})

    #convert dic to list sorted by %arb descending
    listArb = dicToListArb(dicPair)
    listArb.sort(reverse=True)
    
    #log result
    msg = 'Arbitrages stats:\n'
    for arb in listArb:
        prct,pair,avg_profit,listExchCouple = arb
        msg += pair + ': ' + str(round(prct*100,2)) + '% of total arbs for $' + str(avg_profit) + ' avg profit '
        for exchCouple in listExchCouple:
            exchFrom,exchTo = getExchFromCouple(exchCouple[1])
            msg += '[$' + str(exchCouple[0]) + ' ' + exchFrom + ' to ' + exchTo + ']'
        msg += '\n'
    s = '\n########################################################\n'
    logger.info(s + msg + s,bPrint=False)

    return msg
    
if __name__=='__main__':

    
    logger = loggerHandler('test_arbitrages_stats',log_path='log/')

    arbitrages = [[484.91,'btc-usd',[(444.3,'btc-e%%%okcoin'),(36.84,'btc-e%%%hitbtc'),(3.77,'btc-e%%%bter')]],
                  [484.91,'ltc-usd',[(444.3,'btc-e%%%okcoin'),(36.84,'btc-e%%%hitbtc'),(3.77,'btc-e%%%bter')]],
                  [384.91,'btc-usd',[(344.3,'btc-e%%%okcoin'),(36.84,'btc-e%%%hitbtc'),(3.77,'btc-e%%%bter')]],
                  [384.91,'ltc-usd',[(344.3,'btc-e%%%okcoin'),(36.84,'btc-e%%%hitbtc'),(3.77,'btc-e%%%bter')]],
                  [284.91,'btc-usd',[(184.91,'btc-e%%%okcoin'),(100.0,'btc-e%%%bter')]],
                  [284.91,'ltc-usd',[(184.91,'btc-e%%%okcoin'),(100.0,'btc-e%%%bter')]]]

    log_arbitrages_stats(arbitrages,logger)

    logger.close()
    
        
