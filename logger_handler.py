import logging
import datetime
import os

class loggerHandler():

    logger = None
    hdlr = None
    
    def __init__(self,
                 appname,
                 log_path = 'log/',
                 log_file_pattern='',
                 log_date = datetime.date.today().strftime('%Y-%m-%d'),
                 log_file_ext = '.log',
                 log_formatter = '%(asctime)s %(levelname)s %(message)s',
                 log_level = logging.DEBUG):

        try:
            os.makedirs(log_path)
        except OSError as exception:
            if os.path.exists(log_path):
                pass
            else:
                raise
        
        self.logger = logging.getLogger(appname)
        if log_file_pattern == '': log_file_pattern = appname
        self.hdlr = logging.FileHandler(log_path+log_file_pattern+'_'+log_date+log_file_ext)
        self.hdlr.setFormatter(logging.Formatter(log_formatter))
        self.logger.addHandler(self.hdlr)
        self.logger.setLevel(log_level)
        
    def info(self,msg,bPrint=True,bReturnStr=False):
        self.logger.info(msg)
        if bPrint: print(msg)
        if bReturnStr: return msg

    def warning(self,msg,bPrint=True):
        self.logger.warning(msg)
        if bPrint: print(msg)
    
    def fatal(self,msg,bPrint=True):
        self.logger.fatal(msg)
        if bPrint: print(msg)

    def close(self):
        self.hdlr.close()
        self.logger.removeHandler(self.hdlr)

if __name__ == "__main__":
    appname = 'test_logger'
    logger = loggerHandler(appname)
    logger.info('test info')
    logger.warning('test warning')
    logger.fatal('test fatal')
    logger.close()
    
