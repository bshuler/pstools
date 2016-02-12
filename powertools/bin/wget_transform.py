import sys, time, urllib, gzip, StringIO, urllib2, csv

infile = sys.stdin
outfile = sys.stdout

r = csv.DictReader(infile)
header = r.fieldnames

w = csv.DictWriter(outfile, fieldnames=r.fieldnames)
w.writeheader()

for result in r:
	response = urllib2.urlopen(result['url'])
	i = 1
	for line in response:
		result['web_response'] = str(line).strip()
		w.writerow(result)
		i=i+1