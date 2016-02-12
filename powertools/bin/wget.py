import sys, time, urllib, gzip, StringIO, urllib2
from splunklib.searchcommands import \
    dispatch, GeneratingCommand, Configuration, Option, validators

@Configuration()
class WGetCommand(GeneratingCommand):
    url = Option(require=True)

    def generate(self):
        response = urllib2.urlopen(self.url)
        i = 1
        for line in response:
            
            yield {'_time': time.time(), 'event_no': i, '_raw': line.rstrip() }
            i=i+1

dispatch(WGetCommand, sys.argv, sys.stdin, sys.stdout, __name__)