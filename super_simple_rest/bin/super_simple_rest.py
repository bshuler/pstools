from splunk import rest

# curl -k -u admin:changeme https://localhost:8089/services/super_simple_rest

#sys.path.append("/home/splunk/splunk/etc/apps/super_simple_rest/bin/pydevd-pycharm.egg")
#import pydevd_pycharm

class HelloWorld(rest.BaseRestHandler):

    def handle_POST(self):
        #pydevd_pycharm.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)
        self.response.setHeader("content-type", "text/html")
        self.response.write("<p>Hello World</p>")

    #handle verbs, otherwise Splunk will throw an error
    handle_GET = handle_POST