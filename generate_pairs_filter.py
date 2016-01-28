import threading
import exchange_utils as u
from logger_handler import loggerHandler
from lxml import etree

def generate_pairs_filter_xml(maxpairs=None):

    lock = threading.Lock()
    exchanges = u.getExchangesFromXml('exchanges.xml')
    assets = u.getAssetsFromXml('assets.xml')
    logger = loggerHandler('generate_pairs_filter_xml',log_path='log/')
    
    u.initExchangesConcurrency(exchanges,assets,logger)
    pairs = u.getMostQuotedPairs(exchanges,logger)

    root = etree.Element('PairsFilter')

    if maxpairs:
        if maxpairs>len(pairs):
            maxpairs = len(pairs)
    else:
        maxpairs = len(pairs)
    
    for pair in pairs[:maxpairs]:
        node = etree.SubElement(root,'Pair',name=pair[1])
        
    str_xml = etree.tostring(root,pretty_print=True)
    outFile = open('pairs_filter.xml','w')
    outFile.write(str_xml.decode())
    outFile.close()
    logger.close()

if __name__=="__main__":
    generate_pairs_filter_xml()
