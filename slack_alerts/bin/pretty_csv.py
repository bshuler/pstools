import csv
import gzip
import string

def pretty_file(filename, **options):
    with gzip.open(filename, 'rb') as csvfile:
        table_string = ""
        reader       = csv.reader( csvfile )

        for row in reader:
            table_string += "" + \
                "| " + \
                  string.join( row, " | " ) + \
                " |" + \
                "\n"
    return table_string