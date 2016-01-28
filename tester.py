try:
    import exchange_utils as u
    from exchange import Exchange
    from logger_handler import loggerHandler
    from worker import PriceListenerWorker
except ImportError:
    pass

import threading
import time

#test
if __name__=="__main__":

    logger = loggerHandler('test',log_path='log/')
    lock = threading.Lock()
    
    #getHttpResponse
    print('test getHttpResponse: ')
    print(u.getHttpResponse('https://btc-e.com/api/3/depth/btc_usd'))
    print('--------------------------------------')
    
    #getExchangesFromXml
    print('test getExchangesFromXml: ')
    exchanges = u.getExchangesFromXml('exchanges.xml')
    expected_len = 6
    for exchange in exchanges:
        print(exchange)
    if len(exchanges)!=expected_len:
        raise Exception('Expected # exchanges is ' + str(expected_len) +
                        ', only ' + str(len(exchanges)) + ' in the list')
    print('--------------------------------------')
    
    #getAssetsFromXml
    print('test getAssetsFromXml: ')
    assets = u.getAssetsFromXml('assets.xml')
    print('#assets: ' + str(len(assets)))
    print('--------------------------------------')

    #getPairsFilterFromXml
    print('test getPairsFilterFromXml: ')
    pairs = u.getPairsFilterFromXml('pairs_filter.xml')
    print('#pairs: ' + str(len(pairs)))
    print('--------------------------------------')

    #deducePair
    print('test deducePair: ')
    print(u.deducePair('BTCUSD',assets))
    print('--------------------------------------')
    
    #getPairUrl
    print('test getPairUrl: ')
    print(u.getPairUrl('btc-usd','https://btc-e.com/api/3/depth/%asset1%_%asset2%'))
    print(u.getPairUrl('btc-uro','https://poloniex.com/public?command=returnOrderBook&amp;currencyPair=%ASSET1%_%ASSET2%&amp;depth=50'))
    print('--------------------------------------')
    
    #init all exchanges
    print('initExchangesConcurrency: ')
    u.initExchangesConcurrency(exchanges,assets,logger)
    print('--------------------------------------')

    #getAssetsFromPair
    print('getAssetsFromPair: ')
    print(u.getAssetsFromPair('btc-usd'))
    print(u.getAssetsFromPair('btc-_nexus'))
    print(u.getAssetsFromPair('atomic-btc'))
    print('--------------------------------------')
    
##    #Exchange - init
##    print('test Exchange: ')
##    exch = u.getExchange(exchanges,'hitbtc')
##    print(exch)
##    istatus,err = exch.initPairs(assets)
##    if istatus==0:
##        print('initPairs ok')
##    else:
##        print('initPairs failed: ')
##        print(err)
##    print('--------------------------------------')

##    #getAllAssetsFromExchanges
##    print('test getAllAssetsFromExchanges: ')
##    print(u.getAllAssetsFromExchanges(exchanges))
##    print('--------------------------------------')
    
    #Exchange - bid offer
    print('test Exchange - getBestBidOffer: ')
    exch = u.getExchange(exchanges,'okcoin')
    pair = 'btc-usd'
    exch.refreshMarketDepth(pair)
    print(exch.getBestBidOffer(pair))
    print(exch.getBestBidOffer(pair,withVolume=True))
    print('--------------------------------------')

    #Exchange - getInfo
    print('test Exchange - getInfo: ')
    print(exch.getInfo(pair))
    print('--------------------------------------')

    #Exchange - executeMarketOrder
    print('test Exchange - executeMarketOrder: ')
    exch = u.getExchange(exchanges,'btc-e')
    pair = 'btc-usd'
    exch.refreshMarketDepth(pair)
    order = 0
    prices = exch.getMarketDepth(pair).asks
    volume = 5.01
    rows = 10
    print('before order: \n' + str(prices[:rows]))
    print(exch.executeMarketOrder(order,pair,volume))
    print('after order: \n' + str(prices[:rows]))
    print('--------------------------------------')
    
    #getMostQuotedPairs
    print('test getMostQuotedPairs: ')
    most_quoted_pairs = u.getMostQuotedPairs(exchanges,logger)
    print('--------------------------------------')
    
    #test copy of exchanges
    print('test copy of exchanges: ')
    exchanges_copy = exchanges.copy()
    exchanges_copy.pop(0)    
    print('len(exchanges):' + str(len(exchanges)))
    print('len(exchanges_copy):' + str(len(exchanges_copy)))
    print('--------------------------------------')   
    
##    #PriceListenerWorker
##    print('test PriceListenerWorker: ')
##    w = PriceListenerWorker(0,'thread0',exch,pair,lock,logger)
##    w.start()
##    while True:
##        pass

    
    
    
    
