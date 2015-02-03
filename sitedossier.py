#!/usr/bin/env python
# encoding: utf-8

import urllib
import urllib2
import sys
import re
import json
import time
import random
import subprocess

# 动态配置项
retrycnt = 3	# 重试次数
timeout = 10	# 超时时间

def http_request_get(url):
	'''
		url = 'http://www.google.com/search.php?a=123&b=456'
		http_request_get(url)
	'''
	trycnt = 0
	while True:
		try:
			request = urllib2.Request(url)
			request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1')
			request.add_header('Referer', request.get_full_url())
			# request.add_header('Cookie', cookies)
			u = urllib2.urlopen(request , timeout = timeout)
			content = u.read()
			return {'html':content,'url':u.geturl()}
		except Exception, e:
			print e
			trycnt += 1
			if trycnt >= retrycnt:
				# print 'retry overflow'
				return "retryover"

def get_domains(content):
	domain = []
	re_domain = re.compile(r'(?<=<a href\=\"/site/).*?(?=\">)')
	domains = re_domain.findall(content)
	for site in domains:
		domain.append(site)
	return domain

def process_content(url):
	try:
		html = http_request_get(url)['html']
		nextpage_obj = re.search('<a href="/parentdomain/(.*?)"><b>Show', html)

		if nextpage_obj:
			sub_domains.extend(get_domains(html))
			# print 'have npage'
			next_url = 'http://www.sitedossier.com/parentdomain/%s' % nextpage_obj.group(1)
			# print next_url
			process_content(next_url)
		else:
			# print 'not npage'
			sub_domains.extend(get_domains(html))
	except Exception, e:
		pass

def main(pre_domain):
	global sub_domains
	sub_domains = []
	url = 'http://www.sitedossier.com/parentdomain/%s' % pre_domain
	process_content(url)
	return sub_domains

if __name__ == "__main__":
	if len(sys.argv) == 2:
		global pre_domain
		pre_domain = sys.argv[1]
		print main(pre_domain)
		sys.exit(0)
	else:
		print ("usage: %s domain" % sys.argv[0])
		sys.exit(-1)
