from lxml import etree
from urllib.request import urlopen,Request
import re
try:
    from exchange import Exchange
    from worker import InitExchangeWorker, PriceListenerWorker
    from logger_handler import loggerHandler
    import threading
except ImportError:
    pass

#get http response
def getHttpResponse(url):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers={'User-Agent':user_agent,}
    request = Request(url,None,headers)
    return urlopen(request).read()

#get float list out of byte list based on regex
def getFloatList(bList,regex,index_price,index_volume,index_order):
    l = re.findall(regex,bList)
    fList = []
    for i in l:
        fPrice = float(i[index_price])
        fVolume = float(i[index_volume])
        fList.append((fPrice,fVolume))

    #desc order for bids
    if index_order==0:
        fList.sort(reverse=True)
    #asc order for asks
    else:
        fList.sort()
    return fList

#function returns a list of exchanges instanciated from xml file
def getExchangesFromXml(path):
    exchanges = []
    tree = etree.parse(path)
    root = tree.getroot()
    new_exchange = False
    pairs = []
    hasPair = False
    
    for element in root.iter('*'):

        if element.tag=='Exchange':
            #now we are done with previous exchange
            #we can instanciate the class and add it to the list
            if new_exchange:
                if hasPair:
                    exchanges.append(Exchange(name,
                                              url_info,regex_info,
                                              url_depth,regex_bid_ask,index_bid,index_ask,
                                              regex_price_volume,index_price,index_volume,pairs))
                else:
                    exchanges.append(Exchange(name,
                                              url_info,regex_info,
                                              url_depth,regex_bid_ask,index_bid,index_ask,
                                              regex_price_volume,index_price,index_volume))
                pairs = []
                hasPair = False
            
            new_exchange = True
            name = element.attrib.get('name')

        if element.tag=='MarketInfo':
            url_info = element.attrib.get('url')

        if element.tag=='RegexInfo':
            regex_info = str.encode(element.attrib.get('value'))

        if element.tag=='MarketDepth':
            url_depth = element.attrib.get('url')

        if element.tag=='Regex':

            regex_name = element.attrib.get('name')

            if regex_name=='BidAsk':
                index_bid = int(element.attrib.get('index_bid'))
                index_ask = int(element.attrib.get('index_ask'))
                regex_bid_ask = str.encode(element.attrib.get('value'))

            elif regex_name=='PriceVolume':
                index_price = int(element.attrib.get('index_price'))
                index_volume = int(element.attrib.get('index_volume'))
                regex_price_volume = str.encode(element.attrib.get('value'))

        if element.tag=='Pair':
            hasPair = True
            pairs.append(element.attrib.get('name'))
    
    #handle exchange created in the last loop
    if new_exchange:
        if hasPair:
            exchanges.append(Exchange(name,
                                      url_info,regex_info,
                                      url_depth,regex_bid_ask,index_bid,index_ask,
                                      regex_price_volume,index_price,index_volume,pairs))
        else:
            exchanges.append(Exchange(name,
                                      url_info,regex_info,
                                      url_depth,regex_bid_ask,index_bid,index_ask,
                                      regex_price_volume,index_price,index_volume))
    
    return exchanges

#function returns a list of exchanges instanciated from xml file
def getAssetsFromXml(path):
    assets = []
    tree = etree.parse(path)
    root = tree.getroot()

    for element in root.iter('*'):

        if element.tag=='Asset':
            name = element.attrib.get('name')
            assets.append(name.lower())

    return assets

#function returns a list of pairs which can be used as a filter
def getPairsFilterFromXml(path):
    pairs = []
    tree = etree.parse(path)
    root = tree.getroot()

    for element in root.iter('*'):

        if element.tag=='Pair':
            name = element.attrib.get('name')
            pairs.append(name.lower())

    return pairs

#get pair url from template url
def getPairUrl(pair,url_base):
    if '-' not in pair:
        raise Exception("pair format error, '-' is missing: " + pair)
    idash = pair.index('-')
    asset1 = pair[:idash]
    asset2 = pair[idash+1:]
    if '%asset1%' in url_base:
        url_base = url_base.replace('%asset1%',asset1.lower())
    if '%asset2%' in url_base:
        url_base = url_base.replace('%asset2%',asset2.lower())
    if '%ASSET1%' in url_base:
        url_base = url_base.replace('%ASSET1%',asset1.upper())
    if '%ASSET2%' in url_base:
        url_base = url_base.replace('%ASSET2%',asset2.upper())
    return url_base
    
