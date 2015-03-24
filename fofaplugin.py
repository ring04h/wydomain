#!/usr/bin/env python
# encoding: utf-8

'''
	UPDATE:
		将根域名的信息推入返回数据里面

	STEP:
		判断fofa的网站是否存活，isAlive
			如果不存活，直接返回{'status':'down'}
	一、从FOFA查询获取兄弟域名
	二、遍历兄弟域名，取对应域名的根域名透视结果
	三、生成字典给其它API调用

	从FOFA抓取结果
	http://fofa.so/lab/addtask/?taskaction=alldomains&domain=youku.com
	POST:
		taskaction=alldomains&domain=youku.com
	REP:
		{"error":false,"errormsg":"","jobId":"b3b6c3fd575c82b7a7f55b2ac93243c7"}

	http://fofa.so/lab/gettask?jobId=b3b6c3fd575c82b7a7f55b2ac93243c7&t=1418114915063
	GET:
		{"error":false,"msgs":["start dumping...","mysjsp.com","yoqoo.net.cn","ukoo.com.cn","1verge.cn","1verge.net.cn","yoqoo.tv","yoku.net.cn","1verge.com.cn","youku.org","yodou.com","soku.com.cn","youqoo.net","yoqoo.net","yoqoo.com","youku.com.cn","ykimg.com","youkoo.com","yoqoo.com.cn","youku.net","youku.tv","youkulabs.com","ukoo.tv","yokoo.com","yoqoo.cn","soku.com","xujingit.cn","xingmeng.com","laifeng.com","8mmmen.com","ksf-natural-water.com","heyi.com","\u003c\u003c\u003cfinished\u003e\u003e\u003e"],"finished":true}

	# 数据结构
	{
	 'parther': {
	 	'1verge.cn': {
		 	'domain': ['mysjsp.com','yoqoo.net.cn','ukoo.com.cn'],
		 	'ipaddr': ['127.0.0.1','192.168.1.1']
		 },
	 	'mysjsp.com': {
		 	'domain': ['mysjsp.com','yoqoo.net.cn','ukoo.com.cn'],
		 	'ipaddr': ['127.0.0.1','192.168.1.1']
		 },
	 	'ukoo.com.cn': {
		 	'domain': ['mysjsp.com','yoqoo.net.cn','ukoo.com.cn'],
		 	'ipaddr': ['127.0.0.1','192.168.1.1']
		 },
	 	'yoqoo.net.cn': {
		 	'domain': ['mysjsp.com','yoqoo.net.cn','ukoo.com.cn'],
		 	'ipaddr': ['127.0.0.1','192.168.1.1']
		 }
	 }
	}
'''

import sys
import random
import requests
import json
import time
import re

# 动态配置项
retrycnt = 3	# 重试次数
timeout = 10	# 超时时间

# 动态使用代理，为空不使用，支持用户密码认证
proxies = {
	# "http": "http://user:pass@10.10.1.10:3128/",
	# "https": "http://10.10.1.10:1080",
}

result = {}

# 随机生成User-Agent
def random_useragent():
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
	return random.choice(USER_AGENTS)

# 随机X-Forwarded-For，动态IP
def random_x_forwarded_for():
	return '%d.%d.%d.%d' % (random.randint(1, 254),random.randint(1, 254),random.randint(1, 254),random.randint(1, 254))

