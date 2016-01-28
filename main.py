from worker import InitExchangeWorker,PriceListenerWorker
import exchange_utils as u
from exchange import Exchange
from logger_handler import loggerHandler
import mylib.email_handler as e
import arbitrage as arb
import threading
import time
import sys

appname = 'exchange'


def handleStats(sfrequence,time_start,imin,arbs,logger):
    if ((time.time()-time_start)/60)>=imin:
        subj = '[' + appname + '] ' + sfrequence + ' Arbitrages stats'
        msg = arb.log_arbitrages_stats(arbs,logger)
        e.send_email(subj,msg)
        arbs = []
        return True
    else:
        return False
   
if __name__=="__main__":

    exchanges = u.getExchangesFromXml('exchanges.xml')
    assets = u.getAssetsFromXml('assets.xml')
    pairs_filter = u.getPairsFilterFromXml('pairs_filter.xml')
    logger = loggerHandler('exchange_listener',log_path='log/')
    loggerArbitrage = loggerHandler('exchange_arbitrage',log_path='log/')
    
    #init exchanges
    u.initExchangesConcurrency(exchanges,assets,logger)
    
    #delete pair we are not listening
    u.deletePairsUnlistened(exchanges,pairs_filter)
    
    #listen to exchanges
    u.launchExchangeListenersWithPairsFilter(exchanges,pairs_filter,logger)
    time.sleep(3)

    #arbitrage every x minutes
    imin = 1.0
    time_start = time.time()
    
##    #arbitrages stats every x minutes
##    imin_stats = 60.0
##    time_start_stats = time.time()
##    arbitrages = []
    
##    #arbitrages stats 1M
##    imin_stats_1m = 1.0
##    time_start_stats_1m = time.time()
##    arbitrages_1m = []
##
##    #arbitrages stats 5M
##    imin_stats_5m = 5.0
##    time_start_stats_5m = time.time()
##    arbitrages_5m = []
##    
##    #arbitrages stats 1H
##    imin_stats_1h = 60.0
##    time_start_stats_1h = time.time()
##    arbitrages_1h = []
    
    #arbitrages stats 4H
    imin_stats_4h = 4*60.0
    time_start_stats_4h = time.time()
    arbitrages_4h = []
##    
##    #arbitrages stats 1D
##    imin_stats_1d = 24*60.0
##    time_start_stats_1d = time.time()
##    arbitrages_1d = []
    
    while True:
        #arbitrage
        if ((time.time()-time_start)/60)>=imin:
            arbs = arb.log_arbitrage(exchanges,pairs_filter,loggerArbitrage)
##            [arbitrages.append(x) for x in arbs]
##            [arbitrages_5m.append(x) for x in arbs]
##            [arbitrages_1h.append(x) for x in arbs]
            [arbitrages_4h.append(x) for x in arbs]
##            [arbitrages_1d.append(x) for x in arbs]
            time_start = time.time()
        
        #arbitrages stats
##        if handleStats('1M',time_start_stats_1m,imin_stats_1m,arbitrages_1m,loggerArbitrage):
##            time_start_stats_1m = time.time()
##            
##        if handleStats('5M',time_start_stats_5m,imin_stats_5m,arbitrages_5m,loggerArbitrage):
##            time_start_stats_5m = time.time()
##
##        if handleStats('1H',time_start_stats_1h,imin_stats_1h,arbitrages_1h,loggerArbitrage):
##            time_start_stats_1h = time.time()

        if handleStats('4H',time_start_stats_4h,imin_stats_4h,arbitrages_4h,loggerArbitrage):
            time_start_stats_4h = time.time()
        
    logger.close()
    
    
    
    
    
