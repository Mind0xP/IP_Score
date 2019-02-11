import re
import requests
from ThreadWrapper import ThreadWrapper

HEADERS = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
        }

class UrlVoid(object):
    def __init__(self, fqdn):
        self.fqdn = fqdn
        self._score = None

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, score):
        self._score = score

    def get_score(self):
        _verdict = self._get_verdict(self.fqdn)
        if _verdict:
            _parsed = self._parse_verdict(_verdict)
            if _parsed:
                self.score = _parsed
            else:
                self.score = 'Not Concluded'

    @staticmethod
    def _parse_verdict(res):
        regexp = r'(?:<tr><td><span\sclass=\"font-bold\">Blacklist Status</span></td><td><span\sclass=\"label\s\w+-\w+\">)((?P<score>\d+\/\d+))'
        match = re.search(regexp, res)
        if hasattr(match, 'groups'):
            return match.groups()[0]
        return None

    @staticmethod
    def _get_verdict(fqdn):
        url = 'https://www.urlvoid.com/scan/{}/'.format(fqdn)
        try:
            res = requests.get(url, headers=HEADERS)
        except Exception:
            return None
        return res.text

class UrlVoidThreaded(ThreadWrapper):
    def __init__(self, fqdns, workers=60):
        super().__init__(threads_count=workers, debug=True)
        self.urlVoid_instances = [UrlVoid(fqdn) for fqdn in fqdns if fqdn]
        self._results = []

    def run(self):
        self.execute_method('get_score', self.urlVoid_instances)
        
    def get_results(self):
        for instance in self.urlVoid_instances:
            self._results.append({'fqdn': instance.fqdn, 'score': instance.score})
        return self._results