import sys, os
import logging

SPLUNK_HOME = os.getenv('SPLUNK_HOME', default=None)
if not SPLUNK_HOME:
    sys.exit('No env SPLUNK_HOME found.')

DEFAULT_LOG_FORMAT = '%(asctime)s, Level=%(levelname)s, Pid=%(process)s, Logger=%(name)s, File=%(filename)s, ' \
                 'Line=%(lineno)s, %(message)s'
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S %Z'

def setup_logging(level, log_format=DEFAULT_LOG_FORMAT, date_format=DEFAULT_DATE_FORMAT):
    logging.basicConfig(level=level,
                        format=log_format,
                        datefmt=date_format,
                        filename="%s/var/log/splunk/%s.log" % (SPLUNK_HOME, os.path.basename(__file__)))

# To see debug and above level logs
setup_logging(logging.DEBUG)


users = [{
    "name": "alice",
    "password": "correctpassword",
    "roles": "admin:super"
},{
    "name": "bob",
    "password": "correctpassword",
    "roles": "user"
}
]

def output(l):
    print(l)
    logging.debug("output: %s" % l)

def getUser(username):
    for u in users:
        if u["name"] == username:
            return u
    return None

def getLine():
    for line in sys.stdin:
        if "=" in line:
            return line.split("=")[0].lstrip(" -"), line.split("=")[1].rstrip()

def userLogin():
    logging.debug("Starting userLogin")
    conf = {}
    k, v = getLine()
    conf[k] = v
    k, v = getLine()
    conf[k] = v
    grabeof = getLine()
    
    # Dont log this. It is only needed temporarily while debugging.
    #logging.debug("conf: %s " % (conf))

    user_object = getUser(conf["username"])
    if user_object:
        if user_object["password"] == conf["password"]:
            output("--status=success")
            logging.debug("Ending userLogin success")
            sys.exit()
    output("--status=fail")
    logging.debug("Ending userLogin fail")
    sys.exit()

def getUserInfo():
    logging.debug("Starting getUserInfo")
    conf = {}
    k, v = getLine()
    conf[k] = v
    grabeof = getLine()
    user = getUser(conf["username"])
    if user:
        output("--status=success --userInfo=%s;%s;%s;%s" % (user["name"], user["name"], user["name"], user["roles"]))
        logging.debug("Ending getUserInfo success")
        sys.exit()
    output("--status=fail")
    logging.debug("Ending getUserInfo fail")
    sys.exit()


def getUsers():
    logging.debug("Starting getUsers")
    line = "--status=success "
    for user in users:
        line += "--userInfo=%s;%s;%s;%s " % (user["name"], user["name"], user["name"], user["roles"])
    output(line)
    logging.debug("Ending getUsers")



if __name__ == "__main__":
    logging.debug("Starting %s arg: %s" % (sys.argv[0], sys.argv[1]))
    if sys.argv[1] == "userLogin":
        userLogin()
    if sys.argv[1] == "getUserInfo":
        getUserInfo()
    if sys.argv[1] == "getUsers":
        getUsers()

 
