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

# 引入随机AGENT
USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]

def random_useragent():
	return random.choice(USER_AGENTS)

def get_cookie():
	cmdline = 'phantomjs ph_cookie.js'
	run_proc = subprocess.Popen(cmdline,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	(stdoutput,erroutput) = run_proc.communicate()
	cookies = stdoutput.rstrip()
	return cookies

def http_request_get(url):
	'''
		url = 'http://www.google.com/search.php?a=123&b=456'
		http_request_get(url)
	'''
	trycnt = 0
	while True:
		try:
			request = urllib2.Request(url)
			request.add_header('User-Agent', '')
			request.add_header('Referer', request.get_full_url())
			request.add_header('Cookie', cookies)
			u = urllib2.urlopen(request , timeout = timeout)
			content = u.read()
			return {'html':content,'url':u.geturl()}
		except Exception, e:
			# print e
			trycnt += 1
			if trycnt >= retrycnt:
				# print 'retry overflow'
				return {'html':"", 'url':""}

def get_domains(content):
	domain = []
	replace_str = '<FONT COLOR="#ff0000">%s</FONT>' % pre_domain
	re_domain = re.compile(r'(?<=rel\="nofollow">).*?(?=</a>)')
	domains = re_domain.findall(content)
	for site in domains:
		domain.append(site.replace(replace_str, pre_domain))
	return domain

# 迭代处理下一页的URL内容，并且加入二级域名列表里面
def process_content(url):
	html = http_request_get(url)['html']

	re_nextpage_str = u'<A href\=\"/?host\=(.*?)&position\=limited\"><b>Next page</b></a>'
	nextpage_obj = re.search('<A href="(.*?)"><b>Next page</b></a>', html)

	if nextpage_obj:
		# print 'have npage'
		sub_domains.extend(get_domains(html))
		next_request_url = 'http://searchdns.netcraft.com' + nextpage_obj.group(1)
		process_content(next_request_url)
		'''
		# 高级操作技巧，暂时用不上
		npage_url = nextpage_obj.group(1).split('?')
		npage_url = npage_url[1].split('&')
		for npage_str in npage_url:
			npage_str = npage_str.split('=')
			if npage_str[0] == 'from':
				print 'from: %s' % npage_str[1]
			if npage_str[0] == 'last':
				print 'last: %s' % npage_str[1]
		'''
	else:
		# print 'not npage'
		sub_domains.extend(get_domains(html))

def main(domain):
	global pre_domain
	pre_domain = domain
	global cookies
	cookies = get_cookie()
	global sub_domains
	sub_domains = []
	url = 'http://searchdns.netcraft.com/?restriction=site+contains&position=limited&host=%s' % pre_domain
	process_content(url)
	return sub_domains

if __name__ == "__main__":
	if len(sys.argv) == 2:
		domain = sys.argv[1]
		print main(domain)
		sys.exit(0)
	else:
		print ("usage: %s domain" % sys.argv[0])
		sys.exit(-1)