#return exchange object from exchanges list
def getExchange(exchanges,name):
    for exchange in exchanges:
        if exchange.name.lower()==name.lower():
            return exchange
    return None

#deduce pair and return it with format %asset1%-%asset2%
def deducePair(pair,assets):
    for i in range(1,len(pair)-1):
        if pair[:i].lower() in assets and pair[i:].lower() in assets:
            return pair[:i].lower() + '-' + pair[i:].lower()
    raise Exception('pair not recognized: ' + pair.lower())

#get all asssets from exchanges list
#usefull to setup 'assets' xml generator function by copying result of this function..
def getAllAssetsFromExchanges(exchanges):
    assets = []
    for exchange in exchanges:
        for pair in exchange.pairs:
            idash = pair.index('-')
            asset1 = pair[:idash]
            asset2 = pair[idash+1:]
            if asset1 not in assets:
                assets.append(asset1)
            if asset2 not in assets:
                assets.append(asset2)
    assets.sort()
    return assets

#init exchanges with multi-threading
def initExchangesConcurrency(exchanges,assets,logger):
    logger.info('starting to init exchanges in concurent mode')
    threads_init = []
    i = 0
    for exchange in exchanges:
        t = InitExchangeWorker(i,'thread-'+str(i),exchange,assets,logger)
        threads_init.append(t)
        i += 1
    [x.start() for x in threads_init]
    [x.join() for x in threads_init]

#get asset1,asset2 from pair
def getAssetsFromPair(pair):
    idash = pair.index('-')
    return pair[:idash],pair[idash+1:]

#get list of (pair,[exchanges])
#for exchanges which quote the pair
#order by most quoted pair
def getMostQuotedPairs(exchanges,logger):
    dicPairs = {}
    for exchange in exchanges:
        for pair in exchange.pairs:
            asset1,asset2 = getAssetsFromPair(pair) 
            pair_reverse = asset2 + '-' + asset1
            if pair not in dicPairs and pair_reverse not in dicPairs:
                dicPairs.update({pair:[exchange.name]})
            else:
                if pair in dicPairs:
                    exch_list = dicPairs.get(pair)
                    exch_list.append(exchange.name)
                    dicPairs.update({pair:exch_list})
                if pair_reverse in dicPairs:
                    exch_list = dicPairs.get(pair_reverse)
                    exch_list.append(exchange.name)
                    dicPairs.update({pair_reverse:exch_list})
    pairs = []
    for pair in dicPairs:
        exch_list = dicPairs.get(pair)
        if len(exch_list)>1:
            pairs.append((len(exch_list),pair,exch_list))
    
    pairs.sort(reverse=True)
    return pairs

#delete pair we don't listen to according to filter
def deletePairsUnlistened(exchanges,pairs_filter):
    for exchange in exchanges:
        #logger.info('exchange: ' + exchange)
        l = list(exchange.pairs.keys())
        for pair in l:
            asset1,asset2 = getAssetsFromPair(pair)
            pair_reverse = asset2 + '-' + asset1
            if pair not in pairs_filter and pair_reverse not in pairs_filter:
                exchange.pairs.pop(pair)
    
#launch exchange listeners
def launchExchangeListenersWithPairsFilter(exchanges,pairs_filter,logger):
    logger.info('starting to launch exchange listeners - pairs filter mode')
    i=0
    threads_listen = []
    for exchange in exchanges:
        for pair in exchange.pairs:
            if pair in pairs_filter:
                t = PriceListenerWorker(i,'thread-'+str(i),exchange,pair,logger)
                threads_listen.append(t)
                i += 1
    [x.start() for x in threads_listen]
    return threads_listen

#log info for all exchanges
def logInfoExchanges(exchanges,logger):
    s = '\n#################################################'
    s += '\n#################################################'
    for exchange in exchanges:
        s += getExchangeInfo(exchange)
    logger.info(s,bPrint=True)

#log info about an exchange
def logInfo(exchange,logger):
    logger.info(getExchangeInfo(exchange),bPrint=True)

#return info about an exchange as a string
def getExchangeInfo(exchange):
    str_output = '\nExchange ' + exchange.name + ' info:'
    for pair in exchange.pairs:
        str_output += '\n' + pair + ':\t' + exchange.getInfo(pair)
    str_output += '\n--------------------'
    return str_output

def stopThreads(threads):
    for t in threads:
        t.stop()
    for t in threads:
        t.join()
