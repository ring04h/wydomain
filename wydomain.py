#!/usr/bin/env python
# encoding: utf-8
# author: @ringzero
# email: ringzero@0x557.org

'''
	流程
	0、利用FOFA插件，获取兄弟域名
		根域名透视
		兄弟域名透视
			用FOR循环便利兄弟域名的节点
			aizhan IP 反查
			bing IP 反查
	1、检查是否存在域传送漏洞
		存在
			遍历ZONE记录，返回到总域名表
			流程结束 exit(0)
		不存在
			跳转到 step: 2
	2、取得公开记录
		获取 NS 记录
		获取 MX 记录
		获取 SOA 记录
	3、二级域名字典暴力破解
		返回
		结果剔除与公开记录重合的记录
	4、使用第三方API查询域名的二级域名，并合并去重
	5、过滤掉泛域名解析
		方法
			利用dns_serverlist里面的NS服务器，逐个解析一个不存在的域名，IP设置黑名单
			剔除掉域名解析结果为IP列表里面的结果，保留RANK值高的可信域名
	6、递归获取已有域名的CNAME记录、TXT记录、A记录
		返回IP列表

'''
import sys
import subprocess
import time
import re
from dnsfunc import *
from fofaplugin import start_fofa_plugin
from wysubdomain import wy_subdomain_run
from wydomain_ip2domain import ip2domain_start
from split_domain import gender_domian_view