def http_request_get(url, body_content_workflow=0):
	trycnt = 0
	# cookies = dict(scan_worker='working', cookies_be='wscan.net')
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20',
		'Referer' : url,
		'X-CSRF-Token': 'gq+Gnl4JMKKOhALUqNUwZmVBQvEPr7GwB83R26v4SRo=',
		'Cookie': '_gat=1; request_method=GET; _fofa_session=WXprb0hwSjJQOHdSZHd6UDhQazkxdm02TUFqNDVyVGZMKzRmTUJPM2pJYTVhRnNqdDN4K1hmMmhwbVIwSnFRaWtSb0lrbEt1UHVJMkFaTWRyUytlWTJINEV0L0ZTWUVDUDdhSzBJeE4xeis1eUIyY3RCOGNjRlVhZENTaTNxdlNIQW4vVThycmhmOWg3ZXVBRDQ3Mkh0NUtRTFArcTdjUUNqNW9zc1dVUHVUby9pTjlpTWhwM2YrYjBGYUY1UndNbXNzOTk2ZFRrcmYrcWpPR2gremx0RVEwRHU2eld3bTZFemRrRGZOTUUzVmZHaEdaOS95bEYreG55VzVlMEJuRk9QdGVZZ1pTQjl2WGxSUHhyczVFS0lzWExGYldxNFBJRlNJTE1FL3VLa0Y1dVBxa01mNFdqdE9PVWptT2ZBV2ctLWNvSXdsVzJ1SThRVFNHTHI2a0pSV0E9PQ%3D%3D--4e6f0b38ea5068aa7425034c0e7c8992468f996d; _ga=GA1.2.263432433.1418114647',
		}
	while True:
		try:
			if body_content_workflow == 1:
				result = requests.get(url, stream=True, headers=headers, timeout=timeout, proxies=proxies)
				return result
			else:
				result = requests.get(url, headers=headers, timeout=timeout, proxies=proxies)
				return result
		except Exception, e:
			# print 'Exception: %s' % e
			trycnt += 1
			if trycnt >= retrycnt:
				# print 'retry overflow'
				return False

def http_request_post(url, payload, body_content_workflow=0):
	'''
		payload = {'key1': 'value1', 'key2': 'value2'}
	'''
	trycnt = 0
	# cookies = dict(scan_worker='working', cookies_be='wscan.net')
	headers = {
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20',
		'Referer' : url,
		'X-CSRF-Token': 'gq+Gnl4JMKKOhALUqNUwZmVBQvEPr7GwB83R26v4SRo=',
		'Cookie': '_gat=1; request_method=GET; _fofa_session=WXprb0hwSjJQOHdSZHd6UDhQazkxdm02TUFqNDVyVGZMKzRmTUJPM2pJYTVhRnNqdDN4K1hmMmhwbVIwSnFRaWtSb0lrbEt1UHVJMkFaTWRyUytlWTJINEV0L0ZTWUVDUDdhSzBJeE4xeis1eUIyY3RCOGNjRlVhZENTaTNxdlNIQW4vVThycmhmOWg3ZXVBRDQ3Mkh0NUtRTFArcTdjUUNqNW9zc1dVUHVUby9pTjlpTWhwM2YrYjBGYUY1UndNbXNzOTk2ZFRrcmYrcWpPR2gremx0RVEwRHU2eld3bTZFemRrRGZOTUUzVmZHaEdaOS95bEYreG55VzVlMEJuRk9QdGVZZ1pTQjl2WGxSUHhyczVFS0lzWExGYldxNFBJRlNJTE1FL3VLa0Y1dVBxa01mNFdqdE9PVWptT2ZBV2ctLWNvSXdsVzJ1SThRVFNHTHI2a0pSV0E9PQ%3D%3D--4e6f0b38ea5068aa7425034c0e7c8992468f996d; _ga=GA1.2.263432433.1418114647',
		}
	while True:
		try:
			if body_content_workflow == 1:
				result = requests.post(url, data=payload, headers=headers, stream=True, timeout=timeout, proxies=proxies)
				return result
			else:
				result = requests.post(url, data=payload, headers=headers, timeout=timeout, proxies=proxies)
				return result
		except Exception, e:
			# print 'Exception: %s' % e
			trycnt += 1
			if trycnt >= retrycnt:
				# print 'retry overflow'
				return False

def check_website_status(url):
	result = http_request_get(url, body_content_workflow=1)
	if result == False:
		# 服务器宕机或者选项错误
		return {'status': False, 'info': 'server down or options error'}
	elif result.status_code != requests.codes.ok:
		# 返回值不等于200
		result_info = 'status_code: %s != 200' % result.status_code
		return {'status': False, 'info': result_info}
	else:
		# 返回正常
		return {'status': True, 'info': 'response ok'}

