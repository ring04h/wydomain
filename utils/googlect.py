# encoding: utf-8

# import sys
# sys.path.append("../")

import time
import json
import logging

from random import Random,uniform
from urllib import quote
from common import http_request_get

def random_sleep():
    time.sleep(uniform(0,2))

def random_str(randomlength=8):
    rstr = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        rstr += chars[random.randint(0, length)]
    return rstr.lower()

class TransparencyReport(object):
    """docstring for TransparencyReport"""
    def __init__(self, domain):
        self.domain = domain
        self.token = ""
        self.dns_names = []
        self.subjects = []
        self.hashs = []
        self.num_result = 0
        self.website = 'https://www.google.com/transparencyreport/jsonp/ct'

    def run(self):
        self.parser_subject()
        self.hashs = list(set(self.hashs)) # unique sort hash
        self.parser_dnsname()
        self.dns_names = list(set(self.dns_names))
        self.subjects = list(set(self.subjects))
        return {'subjects': self.subjects, 'dns_names': self.dns_names}

    def parser_subject(self):
        try:
            callback = random_str()
            url = '{0}/search?domain={1}&incl_exp=true&incl_sub=true&token={2}&c={3}'.format(
                    self.website, self.domain, quote(self.token), callback)
            content = http_request_get(url).content
            result = json.loads(content[27:-3])
            self.token = result.get('nextPageToken')
            for subject in result.get('results'):
                if subject.get('subject'):
                    self.dns_names.append(subject.get('subject'))
                if subject.get('hash'):
                    self.hashs.append(subject.get('hash'))
        except Exception as e:
            logging.info(str(e))

        if self.token:
            self.parser_subject()

    def parser_dnsname(self):
        for hashstr in self.hashs:
            try:
                callback = random_str()
                url = '{0}/cert?hash={1}&c={2}'.format(
                        self.website, quote(hashstr), callback)
                content = http_request_get(url).content
                result = json.loads(content[27:-3])
                if result.get('result').get('subject'):
                    self.subjects.append(result.get('result').get('subject'))
                if result.get('result').get('dnsNames'):
                    self.dns_names.extend(result.get('result').get('dnsNames'))
            except Exception as e:
                logging.info(str(e))
            random_sleep()

# ct = TransparencyReport('aliyun.com')
# ct.run()
# print ct.subjects
# print ct.dns_names
