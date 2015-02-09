#!/usr/bin/env python
# encoding: utf-8
# author: @ringzero
# email: ringzero@0x557.org

import re
import dns.resolver
import dns.reversename
import dns.query
from wydomain_config import *

_res = dns.resolver.Resolver(filename='/etc/resolv.conf', configure=True)
_res.nameservers = ['114.114.114.114', '8.8.8.8']
_res.timeout = 5.0 # 设置超时时间

def check_mx_whitelist(varname):
	for whiteline in mx_whitelist:
		if whiteline in varname:
			return True
	return False

def check_ip_whitelist(varname):
	for whiteline in ip_whitelist:
		if varname.startswith(whiteline):
			return True
	return False

def check_whitelist(varname):
	for whiteline in dns_whitelist:
		if whiteline in varname:
			return True
	return False

def is_zone_transfer_vul(server, domain):
	try:
		zone_res = dns.query.xfr(server, domain)
		zone_res.next()
		return True
	except Exception, e:
		return False

def get_zone_record(server, domain):

	print '* Starting get zone record'
	print '-' * 50

	domains = {}

	zone_transfer_record = {}
	zone_res = dns.query.xfr(server, domain)

	for request in zone_res:
		
		a_record = []
		cname_record = []
		origin = request.origin.to_text()

		for answerline in request.answer:
			if answerline.rdtype == 1: # A
				zone_record = []
				record_split = answerline.to_text().split()
				record_name = "%s.%s" % (record_split[0], origin)
				record_value = record_split[-1]
				zone_record.append(record_name.rstrip('.'))
				zone_record.append(record_value)
				a_record.append(zone_record)
				# print "A: %s.%s => %s" % (zone_record[0], origin, zone_record[-1])
			elif answerline.rdtype == 5: # CNAME
				zone_record = []
				record_split = answerline.to_text().split()
				record_name = "%s.%s" % (record_split[0], origin)
				record_value = "%s.%s" % (record_split[-1], origin)
				zone_record.append(record_name)
				zone_record.append(record_value)
				cname_record.append(zone_record)
				# print "CNAME: %s.%s => %s.%s" % (zone_record[0], origin, zone_record[-1], origin)
			elif answerline.rdtype == 16: # TXT
				# txtbase.TXTBase
				# ANY.SPF.SPF, ANY.TXT.TXT
				print "没有数据场景研究，QQ联系我完善吧"
				pass
			else:
				pass

	domains['a'] = a_record
	domains['cname'] = cname_record

	return domains

def get_a_record(domain):
	a_result = {}
	a_result['cname'] = []
	a_result['a'] = []
	try:
		request = _res.query(domain, 'A')

		for i in request.response.answer:
			for j in i.items:
				if j.rdtype == 5: # CNAME
					a_result['cname'].append(j.to_text().rstrip('.'))
				elif j.rdtype == 1: # A
					a_result['a'].append(j.to_text())
		# domains['a'] = request_record
		return a_result
	except Exception, e:
		return a_result

# 这个函数基本不会用到
def get_cname_record(domain):
	try:
		request = _res.query(domain, 'CNAME')
		request_record = []
		for i in request.response.answer:
			for j in i.items:
				request_record.append(j.to_text())
		# domains['cname'] = request_record
		return request_record
	except Exception, e:
		return None

def get_txt_record(domain):
	# SPF 记录需要递归查询，所以需要申明全局变量
	global spf_request_record
	global spf_ipaddr_record

	spf_request_record = []
	spf_ipaddr_record = []

	txt_record_result = {}

	# 在这里格式化IP，存入全局domain变量中
	get_spf_record(domain)

	txt_record_result['domain'] = spf_request_record
	txt_record_result['ipaddr'] = spf_ipaddr_record

	return txt_record_result

def get_spf_record(domain):
	try:
		request = _res.query(domain, 'TXT')
		for i in request.response.answer:
			for j in i.items:
				txt_result = j.to_text()
				if 'include' in txt_result:
					txtconf = re.findall( r'include:.+ ', txt_result)
					for txtline in txtconf:
						spf = txtline.split()
						for txtspf in spf:
							spfdomain = txtspf.split(':')[1]
							spf_request_record.append(str(spfdomain).rstrip('.'))
							get_spf_record(spfdomain)

				# print 'no spf include, goto process ip4'
				ip4rec = re.findall( r'ip4:.+ ', txt_result)

				for ip4line in ip4rec:
					for txtline in ip4line.split():
						if 'ip4' in txtline:
							ip4txt = txtline.split(':')[1]
							ip4txt = ip4txt.split('/')[0] # 处理掉RFC的IP段标准
							spf_ipaddr_record.append(str(ip4txt))
						else:
							pass
	except Exception, e:
		return None

def get_mx_record(domain):
	domains = {'mx':[]}
	try:
		mx = _res.query(domain, 'MX')
		mx_record = []
		for i in mx.response.answer:
			for j in i.items:
				mx_record.append(j.exchange.to_text().rstrip('.'))
		# MX解析记录写入总域名表
		domains['mx'] = mx_record
		return domains
	except Exception, e:
		return domains

def get_soa_record(domain):
	domains = {'soa':[]}
	try:
		soa = _res.query(domain, 'SOA')
		soa_record = []
		for i in soa.response.answer:
			j = i.to_text().split()
			soa_record.append(j[4].rstrip('.'))
			soa_record.append(j[5].rstrip('.'))
		# SOA解析记录写入总域名表
		domains['soa'] = soa_record
		return domains
	except Exception, e:
		return domains

def get_ns_record(domain):
	domains = {'ns':[]}
	domains['is_zone_vul'] = False
	# print 'process domain ns record: %s' % domain
	try:
		ns = _res.query(domain, 'NS')
		for i in ns.response.answer:
			ns_record = []
			for j in i.items:
				ns_name = j.to_text().rstrip('.')
				if check_whitelist(ns_name):
					print '* %s in whitelist' % ns_name
				else:
					if is_zone_transfer_vul(ns_name, domain):
						print '* %s zone_transfer_vul exist' % ns_name
						print '-' * 50
						if domains['is_zone_vul'] == True:
							# 已经处理过一次域传送漏洞
							pass
						else:
							domains['is_zone_vul'] = True
							domains['zone'] = get_zone_record(ns_name, domain)
					else:
						print '* %s zone_transfer_vul not exist' % ns_name
				ns_record.append(ns_name)
		# NS解析记录写入总域名表
		domains['ns'] = ns_record
		return domains
	except Exception, e:
		# print e
		return domains

# 根据主机名解析IP地址
def getipaddr(hostname):
	trytime = 0
	while True:
		try:
			ipaddr = socket.getaddrinfo(hostname,'http')[0][4][0]
			return ipaddr
		except:
			trytime += 1
			if trytime > 3:
				return ""