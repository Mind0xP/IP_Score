import requests
import re
import threading
import csv
import ipaddress
from UrlVoid import UrlVoidThreaded
from IpVoid import IpVoidThreaded
from urlparser import urlparser
from datetime import datetime

def is_ip_private(ip):
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return False

def read_csv(filename):
    results = []
    with open(filename, encoding='utf-8') as f:
         reader = csv.reader(f, delimiter=",")
         for i in reader:
             results.append(i[0])
    return results

def filter_ips(ips):
    return [ip for ip in ips if not is_ip_private(ip[0])]

def filter_urls(urls):
    results = []
    for url in urls:
        netloc = urlparser.urlparse(url).netloc
        if not is_ip_private(netloc):
            results.append(netloc.split(' ')[0])
    return results

def write_csv(filename, data):
    try:
        with open(filename, 'w', newline='') as f:
            headers = ['fqdn','score']
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
            for row in data:
                w.writerow(row)
    except Exception as e:
        print(e)
    return True

def evaluate_urls(urls):
    filtered_urls = filter_urls(urls)
    urlVoidThreaded = UrlVoidThreaded(filtered_urls, workers=100)
    urlVoidThreaded.run()
    return urlVoidThreaded.get_results()

def evaluate_ips(ips):
    filtered_ips = filter_ips(ips)
    ipVoidThreaded = IpVoidThreaded(filtered_ips, workers=100)
    ipVoidThreaded.run()
    return ipVoidThreaded.get_results()


if __name__ == '__main__':
    # get user input & output files
    csv_input = input("Please specify input csv file: ").strip()
    csv_output = input("Please specify output csv file: ").strip()
    data_type = input("Are we handling urls or ips? (ips|urls): ").strip()
    print("Starting to scan IPs from {}".format(csv_input))
    # get current time state
    startTime = datetime.now()

    # rea from input csv
    data = read_csv(csv_input)
    if data_type == 'urls':
        verdicts = evaluate_urls(data)
    if data_type == 'ips':
        verdicts = evaluate_ips(data)

    # job execution time
    end_time = datetime.now() - startTime
    print("Scanned {} URLs in {}".format(len(verdicts), end_time))
    # write results to csv
    status = write_csv(csv_output, verdicts)
    if status:
        print("Successfully written output to {}".format(csv_output))