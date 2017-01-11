#!/usr/bin/env python
# encoding: utf-8
# email: c4bbage@qq.com
# weibo: @s4turnus
# encoding: utf-8

# import sys
# sys.path.append("../")

import re
import json
import requests
import logging
from common import curl_get_content, http_request_get, is_domain,http_request_post
# API INFO https://api.passivetotal.org/api/docs/
class PassiveTotal(object):
    """docstring for PassiveTotal"""
    def __init__(self, domain):
        super(PassiveTotal, self).__init__()
        self.domain = domain
        self.subset = []
        self.website = "https://www.passivetotal.org"

    def run(self):
        try:
            # 此auth 需要自行申请，每个auth 每天有查询次数限制
            auth=("ouqiower@163.com","d160262241ccf53222d42edc6883c129")
            payload={"query":"*.%s" % self.domain}
            url = "https://api.passivetotal.org/v2/enrichment/subdomains"
            response = requests.get(url,auth=auth,params=payload)

            for sub in json.loads(response.content)['subdomains']:
                sub="%s.%s" %(sub,self.domain)
                if is_domain(sub):
                    self.subset.append(sub)

            return list(set(self.subset))
        except Exception as e:
            logging.info(str(e))
            return self.subset

# passive = PassiveTotal('aliyun.com')
# print passive.run()
        