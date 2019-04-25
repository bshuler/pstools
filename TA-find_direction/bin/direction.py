import csv
import sys
import ipaddress

infile = sys.stdin
outfile = sys.stdout

r = csv.DictReader(infile)
header = r.fieldnames

w = csv.DictWriter(outfile, fieldnames=r.fieldnames)
w.writeheader()

internal_ranges = []

file = open('../lookups/internal_ranges.csv', "rU")
reader = csv.DictReader(file)
for row in reader:
    internal_ranges.append(ipaddress.ip_network(row['range'].strip().decode('utf-8')))


def find_orientation(ip):
    if isinstance(ip, str):
        ip = ip.decode('utf-8')
    ip = ipaddress.ip_address(ip.strip())
    for my_range in internal_ranges:
        if ip in my_range:
            return 'internal'
    return 'external'


def find_direction(src_ip, dest_ip):
    if find_orientation(src_ip) is 'internal' and find_orientation(dest_ip) is 'external':
        return 'outbound'
    if find_orientation(src_ip) is 'external' and find_orientation(dest_ip) is 'internal':
        return 'inbound'
    return 'none'


for result in r:
    result['direction'] = find_direction(result['src_ip'], result['dest_ip'])
    w.writerow(result)
