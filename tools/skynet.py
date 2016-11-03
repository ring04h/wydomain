# encoding: utf-8

import json
import base64
import requests
import traceback
from urllib import quote

class SkynetDomain(object):
    """docstring for SkynetDomain"""
    def __init__(self):
        self.website = 'http://127.0.0.1:5000'

    def bulk_sync(self, subdomains):
        url = '{0}/subdomain/bulk.add'.format(self.website)
        try:
            data = base64.encodestring(json.dumps(subdomains)).rstrip()
            payload = {'subdomains': quote(data)}
            r = requests.post(url, data=payload, timeout=5)
            result = json.loads(r.content)
            return True if result.get('status') else False
        except Exception:
            traceback.print_exc()
            return False

    def sync(self, subdomain):
        url = '{0}/subdomain/add?sub={1}'.format(self.website, subdomain)
        try:
            r = requests.get(url, timeout=5)
            result = json.loads(r.content)
            return True if result.get('status') else False
        except Exception:
            traceback.print_exc()
            return False

# skynet = SkynetDomain()
# _subdomain = 'workorder.console.aliyun.com'
# print(skynet.sync(_subdomain))
# _subdomains = ["awdc.aliyun.com", "24om.aliyun.com"]
# print(skynet.bulk_sync(_subdomains))