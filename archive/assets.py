from urllib.request import urlopen,Request
import re

#get http response
def getHttpResponse(url):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers={'User-Agent':user_agent,}
    request = Request(url,None,headers)
    return urlopen(request).read()

#get assets list
def getAssets(url,regex):
    l = re.findall(regex,getHttpResponse(url))
    assets = []
    for i in l:
        #case where asset has no separation (ie: 'BTCUSD')
        if type(i) is bytes:
            assets.append((i.decode().lower()))
        #case where asset has separation (ie: 'BTC-USD' or 'BTC_USD' or 'BTC/USD')
        if type(i) is tuple:
            assets.append((i[0].decode() + '-' + i[1].decode()).lower())
        
    return assets

exchanges = []

#Bitfinex
exchanges.append(
    ('Bitfinex',
     'https://api.bitfinex.com/v1/symbols',
     b'\"(\w+)"',
     6))

###Bittrex
##exchanges.append(
##    ('Bittrex',
##     'https://bittrex.com/api/v1.1/public/getmarkets',
##     b'"MarketCurrency":"(\w+)","BaseCurrency":"(\w+)",',
##     214))
##
###BTC-e
##exchanges.append(
##    ('BTC-e',
##     'https://btc-e.com/api/3/info',
##     b'"(\w+)_(\w+)":\{"decimal_places":',
##     25))
##
###Bter
##exchanges.append(
##    ('Bter',
##     'https://data.bter.com/api/1/marketinfo',
##     b'"(\w+)_(\w+)":\{"decimal_places":',
##     149))
##
###Coins-E
##exchanges.append(
##    ('Coins-E',
##     'https://www.coins-e.com/api/v2/markets/data/',
##     b'"(\w+)_(\w+)": *\{"status":',
##     123))
##
###Crypto-Trade
##exchanges.append(
##    ('Crypto-Trade',
##     'https://crypto-trade.com/api/1/getpairs',
##     b'"(\w+)_(\w+)":\{"min_amount":',
##     59))
##
###Cryptsy
##exchanges.append(
##    ('Cryptsy',
##     'http://pubapi.cryptsy.com/api.php?method=marketdatav2',
##     b'"(\w+)\\\/(\w+)":\{"marketid":',
##     406))
##
###HitBTC
##exchanges.append(
##    ('HitBTC',
##     'https://api.hitbtc.com/api/1/public/symbols',
##     b'"symbol":"(\w+)"',
##     15))

###Kraken
##exchanges.append(
##    ('Kraken',
##     'https://api.kraken.com/0/public/AssetPairs',
##     b'"altname":"(\w+)",',
##     12))

###Poloniex
##exchanges.append(
##    ('Poloniex',
##     'https://poloniex.com/public?command=returnTicker',
##     b'"(\w+)_(\w+)":\{"last":',
##     140))



for exch in exchanges:
    assets = getAssets(exch[1],exch[2])
    print(exch[0] + ' Assets: ' + str(assets))
    if len(assets)==exch[3]:
        print('Exchange ' + exch[0] + ' OK\n')
    else:
        print('Exchange ' + exch[0] + ' NOT OK (actual len:' + str(len(assets)) +
              ', expected len:' + str(exch[3]) + ')\n')









