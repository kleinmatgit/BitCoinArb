import exchange_utils as u
import re

#describes market depth for an asset
class MarketDepth:

    bids = None
    asks = None
    updatedTime = None
    
    def __init__(self,url,regex_bid_ask,index_bid,index_ask,
                 regex_price_volume,index_price,index_volume):
        self.url = url
        self.regex_bid_ask = regex_bid_ask
        self.index_bid = index_bid
        self.index_ask = index_ask
        self.regex_price_volume = regex_price_volume
        self.index_price = index_price
        self.index_volume = index_volume

    def __eq__(self,other):
        if other:
            return (self.bids==other.bids and
                    self.asks==other.asks)
        else:
            return False
    
    def __repr__(self):
        return ('bids: ' + str(self.bids) + '\nasks: ' + str(self.asks))
    
    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result
    
    #query exchange website to get latest market depth
    def refresh(self):
        bBids,bAsks = re.match(self.regex_bid_ask,u.getHttpResponse(self.url)).group(self.index_bid,self.index_ask)
        self.bids,self.asks = (u.getFloatList(bBids,self.regex_price_volume,self.index_price,self.index_volume,0),
                               u.getFloatList(bAsks,self.regex_price_volume,self.index_price,self.index_volume,1))
    
    #get best bid/offer (with volume conditionaly)
    def getBestBidOffer(self,withVolume=False):
        if self.bids:
            best_bid = max(self.bids)[0]
            vol_bid = max(self.bids)[1]
        else:
            best_bid = None
            vol_bid = None
        if self.asks:
            best_ask = min(self.asks)[0]
            vol_ask = min(self.asks)[1]
        else:
            best_ask = None
            vol_ask = None
        if withVolume:
            return best_bid,best_ask,vol_bid,vol_ask
        else:
            return best_bid,best_ask

    #set last updated time
    def setUpdatedTime(self,dtime):
        self.updatedTime = dtime
        
#describes a CryptoCurrency Exchange class
class Exchange:

    pairs = None
    
    def __init__(self,name,
                 url_info,regex_info,
                 url_depth,regex_bid_ask,index_bid,index_ask,
                 regex_price_volume,index_price,index_volume,pairs=None):
        self.name = name
        self.url_info = url_info
        self.regex_info = regex_info
        self.url_depth = url_depth
        self.regex_bid_ask = regex_bid_ask
        self.index_bid = index_bid
        self.index_ask = index_ask
        self.regex_price_volume = regex_price_volume
        self.index_price = index_price
        self.index_volume = index_volume

        #in some cases, list of pairs is hardcoded in the conf
        #then directly passed to the construtctor
        if pairs:
            self.pairs = {}
            for pair in pairs:
                self.pairs.update({pair:[]})
    
    def __repr__(self):
        str_main = ('ExchangeName: ' + self.name + '\n' +
                    'MarketInfo:\n' +
                    '\tURL: ' + self.url_info + '\n' +
                    '\tRegex: ' + self.regex_info.decode() + '\n' +
                    'MarketDepth:\n' +
                    '\tURL: ' + self.url_depth + '\n'
                    '\tRegex(bid/ask): ' + self.regex_bid_ask.decode() + '\n' +
                    '\tIndex(bid/ask): ' + str(self.index_bid) + '/' + str(self.index_ask) + '\n' +
                    '\tRegex(price/volume): ' + self.regex_price_volume.decode() + '\n' +
                    '\tIndex(price/volume): ' + str(self.index_price) + '/' + str(self.index_volume)
                    )
        if self.pairs:
            return (str_main + '\n' +
                    'Pairs: ' + str(self.pairs))
        else:
            return str_main
    
    #init dic of pairs from url/regex of exchange market info
    def initPairs(self,assets):
        try:
            if self.pairs:
                for pair in self.pairs:
                    #construct marketDepth for this pair
                    marketDepth = MarketDepth(u.getPairUrl(pair,self.url_depth),
                                              self.regex_bid_ask,self.index_bid,self.index_ask,
                                              self.regex_price_volume,self.index_price,self.index_volume)
                    self.pairs.update({pair:marketDepth})

            else:
                l = re.findall(self.regex_info,u.getHttpResponse(self.url_info))
                self.pairs = {}
                for i in l:
                    #case where pair has no separation (ie: 'BTCUSD')
                    if type(i) is bytes:
                        pair = u.deducePair(i.decode().lower(),assets)
                    #case where pair has separation (ie: 'BTC-USD' or 'BTC_USD' or 'BTC/USD')
                    if type(i) is tuple:
                        pair = (i[0].decode() + '-' + i[1].decode()).lower()

                    #construct marketDepth for this pair
                    marketDepth = MarketDepth(u.getPairUrl(pair,self.url_depth),
                                      self.regex_bid_ask,self.index_bid,self.index_ask,
                                      self.regex_price_volume,self.index_price,self.index_volume)
                    self.pairs.update({pair:marketDepth})

            return 0,''

        except Exception as e:
            return -1,str(e)
    
    #refresh market depth for given asset
    def refreshMarketDepth(self,pair):
        if pair in self.pairs:
            self.pairs.get(pair).refresh()    
        else:
            raise Exception(pair + ' not found in ' + self.name + ' exchange pairs list')

    #get best price for that pair/list of bids or asks
    def getBestPrice(self,pair,order):
        if order==0:
            prices = self.bids
        else:
            prices = self.asks
        
    #get best bid/offer for that pair
    def getBestBidOffer(self,pair,withVolume=False):
        if pair in self.pairs:
            return(self.pairs.get(pair).getBestBidOffer(withVolume))
        else:
            raise Exception(pair + ' not found in ' + self.name + ' exchange pairs list')

    #get last updated time for that pair
    def getUpdatedTime(self,pair):
        if pair in self.pairs:
            return(self.pairs.get(pair).updatedTime)
        else:
            raise Exception(pair + ' not found in ' + self.name + ' exchange pairs list')

    #return market depth object for this pair
    def getMarketDepth(self,pair):
        if pair in self.pairs:
            return(self.pairs.get(pair))
        else:
            raise Exception(pair + ' not found in ' + self.name + ' exchange pairs list')

    #return info about a pair as a string
    def getInfo(self,pair):
        bid,ask,vol_bid,vol_ask = self.getBestBidOffer(pair,withVolume=True)
        updated_time = self.getUpdatedTime(pair)
        return str(vol_bid) + ' | ' + str(bid) + ' : ' + str(ask) + ' | ' + str(vol_ask) + ' - ' + str(updated_time)

    #buy/sell a volume of a certain pair
    #the operation is assume at best price (ie: will hit lowest offer (for a BUY) or highest bid (for a SELL)
    #if volume is superior to best price volume, then will hit next best price etc until the volume is fill
    #exchange market depth will be updated accordingly
    #this method will be essentially usefull when simulating arbitrage
    def executeMarketOrder(self,order,pair,volume):

        #BUY
        if order==0:
            prices = self.getMarketDepth(pair).asks
        #SELL
        else:
            prices = self.getMarketDepth(pair).bids
        
        while volume>0.0 and len(prices)>0:
            best_price,best_volume = prices[0]
            if best_price==None:
                volume = 0.0
                break
            if best_volume>volume:
                prices[0] = best_price,best_volume - volume
                break
            elif best_volume<=volume:
                prices.pop(0)
                volume -= best_volume
            
                
            

        