def get_partner_domain(domain):

	# 判断传入的值是多域名还是单域名
	query_domain = domain.split(',')
	if len(query_domain) > 1: # 多域名
		# fofa 已经不再对外开放，对外之后再做专版更新
		result['partner'] = {}
		result['status'] = False
		result['info'] = 'fofa is down'
		for domainline in query_domain:
			result['partner'][domainline] = {'domains':[],'ipaddrs':[]}
		return ""
	else: # 单域名

		timeout = 90
		runtime = 3

		if check_website_status('http://fofa.so')['status'] == True:

			# 发起查询请求
			payload = {'taskaction' : 'alldomains', 'domain' : domain}
			content = http_request_post('http://fofa.so/lab/addtask/', payload)
			taskinfo = content.text
			jobId = json.loads(taskinfo)['jobId']
			domian_jobInfo_url = 'http://fofa.so/lab/gettask?jobId=%s&t=%s' % (jobId, int(time.time()))
			partner_domain = []

			while True:
				if timeout >= runtime:
					partner_result = json.loads(http_request_get(domian_jobInfo_url).text)
					if partner_result['finished']:
						partner_domain = partner_result['msgs']
						break
					print 'searched %ss' % runtime
					time.sleep(3)
					runtime += 3
				else:
					print '<<<timeout>>>'
					break

			if len(partner_domain) > 0:
				partner_domain.remove('start dumping...')
				partner_domain.remove('<<<finished>>>')

			if len(partner_domain) > 0:
				partner_domain.append(domain)
				result['partner'] = result.fromkeys(partner_domain)
				for domainline in partner_domain:
					get_sub_domain(domainline)
			else:
				# 没有兄弟域名，直接进入子域名查询
				result['partner'] = {domain:None}
				get_sub_domain(domain)

		else:
			# print 'fofa is down'
			result['partner'] = {domain:None}
			result['status'] = False
			result['info'] = 'fofa is down'
			result['partner'][domain] = {'domains':[],'ipaddrs':[]}
			return ""

def get_sub_domain(domain):
	# print 'start process sub domain: %s' % domain
	# 发起查询请求
	payload = {'utf8' : '✓', 'authenticity_token' : 'MM1wr0PZd4D07r3aavz/CTZ8hx3xMCVl7YW5A9I3ADM=', 'all' : 'true', 'domain' : domain}
	ipsinfo = http_request_post('http://fofa.so/lab/ips', payload).text

	re_ip = re.compile(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])')
	re_domain = re.compile(r'(?<=target\="_blank">).*?(?=</a>)')

	# 加re.S, 匹配带有换行符的数据
	re_ips = re.compile(r'<div class="col-lg-3">\n    </div>\n  </div>\n\n</div>\n\n\n    (.+)<footer >',re.S)
	ips_result = str(re_ips.findall(ipsinfo))

	result['partner'][domain] = {'domains':[],'ipaddrs':[]}

	for ipsline in re_domain.findall(ips_result):
		if re_ip.match(ipsline):
			result['partner'][domain]['ipaddrs'].append(ipsline)
		else:
			ipsline = ipsline.rstrip('.')
			ipsline = ipsline.rstrip(':')
			result['partner'][domain]['domains'].append(ipsline)

def start_fofa_plugin(domain):
	get_partner_domain(domain)
	return result

if __name__ == "__main__":
	if len(sys.argv) == 2:
		print start_fofa_plugin(sys.argv[1])
		sys.exit(0)
	else:
		print ("usage: %s domain" % sys.argv[0])
		sys.exit(-1)


# def get_partner_domain(domain):

# 	url = ''
# 	payload = {'aaaa':'123',}
# 	headers = {'Cookies'}
# 	r = requests.post(url, data=payload, headers=headers)

# 	timeout = 90
# 	runtime = 3








