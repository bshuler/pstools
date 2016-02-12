import csv
import sys
from netaddr import *

infile = sys.stdin
outfile = sys.stdout

r = csv.DictReader(infile)
header = r.fieldnames

w = csv.DictWriter(outfile, fieldnames=r.fieldnames)
w.writeheader()

for result in r:
	r1 = IPRange(result['low_ip'], result['high_ip'])
	addrs = list(r1)
	all_ips=''
	for ip in addrs:
		result['all_ips'] = str(ip)
		w.writerow(result)

	