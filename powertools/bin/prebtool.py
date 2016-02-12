import re, socket, subprocess, sys
import splunk.Intersplunk as si
import os
import logging, logging.handlers
import splunk
import pprint

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
        if len(sys.argv) >1:
            conf = sys.argv[1]
            logger.debug("conf='" + conf + "'")
        else:
            raise Exception("Usage: prebtool confName [stanza]")

        if len(sys.argv) >2:
            stanza_asked = sys.argv[2]
            logger.debug("stanza='" + stanza_asked + "'")
        else:
            stanza_asked = ''
            logger.debug("stanza not passed")

        re_commands = re.compile("(^[\w\-\_]+$)") 
        conf_match = re_commands.match(conf.strip())
        if not conf_match:
            raise Exception("Usage: btool confName")
        proc = subprocess.Popen(['btool', conf, 'list', stanza_asked, '--debug'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc_out, proc_err = proc.communicate()
        
        logger.debug(proc_out)

        if not proc_err == '':
            raise Exception("prebtool returned something in stderr: '%s'" % proc_err)

        host = socket.gethostname()
        stanza = ''
        lines = proc_out.split("\n")

        re_index = re.compile("^(.*)\s+\[(.*)\]")
        re_kv = re.compile("^(.*)\s+(\S+)\s+=\s+(.*)")
        
        results = []
        for line in lines:
            if line != '':
                res = {}
                index = re_index.match(line.strip())
                kv = re_kv.match(line.strip())
                if index:
                    stanza = index.group(2)
                elif kv:
                    res['host'] = host
                    res['conf'] = conf
                    res['file'] = kv.group(1)
                    res['stanza'] = stanza
                    res['key'] = kv.group(2)
                    res['value'] = kv.group(3)
                    results.append(res)
        logger.debug(pprint.pformat(results))
        si.outputResults(results, fields=['host','conf','file','stanza','key','value'])
        logger.debug("exited __main__")
    except Exception, e:
        si.generateErrorResults(e)
