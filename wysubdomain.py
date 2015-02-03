#!/usr/bin/env python
# encoding: utf-8
# author: @ringzero
# email: ringzero@0x557.org

'''
	一、先用字典穷举二级域名
		dnsdic.py 模块返回结果
			from dnsdic import bruteforce_subdomain
			brute_record = bruteforce_subdomain('wooyun.org')['record']

		分析处理返回的域名和解析IP结果，格式化后，推入全局wydomains['ipaddress']

	二、用开放的接口查询二级域名
		查询二级域名信息，解析IP结果，格式化后，推入全局wydomains['ipaddress']

	三、暴力穷举的结果没有从API查询的准备，SO，可以覆盖掉暴力的记录
	
'''
import sys
from dnsfunc import *
from mysubdomain import get_subdomain_run
from dnsdic import bruteforce_subdomain

def wy_subdomain_run(domain):
	wydomains = {
		'domain': {
			domain: {},
		},
		'ipaddress': {}
	}

	# 开始暴力穷举二级域名
	brute_record = bruteforce_subdomain(domain)['brute']

	brute_ipaddress = []

	# 分析穷举出来的二级域名和IP，推到wydomains主数据列表
	for subdomain in brute_record.keys():
		# 清除掉末尾的.
		sub_domain = subdomain.rstrip('.')
		# 处理二级子域名
		wydomains['domain'][domain][sub_domain] = {'a':[],'cname':[]}
		# 处理子域名对应的IP
		wydomains['domain'][domain][sub_domain]['a'] = brute_record[subdomain]
		brute_ipaddress.extend(brute_record[subdomain])

	# 分析穷举出来的IP地址，格式化成RFC地址段标准去重
	for ipaddr in list(set(brute_ipaddress)):
		ipaddr = ipaddr.split('.')
		ipaddr[-1] = '0/24'
		ipaddr = '.'.join(ipaddr)
		wydomains['ipaddress'][ipaddr] = {}

	# 开始用开放的接口查询二级域名
	my_subdomains = get_subdomain_run(domain)

	resolv_ipaddress = []

	for subdomain in my_subdomains:
		resolv_domain = get_a_record(subdomain)
		wydomains['domain'][domain][subdomain] = resolv_domain
		if len(resolv_domain['a']) > 0:
			resolv_ipaddress.extend(resolv_domain['a'])

	for ipaddr in list(set(resolv_ipaddress)):
		ipaddr = ipaddr.split('.')
		ipaddr[-1] = '0/24'
		ipaddr = '.'.join(ipaddr)
		wydomains['ipaddress'][ipaddr] = {}

	return wydomains

if __name__ == "__main__":
   if len(sys.argv) == 2:
      print wy_subdomain_run(sys.argv[1])
      sys.exit(0)
   else:
       print ("usage: %s domain" % sys.argv[0])
       sys.exit(-1)
