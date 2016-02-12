import sys, time, urllib, gzip, StringIO, urllib2, csv

infile = sys.stdin
outfile = sys.stdout

r = csv.DictReader(infile)
header = r.fieldnames

w = csv.DictWriter(outfile, fieldnames=r.fieldnames)
w.writeheader()

for result in r:
	url_handle = urllib.urlopen(result['url'])
	url_f = StringIO.StringIO(url_handle.read())
	i = 1
	with gzip.GzipFile(fileobj=url_f) as f:
		for line in f:
			result['web_response'] = str(line).strip()
			w.writerow(result)
			i=i+1