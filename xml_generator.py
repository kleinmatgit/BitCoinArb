from lxml import etree
from exchange import Exchange

def generate_exchanges_xml():

    exchanges = []

    exchanges.append(Exchange('Bitfinex',
                              'https://api.bitfinex.com/v1/symbols',
                              b'\"(\w+)"',
                              'https://api.bitfinex.com/v1/book/%asset1%%asset2%',
                              b'\{"bids":\[(.*)\],"asks":\[(.*)\]\}',1,2,
                              b'\{"price":"([\d\.]*)","amount":"([\d\.]*)","timestamp":"[\d\.]*"\}',0,1))

    exchanges.append(Exchange('Bittrex',
                              'https://bittrex.com/api/v1.1/public/getmarkets',
                              b'"MarketCurrency":"(\w+)","BaseCurrency":"(\w+)",',
                              'https://bittrex.com/api/v1.1/public/getorderbook?market=%asset2%-%asset1%&type=both&depth=50',
                              b'\{".+":\{"buy":\[(.*)\],"sell":\[(.*)\]\}\}',1,2,
                              b'\{"Quantity":([\d\.]*),"Rate":([\d\.]*)\}',1,0))

    exchanges.append(Exchange('BTC-e',
                              'https://btc-e.com/api/3/info',
                              b'"(\w+)_(\w+)":\{"decimal_places":',
                              'https://btc-e.com/api/3/depth/%asset1%_%asset2%',
                              b'\{".+":\{"asks":\[(.*)\],"bids":\[(.*)\]\}\}',2,1,
                              b'\[([\d\.]*),([\d\.]*)\]',0,1))

    exchanges.append(Exchange('Bter',
                              'https://data.bter.com/api/1/marketinfo',
                              b'"(\w+)_(\w+)":\{"decimal_places":',
                              'http://data.bter.com/api/1/depth/%asset1%_%asset2%',
                              b'\\\n\{.*,"asks":\[(.*)\],"bids":\[(.*)\]\}',2,1,
                              b'\[([\d\.]*),([\d\.]*)\]',0,1))

    exchanges.append(Exchange('Coins-E',
                              'https://www.coins-e.com/api/v2/markets/data/',
                              b'"(\w+)_(\w+)": *\{"status":',
                              'https://www.coins-e.com/api/v2/market/%asset1%_%asset2%/depth/',
                              b'.*\{"bids": \[(.*)\], "asks": \[(.*)\]\},.*\}',1,2,
                              b'\{"q": "([\d\.]*)", "cq": "[\d\.]*", "r": "([\d\.]*)", "n": \d+\}',1,0))

    exchanges.append(Exchange('Crypto-Trade',
                              'https://crypto-trade.com/api/1/getpairs',
                              b'"(\w+)_(\w+)":\{"min_amount":',
                              'https://crypto-trade.com/api/1/depth/%asset1%_%asset2%',
                              b'\{"asks":\[(.*)\],"bids":\[(.*)\]\}',2,1,
                              b'\["([\d\.]*)","([\d\.]*)"\]',0,1))

    exchanges.append(Exchange('HitBTC',
                              'https://api.hitbtc.com/api/1/public/symbols',
                              b'"symbol":"(\w+)"',
                              'https://api.hitbtc.com/api/1/public/%ASSET1%%ASSET2%/orderbook',
                              b'\{"asks":\[(.*)\],"bids":\[(.*)\]\}',2,1,
                              b'\["([\d\.]*)","([\d\.]*)"\]',0,1))

    exchanges.append(Exchange('Kraken',
                              'https://api.kraken.com/0/public/AssetPairs',
                              b'"altname":"(\w+)",',
                              'https://api.kraken.com/0/public/Depth?pair=%asset1%%asset2%',
                              b'.*\{"asks":\[(.*)\],"bids":\[(.*)\]\}\}\}',2,1,
                              b'\["([\d\.]*)","([\d\.]*)",[\d]*\]',0,1))

    exchanges.append(Exchange('OKCoin',
                              'n/a',
                              'n/a',
                              'https://www.okcoin.com/api/depth.do?symbol=%asset1%_%asset2%&ok=1',
                              b'\{"asks":\[(.*)\],"bids":\[(.*)\]\}',2,1,
                              b'\[([\d\.]*),([\d\.]*)\]',0,1,
                              ['btc-usd','ltc-usd']))

    exchanges.append(Exchange('Poloniex',
                              'https://poloniex.com/public?command=returnTicker',
                              b'"(\w+)_(\w+)":\{"last":',
                              'https://poloniex.com/public?command=returnOrderBook&currencyPair=%ASSET1%_%ASSET2%&depth=50',
                              b'\{"asks":\[(.*)\],"bids":\[(.*)\],"isFrozen":.*\}',2,1,
                              b'\["([\d\.]*)",([\d\.]*)\]',0,1))

    root = etree.Element('Exchanges')

    for exchange in exchanges:
        node = etree.SubElement(root,'Exchange',name=exchange.name)
        info = etree.SubElement(node,'MarketInfo',url=exchange.url_info)
        regex_info = etree.SubElement(info,'RegexInfo',value=exchange.regex_info)
        depth = etree.SubElement(node,'MarketDepth',url=exchange.url_depth)
        regex_bid_ask = etree.SubElement(depth,'Regex',
                                         name='BidAsk',
                                         value=exchange.regex_bid_ask,
                                         index_bid=str(exchange.index_bid),
                                         index_ask=str(exchange.index_ask))
        regex_price_volume = etree.SubElement(depth,'Regex',
                                              name='PriceVolume',
                                              value=exchange.regex_price_volume,
                                              index_price=str(exchange.index_price),
                                              index_volume=str(exchange.index_volume))
        if exchange.pairs:
            pairs = etree.SubElement(node,'Pairs')
            for pair in exchange.pairs:
                pair = etree.SubElement(pairs,'Pair',name=pair)
    
    str_xml = etree.tostring(root,pretty_print=True)
    outFile = open('exchanges.xml','w')
    outFile.write(str_xml.decode())
    outFile.close()


