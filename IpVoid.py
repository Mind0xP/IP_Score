import re
import requests
import ipaddress
from time import sleep
from ThreadWrapper import ThreadWrapper

HEADERS = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
        }
IP_VOID_URL = 'http://www.ipvoid.com/ip-blacklist-check/'

class IpVoid(object):
    def __init__(self, ip):
        self.ip = ip
        self._score = None

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, score):
        self._score = score

    def get_score(self):
        _verdict = self._get_verdict(self.ip)
        if _verdict:
            _parsed = self._parse_verdict(_verdict)
            if _parsed:
                self.score = _parsed
            else:
                self.score = 'Not Concluded'

    @staticmethod
    def _parse_verdict(res):
        regexp = r'(?:<tr><td>Blacklist\sStatus</td><td><span\sclass=\"label \w+-\w+\">)(?P<rate>.+(?=\s\d)\s(?P<score>\d+\/\d+))'
        match = re.search(regexp, res)
        if match:
            return match.groups()[0]
        return None

    @staticmethod
    def _get_verdict(ip):
        # so we dont spam the server
        sleep(2)
        query = {'ip': ip}
        try:
            res = requests.post(IP_VOID_URL, data=query, headers=HEADERS)
        except:
            return None
        return res.text

class IpVoidThreaded(ThreadWrapper):
    def __init__(self, fqdns, workers=60):
        super().__init__(threads_count=workers, debug=True)
        self.ipVoid_instances = [IpVoid(ip) for ip in fqdns if ip]
        self._results = []

    def run(self):
        self.execute_method('get_score', self.ipVoid_instances)
        
    def get_results(self):
        for instance in self.ipVoid_instances:
            self._results.append({'fqdn': instance.ip, 'score': instance.score})
        return self._results