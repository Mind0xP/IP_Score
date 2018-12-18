import requests
import re
import threading
import csv
import ipaddress
from datetime import datetime

ip_void_url = 'http://www.ipvoid.com/ip-blacklist-check/'

def send_post_data(url, data):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
    }
    query = { 'ip': data }
    res = requests.post(url, data=query, headers=headers)
    return res.text

def parse_status(res):
    regexp = r'(?:<tr><td>Blacklist\sStatus</td><td><span\sclass=\"label \w+-\w+\">)(?P<rate>.+(?=\s\d)\s(?P<score>\d+\/\d+))'
    match = re.search(regexp, res)
    if match.groups():
        return match.groups()[0]
    return None

def is_ip_private(ip):
    return ipaddress.ip_address(ip).is_private

def get_score(ip):
    output = {}
    if ip:
        res = send_post_data(ip_void_url, ip)
        if res:
            score = parse_status(res)
            if score:
                output['ip'] = ip
                output['score'] = score
            return output

def get_ips_csv(filename):
    ips = []
    with open(filename) as f:
         reader = csv.reader(f, delimiter=",")
         for i in reader:
            if not is_ip_private(i[0]):
                ips.append(i[0])
    return ips

def write_csv(filename, data):
    try:
        with open(filename, 'w', newline='') as f:
            fieldnames = ['ip', 'score']
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for row in data:
                w.writerow(row)
    except:
        return False
    return True

def run_item(f, item):
    result_info = [threading.Event(), None]
    def runit():
        result_info[1] = f(item)
        result_info[0].set()
    threading.Thread(target=runit).start()
    return result_info

def gather_results(result_infos):
    results = [] 
    for i in range(len(result_infos)):
        result_infos[i][0].wait()
        results.append(result_infos[i][1])
    return results

if __name__ == '__main__':
    # get user input & output files
    csv_input = input("Please specify input csv file: ").strip()
    csv_output = input("Please specify output csv file: ").strip()
    print("Starting to scan IPs from {}".format(csv_input))
    # set timer to calculate execution time
    startTime = datetime.now()
    # read IPs from given csv file
    ips = get_ips_csv(csv_input)
    # execute thread for each ip in list
    results = [run_item(get_score, ip) for ip in ips]
    scores = gather_results(results)
    end_time = datetime.now() - startTime
    print("Scanned {} IPs in {}".format(len(ips),end_time))
    status = write_csv(csv_output, scores)
    if status:
        print("Successfully written output to {}".format(csv_output))