def start_wydomain(domain):
	# 初始化全局数据
	wydomains = {'domain': {},'ipaddress': {}, 'dns': {}, 'mx': {}, 'soa': {}}

	print '-' * 50
	print '* Starting fofa plugin search'
	print '-' * 50
	fofa_result = start_fofa_plugin(domain)

	# 检查是否拥有兄弟域名
	if len(fofa_result['partner']) > 1:
		# 有兄弟域名，进入处理流程
		for pdomain in fofa_result['partner']:
			print '-' * 50
			print '* Starting process [%s] partner domain' % pdomain
			print '-' * 50
			wydomains['domain'][pdomain] = {}
			wydomains['dns'][pdomain] = []
			wydomains['mx'][pdomain] = []
			wydomains['soa'][pdomain] = []
			
			# 开始逐个处理FOFA域名查询的结果信息
			for subdomain in fofa_result['partner'][pdomain]['domains']:
				 wydomains['domain'][pdomain][subdomain] = get_a_record(subdomain)
			for ipaddr in fofa_result['partner'][pdomain]['ipaddrs']:
				ipaddr = ipaddr.split('.')
				ipaddr[-1] = '0/24'
				ipaddr = '.'.join(ipaddr)
				wydomains['ipaddress'][ipaddr] = {}

			# 获取NS记录压入wydomains全局数据中，并检查域名是否存在域传送漏洞
			print '* Starting get ns record'
			print '-' * 50
			ns_result = get_ns_record(pdomain)

			# 判断dns server是否为dns厂商，如果不是，将记录压入全局变量中
			for ns_server in ns_result['ns']:
				if not check_whitelist(ns_server):
					wydomains['dns'][pdomain].append(ns_server)
					wydomains['domain'][pdomain][ns_server] = get_a_record(ns_server)
				else:
					wydomains['dns'][pdomain].append(ns_server)

			# 检查域传送漏洞的状况，并取得对应的记录，存在漏洞，会返回['zone']记录数组
			if ns_result['is_zone_vul'] == True:
				# 存在域传送漏洞，处理ZONE里面的解析数据
				# 处理 A 记录 & CNAME 记录
				for a_record_line in ns_result['zone']['a']:
					subdomain = a_record_line[0]
					wydomains['domain'][pdomain][subdomain] = {'a':[],'cname':[]}

				for cname_record_line in ns_result['zone']['cname']:
					subdomain = cname_record_line[0]
					wydomains['domain'][pdomain][subdomain] = {'a':[],'cname':[]}

				for a_record_line in ns_result['zone']['a']:
					subdomain = a_record_line[0]
					wydomains['domain'][pdomain][subdomain]['a'].append(a_record_line[1])

				for cname_record_line in ns_result['zone']['cname']:
					subdomain = cname_record_line[0]
					subdomain_a_record = get_a_record(subdomain)['a']
					wydomains['domain'][pdomain][subdomain]['a'].extend(subdomain_a_record)
					wydomains['domain'][pdomain][subdomain]['cname'].append(cname_record_line[1])

				# 处理 MX 记录
				mx_server = get_mx_record(pdomain)
				# 检查MX服务器是否为免费的企业邮箱
				for mx_server in mx_server['mx']:
					if not check_mx_whitelist(mx_server):
						wydomains['mx'][pdomain].append(mx_server)
						mx_server_record = get_a_record(mx_server)
						# MX的服务器地址对于一个企业非常重要
						for ipaddr in mx_server_record['a']:
							ipaddr = ipaddr.split('.')
							ipaddr[-1] = '0/24'
							ipaddr = '.'.join(ipaddr)
							wydomains['ipaddress'][ipaddr] = {}
						wydomains['domain'][pdomain][mx_server] = mx_server_record
					else:
						wydomains['mx'][pdomain].append(mx_server)

				# 处理 SOA 记录
				soa_server = get_soa_record(pdomain)
				for soa_server in soa_server['soa']:
					wydomains['soa'][pdomain].append(soa_server)

				# 清洗数据，生成C段IP地址，并用bing、aizhan等接口分析整个C段的旁站信息
				# 生成C段IP地址
				for subdomain in wydomains['domain'][pdomain].keys():
					for ipaddr in wydomains['domain'][pdomain][subdomain]['a']:
						ipaddr = ipaddr.split('.')
						ipaddr[-1] = '0/24'
						ipaddr = '.'.join(ipaddr)
						wydomains['ipaddress'][ipaddr] = {}
				
				# 生成一个子域名的IP地址，继续处理其它域名，获得更多的IP，再统一递归查询
				# # 进入IP地址转换成C段，并查询整个C段IP绑定列表
				# for ip_c_block in wydomains['ipaddress']:
				# 	if not check_ip_whitelist(ip_c_block):
				# 		ip2domain_result = ip2domain_start(ip_c_block)
				# 		for ipaddress in ip2domain_result.keys():
				# 			wydomains['ipaddress'][ip_c_block][ipaddress] = ip2domain_result[ipaddress]

				# 处理完毕，等待数据可视化后处理 wydomains 数组

			# 不存在域传送漏洞，用暴力穷举+第三方API查询的方式做处理
			else:
				print '-' * 50
				# 不存在域传送漏洞，获取可以获取的公开信息 MX、SOA记录
				mx_server = get_mx_record(pdomain)
				# 检查MX服务器是否为免费的企业邮箱
				for mx_server in mx_server['mx']:
					if not check_mx_whitelist(mx_server):
						wydomains['mx'][pdomain].append(mx_server)
						mx_server_record = get_a_record(mx_server)
						# MX的服务器地址对于一个企业非常重要
						for ipaddr in mx_server_record['a']:
							ipaddr = ipaddr.split('.')
							ipaddr[-1] = '0/24'
							ipaddr = '.'.join(ipaddr)
							wydomains['ipaddress'][ipaddr] = {}
						wydomains['domain'][pdomain][mx_server] = mx_server_record
					else:
						wydomains['mx'][pdomain].append(mx_server)

				# 处理SOA记录
				soa_server = get_soa_record(pdomain)
				for soa_server in soa_server['soa']:
					wydomains['soa'][pdomain].append(soa_server)

				# 进入用字典穷举二级域名，用开放的接口查询二级域名流程
				subdomains_result = wy_subdomain_run(pdomain)
				for sub_domain in subdomains_result['domain'][pdomain]:
					wydomains['domain'][pdomain][sub_domain] = subdomains_result['domain'][pdomain][sub_domain]
				for ipaddr in subdomains_result['ipaddress']:
					wydomains['ipaddress'][ipaddr] = {}

				# 获取并处理了传递进来的子域名可得到的信息，全部结束后，统一用bing.com、aizhan.com查询C段IP域名信息

		# 进入IP地址转换成C段，并查询整个C段IP绑定列表
		for ip_c_block in wydomains['ipaddress']:
			if not check_ip_whitelist(ip_c_block):
				ip2domain_result = ip2domain_start(ip_c_block)
				for ipaddress in ip2domain_result.keys():
					wydomains['ipaddress'][ip_c_block][ipaddress] = ip2domain_result[ipaddress]

	else:
		# 没有兄弟域名
		print '* No parent domain'
		print '-' * 50
		wydomains['domain'][domain] = {}
		wydomains['dns'][domain] = []
		wydomains['mx'][domain] = []
		wydomains['soa'][domain] = []
		for domain in fofa_result['partner'].keys():

			# 获取NS记录压入wydomains全局数据中，并检查域名是否存在域传送漏洞
			print '* Starting get ns record'
			print '-' * 50
			ns_result = get_ns_record(domain)

			# 判断dns server是否为dns厂商，如果不是，将记录压入全局变量中
			for ns_server in ns_result['ns']:
				if not check_whitelist(ns_server):
					wydomains['dns'][domain].append(ns_server)
					wydomains['domain'][domain][ns_server] = get_a_record(ns_server)
				else:
					wydomains['dns'][domain].append(ns_server)

			# 检查域传送漏洞的状况，并取得对应的记录，存在漏洞，会返回['zone']记录数组
			if ns_result['is_zone_vul'] == True:
				# 存在域传送漏洞，处理ZONE里面的解析数据
				# 处理 A 记录 & CNAME 记录
				for a_record_line in ns_result['zone']['a']:
					subdomain = a_record_line[0]
					wydomains['domain'][domain][subdomain] = {'a':[],'cname':[]}

				for cname_record_line in ns_result['zone']['cname']:
					subdomain = cname_record_line[0]
					wydomains['domain'][domain][subdomain] = {'a':[],'cname':[]}

				for a_record_line in ns_result['zone']['a']:
					subdomain = a_record_line[0]
					wydomains['domain'][domain][subdomain]['a'].append(a_record_line[1])

				for cname_record_line in ns_result['zone']['cname']:
					subdomain = cname_record_line[0]
					subdomain_a_record = get_a_record(subdomain)['a']
					wydomains['domain'][domain][subdomain]['a'].extend(subdomain_a_record)
					wydomains['domain'][domain][subdomain]['cname'].append(cname_record_line[1])

				# 处理 MX 记录
				mx_server = get_mx_record(domain)
				# 检查MX服务器是否为免费的企业邮箱
				for mx_server in mx_server['mx']:
					if not check_mx_whitelist(mx_server):
						wydomains['mx'][domain].append(mx_server)
						mx_server_record = get_a_record(mx_server)
						# MX的服务器地址对于一个企业非常重要
						for ipaddr in mx_server_record['a']:
							ipaddr = ipaddr.split('.')
							ipaddr[-1] = '0/24'
							ipaddr = '.'.join(ipaddr)
							wydomains['ipaddress'][ipaddr] = {}
						wydomains['domain'][domain][mx_server] = mx_server_record
					else:
						wydomains['mx'][domain].append(mx_server)

				# 处理 SOA 记录
				soa_server = get_soa_record(domain)
				for soa_server in soa_server['soa']:
					wydomains['soa'][domain].append(soa_server)

				# 清洗数据，生成C段IP地址，并用bing、aizhan等接口分析整个C段的旁站信息
				# 生成C段IP地址
				for subdomain in wydomains['domain'][domain].keys():
					for ipaddr in wydomains['domain'][domain][subdomain]['a']:
						ipaddr = ipaddr.split('.')
						ipaddr[-1] = '0/24'
						ipaddr = '.'.join(ipaddr)
						wydomains['ipaddress'][ipaddr] = {}

				# 进入IP地址转换成C段，并查询整个C段IP绑定列表
				for ip_c_block in wydomains['ipaddress']:
					# 检查IP是否是内网IP，如果是，别查询了
					if not check_ip_whitelist(ip_c_block):
						ip2domain_result = ip2domain_start(ip_c_block)
						for ipaddress in ip2domain_result.keys():
							wydomains['ipaddress'][ip_c_block][ipaddress] = ip2domain_result[ipaddress]

				# 处理完毕，等待数据可视化后处理 wydomains 数组

			# 不存在域传送漏洞，用暴力穷举+第三方API查询的方式做处理
			else:
				print '-' * 50
				# 不存在域传送漏洞，获取可以获取的公开信息 MX、SOA记录
				mx_server = get_mx_record(domain)
				# 检查MX服务器是否为免费的企业邮箱
				for mx_server in mx_server['mx']:
					if not check_mx_whitelist(mx_server):
						wydomains['mx'][domain].append(mx_server)
						mx_server_record = get_a_record(mx_server)
						# MX的服务器地址对于一个企业非常重要
						for ipaddr in mx_server_record['a']:
							ipaddr = ipaddr.split('.')
							ipaddr[-1] = '0/24'
							ipaddr = '.'.join(ipaddr)
							wydomains['ipaddress'][ipaddr] = {}
						wydomains['domain'][domain][mx_server] = mx_server_record
					else:
						wydomains['mx'][domain].append(mx_server)

				# 处理SOA记录
				soa_server = get_soa_record(domain)
				for soa_server in soa_server['soa']:
					wydomains['soa'][domain].append(soa_server)

				# 进入用字典穷举二级域名，用开放的接口查询二级域名流程
				subdomains_result = wy_subdomain_run(domain)
				for sub_domain in subdomains_result['domain'][domain]:
					wydomains['domain'][domain][sub_domain] = subdomains_result['domain'][domain][sub_domain]
				for ipaddr in subdomains_result['ipaddress']:
					wydomains['ipaddress'][ipaddr] = {}

				# 进入IP地址转换成C段，并查询整个C段IP绑定列表
				for ip_c_block in wydomains['ipaddress']:
					# 检查IP是否是内网IP，如果是，别查询了
					if not check_ip_whitelist(ip_c_block):
						ip2domain_result = ip2domain_start(ip_c_block)
						for ipaddress in ip2domain_result.keys():
							wydomains['ipaddress'][ip_c_block][ipaddress] = ip2domain_result[ipaddress]

	# 生成数据时，将MX、NS、SOA项去重
	for mx_domain in wydomains['mx'].keys():
		wydomains['mx'][mx_domain] = list(set(wydomains['mx'][mx_domain]))
	for dns_domain in wydomains['dns'].keys():
		wydomains['dns'][dns_domain] = list(set(wydomains['dns'][dns_domain]))
	for soa_domain in wydomains['soa'].keys():
		wydomains['soa'][soa_domain] = list(set(wydomains['soa'][soa_domain]))

	# 生成数据可视化页面
	html_content = gender_domian_view(wydomains)
	filepath = './report/result_%s.html' % domain
	try:
		file_object = open(filepath, 'w')
		file_object.writelines(html_content)
		file_object.close()
	except Exception, e:
		return "error"
	finally:
		print '-' * 50
		print "* Report is generated"
		print '-' * 50
		# file_object.close()

	return wydomains

if __name__ == "__main__":
	if len(sys.argv) == 2:
		print start_wydomain(sys.argv[1])
		sys.exit(0)
	else:
		print ("usage: %s domain" % sys.argv[0])
		sys.exit(-1)


