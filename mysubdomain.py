#!/usr/bin/env python
# encoding: utf-8

'''
	容错判断
	为了更好的兼容性，加入全局重试次数机制，超时机制
'''

import urllib
import urllib2
import sys
import re
import json
import time
import random
import netcraft
import sitedossier

# 动态配置项
retrycnt = 3	# 重试次数
timeout = 10	# 超时时间

# 随机AGENT
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

# 随机X-Forwarded-For，动态IP
def random_x_forwarded_for():
	return '%d.%d.%d.%d' % (random.randint(1, 254),random.randint(1, 254),random.randint(1, 254),random.randint(1, 254))

def http_request_get(url):
	'''
		url = 'http://www.google.com/search.php?a=123&b=456'
		http_request_get(url)
	'''
	trycnt = 0
	while True:
		try:
			request = urllib2.Request(url)
			request.add_header('User-Agent', random_useragent())
			request.add_header('Referer', request.get_full_url())
			u = urllib2.urlopen(request , timeout = timeout)
			content = u.read()
			return {'html':content,'url':u.geturl()}
		except Exception, e:
			# print e
			trycnt += 1
			if trycnt >= retrycnt:
				# print 'retry overflow'
				return "retryover"

def http_request_post(url, data):
	'''
		data = {'a' : '123', 'b' : '456'}  ?a=123&b=456
		url = 'http://www.google.com/search.php'
		http_request_post(url, data)
	'''
	trycnt = 0
	while True:
		try:
			request = urllib2.Request(url)
			request.add_header('User-Agent', random_useragent())
			request.add_header('Referer', request.get_full_url())
			data = urllib.urlencode(data)
			u = urllib2.urlopen(request,data,timeout = timeout)
			content = u.read()
			return {'html':content,'url':u.geturl()}
		except Exception, e:
			# print e
			trycnt += 1
			if trycnt >= retrycnt:
				# print 'retry overflow'
				return "retryover"

def links_get(domain):
	trytime = 0
	domainslinks = []
	try:
		req=urllib2.Request('http://i.links.cn/subdomain/?b2=1&b3=1&b4=1&domain='+domain)
		req.add_header('User-Agent',random_useragent())
		res=urllib2.urlopen(req, timeout = 30)
		src=res.read()

		TempD = re.findall('value="http.*?">',src,re.S)
		for item in TempD:
			item = item[item.find('//')+2:-2]
			domainslinks.append(item)
			domainslinks={}.fromkeys(domainslinks).keys()
		return domainslinks

	except Exception, e:
		# print e
		trytime += 1
		if trytime > 3:
			return domainslinks

def bing_get(domain):
	trytime = 0
	f = 1
	domainsbing = []
	while True:
	    try:            
	        req=urllib2.Request('http://cn.bing.com/search?count=50&q=site:'+domain+'&first='+str(f))
	        req.add_header('User-Agent',random_useragent()) 
	        res=urllib2.urlopen(req, timeout = 30)
	        src=res.read()
	        TempD=re.findall('<cite>(.*?)<\/cite>',src)
	        for item in TempD:
	            item=item.split('<strong>')[0]
	            item += domain
	            try:
	                if not (item.startswith('http://') or item.startswith('https://')):
	                    item = "http://" + item
	                proto, rest = urllib2.splittype(item)
	                host, rest = urllib2.splithost(rest) 
	                host, port = urllib2.splitport(host)
	                if port == None:
	                    item = host
	                else:
	                    item = host + ":" + port
	            except:
	                 print traceback.format_exc()
	                 pass                            
	            domainsbing.append(item)         
	        if f<500 and re.search('class="sb_pagN"',src) is not None:
	            f = int(f)+50
	        else:
	            subdomainbing={}.fromkeys(domainsbing).keys()
	            return subdomainbing
	            break
	    except Exception, e:
	        trytime+=1
	        if trytime>3:
	            return domainsbing

def google_get(domain):
    trytime = 0
    s=1
    domainsgoogle=[]
    while True:
        try:
            req=urllib2.Request('http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=site:'+domain+'&rsz=8&start='+str(s))
            req.add_header('User-Agent',random_useragent()) 
            res=urllib2.urlopen(req, timeout = timeout)
            src=res.read()
            results = json.loads(src)
            TempD = results['responseData']['results']
            for item in TempD:
                item=item['visibleUrl'] 
                item=item.encode('utf-8')
                domainsgoogle.append(item)                
            s = int(s)+8
        except Exception, e:
            trytime += 1
            if trytime >= 3:
                domainsgoogle={}.fromkeys(domainsgoogle).keys()
                return domainsgoogle 


def alexa_get(domain):
	url = 'http://alexa.chinaz.com/?domain=' + domain
	html = http_request_get(url)
	if html != 'retryover':
		html = html['html']
		re_domain = re.compile(r'(?<=class\="rank_left">).*?(?=</td>)')
		domains = re_domain.findall(html)
		if domains.count('OTHER') >= 1:
			split_index = domains.index('OTHER')
			return domains[1:split_index]
		else:
			# 结果为空
			return ""
	else:
		# print 'retry overflow'
		return "retryover"

def get_subdomain_run(domain):
	print '* Starting subdomain search task'
	print '-' * 50
	mydomains = []
	mydomains.extend(links_get(domain))
	mydomains.extend(alexa_get(domain))
	mydomains.extend(bing_get(domain))
	mydomains.extend(google_get(domain))
	mydomains.extend(sitedossier.main(domain))
	mydomains.extend(netcraft.main(domain))
	mydomains = list(set(mydomains))
	return mydomains

if __name__ == "__main__":
   if len(sys.argv) == 2:
      print get_subdomain_run(sys.argv[1])
      sys.exit(0)
   else:
       print ("usage: %s domain" % sys.argv[0])
       sys.exit(-1)