def generate_assets_xml():

    assets = ['1cr', '888', '_nexus', '_smbr',
              'aaa', 'aby', 'ac', 'ach', 'acoin', 'adn', 'aeon', 'aero', 'alp', 'amc', 'anc', 'apex', 'ar', 'arch', 'arg', 'atomic', 'aur', 'axr',
              'bbr', 'bc', 'bch', 'bcn', 'bela', 'bet', 'big', 'bitcny', 'bits', 'bitusd', 'biz', 'blc', 'blkt', 'blu', 'bncr', 'boom', 'bqc', 'brit', 'bsty', 'bsy', 'btb', 'btc', 'btcd', 'btg', 'bti', 'btm', 'btq', 'btsx', 'buk', 'burn', 'burst',
              'c2', 'cann', 'capt', 'carbon', 'cash', 'ccn', 'cdc', 'cent', 'cfc2', 'cga', 'cgb', 'cha', 'chcc', 'cin', 'cinni', 'ckc', 'clam', 'cloak', 'clr', 'cmc', 'cnc', 'cnh', 'cnmt', 'cnote', 'cny', 'coco', 'coin', 'col', 'comm', 'crack', 'craig', 'crc', 'crypt', 'csc', 'cure', 'cyc', 'czc',
              'dcn', 'dem', 'dgb', 'dgc', 'dice', 'diem', 'dime', 'dmd', 'dns', 'doge', 'dolp', 'dope', 'drk', 'drkc', 'dsh', 'dt', 'dtc', 'dvc',
              'ebt', 'efl', 'elc', 'elp', 'elt', 'emc2', 'emd', 'enrg', 'envy', 'eqx', 'esc', 'etc', 'ethan', 'eur', 'exc', 'excl', 'exe', 'ezc',
              'fc2', 'fcn', 'fibre', 'fire', 'flex', 'flo', 'flt', 'food', 'fox', 'frac', 'frc', 'frk', 'frsh', 'ftc', 'fz',
              'gaia', 'gb', 'gbp', 'gdc', 'gdn', 'ghc', 'ghost', 'give', 'glc', 'glx', 'glyph', 'gml', 'gns', 'gold', 'gpc', 'grc', 'grs', 'gue',
              'hal', 'hiro', 'huc', 'hyc', 'hyp', 'hyper',
              'icb', 'icg', 'ifc', 'int', 'ioc', 'ipc', 'iso', 'isr',
              'j', 'jbs', 'jlh', 'jpc', 'judge',
              'karm', 'kdc', 'key', 'kgc', 'kore', 'ktk',
              'lab', 'lbw', 'lknx', 'lmr', 'lol', 'lsd', 'ltbc', 'ltc', 'ltcd', 'lts', 'lxc',
              'm', 'maid', 'mamm', 'mars', 'maryj', 'max', 'mcn', 'mec', 'mgw', 'mid', 'mil', 'min', 'mint', 'mls', 'mmc', 'mmxiv', 'mne', 'mns1', 'mnta', 'mon', 'mona', 'mrkt', 'mrs', 'msc', 'muga', 'mwc', 'myr',
              'nan', 'nas', 'naut', 'nav', 'nbc', 'nbe', 'nbt', 'nec', 'neos', 'net', 'nfd', 'nhz', 'nib', 'nlg', 'nmb', 'nmc', 'nobl', 'node', 'note', 'nrb', 'nrs', 'nsr', 'ntr', 'ntx', 'nuc', 'nud', 'nvc', 'nxt', 'nxti', 'nxtty',
              'oc', 'opal', 'orb',
              'pc', 'pes', 'piggy', 'pink', 'pmc', 'pnd', 'pot', 'ppc', 'prc', 'pro', 'prt', 'pseud', 'ptc', 'pts', 'pwc', 'pxc', 'pxi', 'pyra',
              'qbk', 'qcn', 'qora', 'qrk', 'qtl', 'qtm2', 'quid',
              'raw', 'rbt', 'rby', 'rch', 'rdd', 'rec', 'red', 'ric', 'ripo', 'roc', 'rods', 'root', 'ros', 'rox', 'ru', 'ruble', 'rur', 'rzr',
              'sbc', 'sc', 'scot', 'sdc', 'seed', 'sfr', 'shade', 'shibe', 'shopx', 'silk', 'sjcx', 'slg', 'slm', 'slr', 'sole', 'spark', 'src', 'srcc', 'ssd', 'ssv', 'start', 'str', 'stv', 'super', 'svr', 'swarm', 'swift', 'sync', 'sys',
              'tac', 'tag', 'tech', 'thc', 'tips', 'tit', 'tix', 'token', 'tor', 'trc', 'trdr', 'tri', 'trk', 'trust',
              'ultc', 'unat', 'unity', 'uno', 'upm', 'uro', 'usd', 'utc', 'util',
              'vault', 'vdo', 'via', 'vik', 'vlty', 'voot', 'vrc', 'vtc',
              'water', 'wc', 'wdc', 'wise', 'wkc', 'wolf', 'wstl', 'wsx', 'wwc',
              'xap', 'xbc', 'xbm', 'xbt', 'xbot', 'xc', 'xcash', 'xch', 'xcld', 'xcn', 'xcp', 'xcr', 'xdg', 'xdn', 'xdp', 'xdq', 'xg', 'xmr', 'xnc', 'xpm', 'xrp', 'xsi', 'xst', 'xtc', 'xuro', 'xusd', 'xvn', 'xxc', 'xxx',
              'yac', 'yacc',
              'zcc', 'zet']

    root = etree.Element('Assets')

    for asset in assets:
        node = etree.SubElement(root,'Asset',name=asset)
        
    str_xml = etree.tostring(root,pretty_print=True)
    outFile = open('assets.xml','w')
    outFile.write(str_xml.decode())
    outFile.close()

if __name__=="__main__":

    generate_exchanges_xml()
    #generate_assets_xml()
    
