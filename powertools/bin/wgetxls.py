import sys, time, urllib, gzip, StringIO, urllib2, csv
from splunklib.searchcommands import \
    dispatch, GeneratingCommand, Configuration, Option, validators

from io import BytesIO
import xlrd
import pyexcel as pe
from pyexcel.ext import xls

@Configuration()
class WGetxlsCommand(GeneratingCommand):
	url = Option(require=True)

	def generate(self):
		workbook = xlrd.open_workbook(file_contents=urllib2.urlopen(self.url).read())
		i = 1
		worksheets = workbook.sheet_names()
		for worksheet_name in worksheets:
			worksheet = workbook.sheet_by_name(worksheet_name)
			num_rows = worksheet.nrows - 1
			num_cells = worksheet.ncols - 1
			curr_row = -1
			while curr_row < num_rows:
				curr_row += 1
				if curr_row == 0 :
					head_row = worksheet.row(curr_row)
				else:
					row = worksheet.row(curr_row)
				#print 'Row:', curr_row
				curr_cell = -1
				_raw = ""
				line = {}
				while curr_cell < num_cells:
					if curr_row > 0:
						curr_cell += 1
						# Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
						cell_type = worksheet.cell_type(curr_row, curr_cell)
						cell_value = worksheet.cell_value(curr_row, curr_cell)
						head_value = worksheet.cell_value(0, curr_cell)
						#print '	', cell_type, ':', cell_value
						_raw = _raw + '"' + str(head_value) + '"="' + str(cell_value) +'" '
						line[str(head_value)] = str(cell_value)
					else:
						curr_cell += 1
				if curr_row > 1:
					line["_time"] = time.time()
					line["line_number"] = i
					line["_raw"] = _raw
					line["worksheet_name"] = worksheet_name
					yield line
					i=i+1
					
			
dispatch(WGetxlsCommand, sys.argv, sys.stdin, sys.stdout, __name__)




