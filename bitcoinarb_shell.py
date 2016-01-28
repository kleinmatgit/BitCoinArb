from worker import InitExchangeWorker,PriceListenerWorker
import exchange_utils as u
from exchange import Exchange
from logger_handler import loggerHandler
import arbitrage as arb
import threading
import time
import sys

appname = 'BitCoinArbShell'

#test if an exchange name exists in list of exchanges
def ExchangeExists(exchange_name,exchanges):
    for exchange in exchanges:
        if exchange.name.lower() == exchange_name.lower():
            return True
    return False

if __name__=="__main__":

    threads = []
    time_start = time.time()
    exchanges = u.getExchangesFromXml('exchanges.xml')
    assets = u.getAssetsFromXml('assets.xml')
    pairs_filter = u.getPairsFilterFromXml('pairs_filter.xml')
    logger = loggerHandler('exchange_listener',log_path='log/')
    loggerExchangeInfo = loggerHandler('exchange_info',log_path='log/')
    loggerArbitrage = loggerHandler('exchange_arbitrage',log_path='log/')

    #init exchanges
    u.initExchangesConcurrency(exchanges,assets,logger)
    
    #delete pair we are not listening
    u.deletePairsUnlistened(exchanges,pairs_filter)
    
    #listen to exchanges
    threads = u.launchExchangeListenersWithPairsFilter(exchanges,pairs_filter,logger)
    time.sleep(3)

    print('Launching shell....')
    print('****************************************************************')
    print('****  key in \'cmdlist\' to get list of available commands *****')
    print('****************************************************************')
    
    #shell loop
    while True:
        try:
            s = input('MyShell-------->>>>')
            l = s.lower().split()
            
            #quit the shell
            if l[0]=='quit' and len(l[0])==len('quit'):

                #stop all threads before quitting!!!
                u.stopThreads(threads)
                str_time = str(time.time() - time_start)
                logger.info(appname + ' finished in ' + str_time[:str_time.index('.')+3] + ' secs..',bPrint=False)
                logger.info('-----------------------------------------------------------',bPrint=False)
                logger.close()
                sys.exit()

            #display list of commands available
            elif l[0]=='cmdlist' and len(l[0])==len('cmdlist'):
                if len(l) > 1:
                    print('cmdlist command don\'t take any argument')
                else:
                    print('Commands available:')
                    print('cmdlist - display list of command available')
                    print('exchanges - display list of exchanges available')
                    print('getbo - display list bid/offer for a given exchange/assetpair')
                    print('loginfo - display and log information about a given exchange (volume, b/o, last updated time for each asset pair)')
                    print('logarb - display and log information about current arbitrage opportunities')
                    print('quit - stop listeners and exit shell')
                    
            #display list of exchanges we are listening to
            elif l[0]=='exchanges':
                if len(l) > 1:
                    print('exchanges command don\'t take any argument')
                else:
                    print('List of exchanges we are listening to:')
                    for exchange in exchanges:
                        print(exchange.name)
            
            #display best bid/offer for given exchange/assetpair
            #for instance: 'getbo okcoin btc-usd'
            #if call with only exchange in argument, will display b/o for all assetpair for the given exchange
            elif l[0]=='getbo':
                if len(l)==2:
                    if not ExchangeExists(l[1],exchanges):
                        print('exchange not recognized: ' + l[1])
                    else:
                        exch = u.getExchange(exchanges,l[1])
                        print('best bid/offer for ' + exch.name + ' exchange:')
                        [print(pair + ': ' + str(exch.getBestBidOffer(pair))
                               + ' (' + str(exch.getUpdatedTime(pair)) + ')') for pair in exch.pairs]
                        print('#pairs: ' + str(len(exch.pairs)))
                elif len(l)==3:
                    print(u.getExchange(exchanges,l[1]).getBestBidOffer(l[2].lower()))
                else:
                    print('getbo correct usage: getbo %exchange_name% [%assetpair%]')

            #display and log informations about exchange given in argument:
            #volume, bid, offer, last updated time
            #will be logged into 'exchange_info_yyyy-mm-dd.log' file
            #if used without argument, will log info for all exchanges
            elif l[0]=='loginfo':
                if len(l)==1:
                    u.logInfoExchanges(exchanges,loggerExchangeInfo)
                elif len(l)==2:
                    exch = u.getExchange(exchanges,l[1])
                    u.logInfo(exch,loggerExchangeInfo)
                else:
                    print('loginfo correct usage: loginfo [%exchange_name%]')
            
            #display and log informations about current arbitrage opportunities if any
            #will be logged into 'exchange_arbitrage_yyyy-mm-dddd.log' file
            #can be called with 'details' as argument -> verbose mode
            elif l[0]=='logarb':
                if len(l)==1:
                    arb.log_arbitrage(exchanges,pairs_filter,loggerArbitrage)
                elif l[1]=='details':
                    arb.log_arbitrage(exchanges,pairs_filter,loggerArbitrage,details=True)
                else:
                    print('logarb correct usage: logarb [details]')

            elif s=='':
                pass

            else:
                print('command not recognized')

        except Exception as e:
            print('Error in shell: ' + str(e))
            pass
    
    
    
    
    
    
