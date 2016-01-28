try:
    import threading
    from logger_handler import loggerHandler
    import time
    from datetime import datetime
except ImportError:
    pass

lock = threading.Lock()

#thread which init exchange
class InitExchangeWorker(threading.Thread):
	    
    def __init__(self,threadID,name,exchange,assets,logger):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.exchange = exchange
        self.assets = assets
        #self.lock = lock
        self.logger = logger
        
    def run(self):
        
        lock.acquire()
        self.logger.info(self.name + ' starts to init exchange ' + self.exchange.name)
        lock.release()

        i = 5
        istatus = -1
        while i>0 and istatus!=0:
            istatus,msg = self.exchange.initPairs(self.assets)
            i -= 1

        lock.acquire()
        if istatus==0:
            self.logger.info(self.name + ' finished to init exchange ' + self.exchange.name + ' with success(' +
                             str(len(self.exchange.pairs)) + ' pairs)')
        else:
            self.logger.fatal(self.name + ' failed to init exchange ' + self.exchange.name + ': ' + msg)
        lock.release()

#thread listening to asset price continuously
class PriceListenerWorker(threading.Thread):

    exit_flag = 0
    
    def __init__(self,threadID,name,exchange,pair,logger):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.exchange = exchange
        self.pair = pair
        #self.lock = lock
        self.logger = logger
        self.old_mkt_depth = None

    def logLock(self,msg,bPrint=True):
        lock.acquire()
        self.logger.info(msg,bPrint)
        lock.release()

    def stop(self):
        self.exit_flag = 1
        
    def run(self):
        self.logLock(self.name + ' starts to listen to ' +
                     self.pair + ' on exchange ' + self.exchange.name, bPrint=False)

        while not self.exit_flag:
            try:
                self.exchange.refreshMarketDepth(self.pair)
                new_mkt_depth = self.exchange.getMarketDepth(self.pair)
                if not self.old_mkt_depth==new_mkt_depth:
                    new_mkt_depth.setUpdatedTime(datetime.now())
                    self.old_mkt_depth = new_mkt_depth.__copy__()
                
            except Exception as e:
                self.logLock('Error while refreshing ' + self.pair +
                             ' on ' + self.exchange.name + ': ' + str(e),bPrint=False)
            #time.sleep(0.5)
        self.logLock(self.name + ' stopped',bPrint=False)
            
        

