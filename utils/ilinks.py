# encoding: utf-8

# import sys
# sys.path.append("../")

import re
from common import http_request_get, http_request_post, is_domain

class Ilinks(object):
    """docstring for Ilinks"""
    def __init__(self, domain):
        super(Ilinks, self).__init__()
        self.domain = domain
        self.url = 'http://i.links.cn/subdomain/'
        self.subset = []

    def run(self):
        try:
            payload = {
                'b2': 1,
                'b3': 1,
                'b4': 1,
                'domain': self.domain
            }
            r = http_request_post(self.url,payload=payload).text
            subs = re.compile(r'(?<=value\=\"http://).*?(?=\"><input)')
            for item in subs.findall(r):
                if is_domain(item):
                    self.subset.append(item)

            return list(set(self.subset))
        except Exception as e:
            logging.info(str(e))
            return self.subset

# ilinks = Ilinks('aliyun.com')
# ilinks.run()
# print(ilinks.subset)