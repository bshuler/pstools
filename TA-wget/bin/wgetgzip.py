import sys, time, urllib, gzip, StringIO
from splunklib.searchcommands import \
    dispatch, GeneratingCommand, Configuration, Option, validators

@Configuration()
class WGetCommand(GeneratingCommand):
    url = Option(require=True)

    def generate(self):
        url_handle = urllib.urlopen(self.url)
        url_f = StringIO.StringIO(url_handle.read())
        i = 1
        with gzip.GzipFile(fileobj=url_f) as f:
            for line in f:
                yield {'_time': time.time(), 'event_no': i, '_raw': line.rstrip() }
                i=i+1

dispatch(WGetCommand, sys.argv, sys.stdin, sys.stdout, __name__)