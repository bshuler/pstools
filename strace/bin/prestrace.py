import splunk.Intersplunk as si
import sys
import os
import logging, logging.handlers
import splunk
import time
import subprocess
import pprint
import socket
from os.path import expanduser
import urllib

def setup_logging():
    logger = logging.getLogger('splunk.test')    
    SPLUNK_HOME = os.environ['SPLUNK_HOME']
    
    LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
    LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log-local.cfg')
    LOGGING_STANZA_NAME = 'python'
    LOGGING_FILE_NAME = "strace_search_cmd.log"
    BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')
    LOGGING_FORMAT = "%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s"
    splunk_log_handler = logging.handlers.RotatingFileHandler(os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a') 
    splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.addHandler(splunk_log_handler)
    splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
    return logger



if __name__ == '__main__':
    try:
        logger = setup_logging()
        
        # Set this when debugging
        logger.setLevel(logging.DEBUG)

        logger.debug("entered __main__")
        search=''

        # grab auth
        _time=time.time()
        results = []
        # this call populates the results variable with all the events passed into the search script:
        results,dummyresults,settings = splunk.Intersplunk.getOrganizedResults()
        logger.debug(pprint.pformat(settings))

        authString = settings.get("authString", None)
        sessionKey = settings.get("sessionKey", None)
        if sessionKey == None:
            splunk.Intersplunk.generateErrorResults("sessionKey not given.")
            sys.exit

        #my_env = os.environ
        #my_env["SPLUNK_TOK"] = authString
        #logger.debug("SPLUNK_TOK = "+authString)


        #os.system("splunk search '* | head 1' -format csv") 
        hostname = socket.gethostname()
        logger.debug("hostname = "+hostname )

        home = expanduser("~")
        auth_path=home+'/.splunk/authToken_'+hostname+'_8089'
        logger.debug("auth_path = "+auth_path )
        with open(auth_path,'w+') as myfile: 
            myfile.write('<auth><username>admin</username><sessionkey>'+sessionKey+'</sessionkey><cookie>splunkd_8089</cookie></auth>')
        
        search = urllib.unquote(sys.argv[1])

        logger.debug('search = '+search)
        proc = subprocess.Popen(['splunk', 'search',  search, '-output', 'csv'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        proc_out, proc_err = proc.communicate()
        
        logger.debug('Starting Output')
        logger.debug(pprint.pformat(proc_out))
        logger.debug('Ending Output')

        if not proc_err == '':
            raise Exception("prestrace returned something in stderr: '%s'" % proc_err)

        lines = proc_out.split("\n")
        
        results = []
        for line in lines:
            if line != '':
                res = {}
                res['_raw'] = line
                results.append(res)
        logger.debug(pprint.pformat(results))
        si.outputResults(results, fields=['_raw'])
        logger.debug("exited __main__")
    except Exception, e:
        si.generateErrorResults(e)




