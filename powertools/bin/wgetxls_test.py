import sys, time, urllib, gzip, StringIO, urllib2, csv
from splunklib.searchcommands import \
    dispatch, GeneratingCommand, Configuration, Option, validators

import pyexcel as pe
from pyexcel.ext import xls

@Configuration()
class WGetxlsCommand(GeneratingCommand):
	url = Option(require=True)

	def generate(self):
		sheet = pe.load(urllib2.urlopen(self.url), name_columns_by_row=0)
		i = 1
		records = sheet.to_records()
		for record in records:
			_raw=""
			keys = sorted(record.keys())
			for key in keys:
				line[key] = record[key]
				_raw = _raw + '"' + key + '"="' + record[key] +'" '
			line["_time"] = time.time()
			line["line_number"] = i
			line["_raw"] = _raw
			yield line
			i=i+1
dispatch(WGetxlsCommand, sys.argv, sys.stdin, sys.stdout, __name__)
