import sys, time, urllib, gzip, StringIO, urllib2, csv
from splunklib.searchcommands import \
    dispatch, GeneratingCommand, Configuration, Option, validators

@Configuration()
class WGetCommand(GeneratingCommand):
	url = Option(require=True)

	def generate(self):
		response = csv.DictReader(urllib2.urlopen(self.url))
		i = 1
		for line in response:
			_raw=""
			for key, value in line.iteritems() :
				_raw = _raw + '"' + key + '"="' + value +'" '
			line["_time"] = time.time()
			line["line_number"] = i
			line["_raw"] = _raw
			yield line
			i=i+1
dispatch(WGetCommand, sys.argv, sys.stdin, sys.stdout, __name__)
