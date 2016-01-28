from urllib.request import urlopen,Request
import re

#get http response
def getHttpResponse(url):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers={'User-Agent':user_agent,}
    request = Request(url,None,headers)
    return urlopen(request).read()

#get float list out of byte list
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

#get market depth (bids/asks lists)
def getMarketDepth(url,
                   regex_bid_ask,index_bid,index_ask,
                   regex_price_volume,index_price,index_volume):
    bBids,bAsks = re.match(regex_bid_ask,getHttpResponse(url)).group(index_bid,index_ask)
##    print('Bids (bytes):' + str(bBids) + '\n')
##    print('Asks (bytes):' + str(bAsks) + '\n')
    
    return (getFloatList(bBids,regex_price_volume,index_price,index_volume,0),
            getFloatList(bAsks,regex_price_volume,index_price,index_volume,1))

#Bitfinex
url = 'https://api.bitfinex.com/v1/book/btcusd'
regex_bid_ask = b'\{"bids":\[(.*)\],"asks":\[(.*)\]\}'
index_bid = 1
index_ask = 2
regex_price_volume = b'\{"price":"([\d\.]*)","amount":"([\d\.]*)","timestamp":"[\d\.]*"\}'
index_price = 0
index_volume = 1

###Bittrex
##url = 'https://bittrex.com/api/v1.1/public/getorderbook?market=BTC-LTC&type=both&depth=50'
##regex_bid_ask = b'\{".+":\{"buy":\[(.*)\],"sell":\[(.*)\]\}\}'
##index_bid = 1
##index_ask = 2
##regex_price_volume = b'\{"Quantity":([\d\.]*),"Rate":([\d\.]*)\}'
##index_price = 1
##index_volume = 0
##
###BTC-e
##url = 'https://btc-e.com/api/3/depth/btc_usd'
##regex_bid_ask = b'\{".+":\{"asks":\[(.*)\],"bids":\[(.*)\]\}\}'
##index_bid = 2
##index_ask = 1
##regex_price_volume = b'\[([\d\.]*),([\d\.]*)\]'
##index_price = 0
##index_volume = 1
##
###Bter
##url = 'http://data.bter.com/api/1/depth/btc_usd'
##regex_bid_ask = b'\\\n\{.*,"asks":\[(.*)\],"bids":\[(.*)\]\}'
##index_bid = 2
##index_ask = 1
##regex_price_volume = b'\[([\d\.]*),([\d\.]*)\]'
##index_price = 0
##index_volume = 1
##
###Coins-E
##url = 'https://www.coins-e.com/api/v2/market/WDC_BTC/depth/'
##regex_bid_ask = b'.*\{"bids": \[(.*)\], "asks": \[(.*)\]\},.*\}'
##index_bid = 1
##index_ask = 2
##regex_price_volume = b'\{"q": "([\d\.]*)", "cq": "[\d\.]*", "r": "([\d\.]*)", "n": \d+\}'
##index_price = 1
##index_volume = 0
##
###Crypto-trade
##url = 'https://crypto-trade.com/api/1/depth/btc_usd'
##regex_bid_ask = b'\{"asks":\[(.*)\],"bids":\[(.*)\]\}'
##index_bid = 2
##index_ask = 1
##regex_price_volume = b'\["([\d\.]*)","([\d\.]*)"\]'
##index_price = 0
##index_volume = 1
##
###Cryptsy
##url = 'http://pubapi.cryptsy.com/api.php?method=singleorderdata&marketid=2'
##regex_bid_ask = b'.*"sellorders":\[(.*)\],"buyorders":\[(.*)\]\}\}\}'
##index_bid = 2
##index_ask = 1
##regex_price_volume = b'\{"price":"([\d\.]*)","quantity":"([\d\.]*)","total":"[\d.]*"\}'
##index_price = 0
##index_volume = 1
##
###HitBTC
##url = 'https://api.hitbtc.com/api/1/public/BTCUSD/orderbook'
##regex_bid_ask = b'\{"asks":\[(.*)\],"bids":\[(.*)\]\}'
##index_bid = 2
##index_ask = 1
##regex_price_volume = b'\["([\d\.]*)","([\d\.]*)"\]'
##index_price = 0
##index_volume = 1
##
###Kraken
##url = 'https://api.kraken.com/0/public/Depth?pair=LTCUSD'
##regex_bid_ask = b'.*\{"asks":\[(.*)\],"bids":\[(.*)\]\}\}\}'
##index_bid = 2
##index_ask = 1
##regex_price_volume = b'\["([\d\.]*)","([\d\.]*)",[\d]*\]'
##index_price = 0
##index_volume = 1
##
###OKCoin
##url = 'https://www.okcoin.com/api/depth.do?symbol=btc_usd&ok=1'
##regex_bid_ask = b'\{"asks":\[(.*)\],"bids":\[(.*)\]\}'
##index_bid = 2
##index_ask = 1
##regex_price_volume = b'\[([\d\.]*),([\d\.]*)\]'
##index_price = 0
##index_volume = 1
##
###Polionex
##url = 'https://poloniex.com/public?command=returnOrderBook&currencyPair=XUSD_BTC&depth=50'
##regex_bid_ask = b'\{"asks":\[(.*)\],"bids":\[(.*)\],"isFrozen":.*\}'
##index_bid = 2
##index_ask = 1
##regex_price_volume = b'\["([\d\.]*)",([\d\.]*)\]'
##index_price = 0
##index_volume = 1
##
###Vircurex
##url = 'https://api.vircurex.com/api/orderbook.json?base=NMC&alt=BTC'
##regex_bid_ask = b'\{"asks":\[(.*)\],"bids":\[(.*)\],.*\}'
##index_bid = 2
##index_ask = 1
##regex_price_volume = b'\["([\d\.]*)","([\d\.]*)"\]'
##index_price = 0
##index_volume = 1

bids,asks = getMarketDepth(url,
                           regex_bid_ask,index_bid,index_ask,
                           regex_price_volume,index_price,index_volume)
print('Bids: ' + str(bids) + '\n')
print('Asks: ' + str(asks) + '\n')
print('---------------------------')
##while True:
##    bids,asks = getMarketDepth(url,
##                               regex_bid_ask,index_bid,index_ask,
##                               regex_price_volume,index_price,index_volume)
##    print('Bids: ' + str(bids) + '\n')
##    print('Asks: ' + str(asks) + '\n')
##    print('---------------------------')









