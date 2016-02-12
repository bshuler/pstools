import splunk.Intersplunk as si
import sys
import os
import logging, logging.handlers
import splunk

def setup_logging():
    logger = logging.getLogger('splunk.btool')    
    SPLUNK_HOME = os.environ['SPLUNK_HOME']
    
    LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
    LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log-local.cfg')
    LOGGING_STANZA_NAME = 'python'
    LOGGING_FILE_NAME = "btool_search_cmd.log"
    BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')
    LOGGING_FORMAT = "%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s"
    splunk_log_handler = logging.handlers.RotatingFileHandler(os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a') 
    splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.addHandler(splunk_log_handler)
    splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
    return logger



if __name__ == '__main__':
    logger = setup_logging()
    
    # Set this when debugging
    # logger.setLevel(logging.DEBUG)

    logger.debug("entered __main__")
    conf=''
    stanza_asked=''
    try:
        if len(sys.argv) > 2:
            conf = sys.argv[2]
            logger.debug("conf: '" + conf + "'")
        else:
            raise Exception("Usage: btool confName [stanza]")

        if len(sys.argv) > 3:
            stanza_asked = sys.argv[3]
            logger.debug("stanza: '" + stanza_asked + "'")

        (isgetinfo, sys.argv) = si.isGetInfo(sys.argv)

        if isgetinfo:
            reqsop = True
            preop = "prebtool " + conf + " " + stanza_asked
            logger.debug("passed to prebtool: '" + preop + "'")
            si.outputInfo(False, False, False, reqsop, preop) # calls sys.exit()

        results = si.readResults(None, None, False)
        si.outputResults(results)
        logger.debug("exited __main__")
    except Exception, e:
        si.generateErrorResults(e)
