#!/usr/bin/env python
# encoding: utf-8
# author: @ringzero
# email: ringzero@0x557.org
'''
	传入一个IP，自动返回C段的域名绑定列表
	python wydomian_ip2domain.py 42.62.14.14
'''
import sys
import time
import json
import multiprocessing
from domain_bing import reverse_bing
from domain_aizhan_all import reverse_aizhan

def ip2num(ip):
	ip = [int(x) for x in ip.split('.')]
	return ip[0] << 24 | ip[1] << 16 | ip[2] << 8 | ip[3]

def num2ip(num):
	return '%s.%s.%s.%s' % (
		(num & 0xff000000) >> 24,
		(num & 0x00ff0000) >> 16,
		(num & 0x0000ff00) >> 8,
		num & 0x000000ff
	)
 
def gen_ips(start, end):
	"""生成IP地址"""
	# if num & 0xff 过滤掉 最后一段为 0 的IP
	return [num2ip(num) for num in range(start, end + 1) if num & 0xff]

def ip_check(ip):
	'''检查IP是否合规'''
	q = ip.split('.')
	return len(q) == 4 and len(filter(lambda x: x >= 0 and x <= 255, \
		map(int, filter(lambda x: x.isdigit(), q)))) == 4

def make_ips_c_block(ipaddr):
	'''生成C段IP地址'''
	address = {}
	ipaddr = ipaddr.split('.')
	if len(ipaddr) > 3:
		ipaddr[3] = '0'
		ipaddr = '.'.join(ipaddr)
		address[ipaddr] = gen_ips(ip2num(ipaddr),ip2num(ipaddr) + 254)
		return address
	else:
		return {}

def func(ipaddr):
	reverse_result = {'bing':{},'aizhan':{}}
	# 爱站优先
	print 'aizhan.com => %s' % ipaddr
	aizhan_result = json.loads(reverse_aizhan(ipaddr))
	# print 'aizhan.com %s : %s' % (ipaddr, aizhan_result)
	if len(aizhan_result) >= 50:
		# print '# 域名绑定记录大于50，排除CDN'
		pass
	else:
		reverse_result['aizhan'][ipaddr] = aizhan_result
	print 'bing.com => %s' % ipaddr
	bing_result = json.loads(reverse_bing(ipaddr))
	# print 'bing.com : %s : %s' % (ipaddr, bing_result)
	if len(bing_result) >= 50:
		# print '# 域名绑定记录大于50，排除CDN'
		pass
	else:
		reverse_result['bing'][ipaddr] = bing_result
	return reverse_result

def ip2domain_start(ip_blocks):

	# 只接受/24结尾的IP段，其它抛弃
	if not ip_blocks.endswith('/24'):
		return {}

	# 只接受IP合规校验通过的，其它抛弃
	ip4txt = ip_blocks.split('/')[0] # 处理掉RFC的IP段标准
	if not ip_check(ip4txt):
		return {}

	# ip_blocks = '113.108.16.0/24'
	ip4txt = ip_blocks.split('/')[0] # 处理掉RFC的IP段标准
	ip4txt = ip4txt.split('.')
	ip4txt[-1] = '0'
	ip4txt = '.'.join(ip4txt)

	# 多进程，服务器要是好的话，可以提高，问题是bing.com可能会因为频率过高被封
	pool = multiprocessing.Pool(processes=10)
	reverse_info = {}
	result = []
	ipaddress = make_ips_c_block(ip4txt)[ip4txt]

	print '-' * 50
	print '* Starting [%s] domain reverse task' % ip_blocks
	print '-' * 50

	for i in xrange(len(ipaddress)):
		ipaddr = ipaddress[i]
		reverse_info[ipaddr] = []
		result.append(pool.apply_async(func, (ipaddr, )))

	pool.close()
	pool.join()

	for res in result:
		domains = res.get()
		# 处理aizhan.com的返回结果
		for ipaddr in domains['aizhan'].keys():
			reverse_info[ipaddr].extend(domains['aizhan'][ipaddr].keys())
		# 处理bing.com得返回结果
		for ipaddr in domains['bing'].keys():
			reverse_info[ipaddr].extend(domains['bing'][ipaddr].keys())

	for ipaddr in reverse_info.keys():
		# 如果ip反查结果为空，删除该键值
		if len(reverse_info[ipaddr]) == 0:
			reverse_info.pop(ipaddr)

	return reverse_info

if __name__ == "__main__":
	if len(sys.argv) == 2:
		print ip2domain_start(sys.argv[1])
		sys.exit(0)
	else:
		print ("usage: %s ipaddress" % sys.argv[0])
		sys.exit(-1)





