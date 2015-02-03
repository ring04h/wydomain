#!/usr/bin/env python
# encoding: utf-8
# author: @ringzero
# email: ringzero@0x557.org

'''
	返回结果数据结构
	['brute'] 的结果为去除掉CNAME和解析IP去重的结果
	['record'] 的结果为dnsdict6的原生数据
	{'brute': {'drops.wooyun.org.': ['61.155.149.82', '61.155.149.83'],
	  'en.wooyun.org.': ['202.108.5.184', '123.125.23.171'],
	  'job.wooyun.org.': ['222.216.190.67', '61.155.149.83'],
	  'wiki.wooyun.org.': ['61.155.149.82', '61.155.149.83'],
	  'www.wooyun.org.': ['222.216.190.66',
	   '222.216.190.67',
	   '222.216.190.66',
	   '222.216.190.67'],
	  'zone.wooyun.org.': ['222.216.190.67', '222.216.190.66']},
	 'record': [['job.wooyun.org.', '222.216.190.67'],
	  ['job.wooyun.org.', '61.155.149.83'],
	  ['drops.wooyun.org.', '61.155.149.82'],
	  ['drops.wooyun.org.', '61.155.149.83'],
	  ['wiki.wooyun.org.', '61.155.149.82'],
	  ['wiki.wooyun.org.', '61.155.149.83'],
	  ['en.wooyun.org.', '202.108.5.184'],
	  ['en.wooyun.org.', '123.125.23.171'],
	  ['zone.wooyun.org.', '222.216.190.67'],
	  ['zone.wooyun.org.', '222.216.190.66'],
	  ['www.wooyun.org.', '222.216.190.66'],
	  ['www.wooyun.org.', '222.216.190.67'],
	  ['www.wooyun.org.', '222.216.190.66'],
	  ['www.wooyun.org.', '222.216.190.67']]}
'''
import sys
import subprocess
import time
import re
import socket
from dnsfunc import *

domains = {}
sub_domain = {}

# 生成不存在域名的对应数组序列，然后剔除掉一样的泛解析结果 *.domain.com
not_exist_domain = {
	'front_domain': [
		'500accfde65a0c66c2415017ca8104a1',
		'500accfde65a0c66c2415017ca8104a2',
		'500accfde65a0c66c2415017ca8104a3',
		'500accfde65a0c66c2415017ca8104a4',
		'500accfde65a0c66c2415017ca8104a5',
		'500accfde65a0c66c2415017ca8104a6',
		'500accfde65a0c66c2415017ca8104a7',
		'500accfde65a0c66c2415017ca8104a8',
		'500accfde65a0c66c2415017ca8104a9'
		],
	'ipaddress': [
		]
	}

def gender_exist_list(pre_domain):
	for domain in not_exist_domain['front_domain']:
		full_domain = '%s.%s' % (domain, pre_domain)
		resolver_res = get_a_record(full_domain)
		not_exist_domain['ipaddress'].extend(resolver_res['a'])

# 暴力穷举二级域名
def bruteforce_subdomain(domain, dictname='domain_default.csv'):
	
	# 生成不存在域名列表
	gender_exist_list(domain)
	cname_ip_list = list(set(not_exist_domain['ipaddress']))

	try:
		sub_record = []
		cmdline = 'dnsdict6 -4 -t 32 %s %s' % (domain, dictname)
		print '-' * 50
		print '* Starting bruteforce subdomain task'
		print '-' * 50
		print '* running: %s' % cmdline
		print '-' * 50

		run_proc = subprocess.Popen(cmdline,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		(stdoutput,erroutput) = run_proc.communicate()

		re_domain = re.compile(r'.+\=\>.+')
		for domainline in re_domain.findall(stdoutput):
			split_line = domainline.split(' => ')
			if split_line[1] not in cname_ip_list:
				sub_record.append(split_line)

		domains['record'] = sub_record
		for domain in domains['record']:
			sub_domain[domain[0]] = []
		for domain in domains['record']:
			sub_domain[domain[0]].append(domain[1])

		domains['brute'] = sub_domain

		return domains

	except Exception, e:
		return ""

if __name__ == "__main__":
	if len(sys.argv) == 2:
		print bruteforce_subdomain(sys.argv[1])
		sys.exit(0)
	elif len(sys.argv) == 3:
		print bruteforce_subdomain(sys.argv[1],sys.argv[2])
		sys.exit(0)
	else:
		print ("usage: %s wooyun.org domain_large.csv" % sys.argv[0])
		sys.exit(-1)