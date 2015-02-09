#!/usr/bin/env python
# encoding: utf-8
# author: @ringzero
# email: ringzero@0x557.org

'''
	wydomain 定义项
'''

trust_name = ( 'admin', 'adm', 'www', 'mail', 'email', 'webmail', 'exchange', 'bbs', 'forum', 'forums', 'blog', 'home', 'cache', 'chat', 'connect', 'console', 'contact', 'core', 'code', 'conf', 'customer', 'crm', 'oa', 'vpn', 'owa', 'demo', 'dev', 'devel', 'dhcp', 'desktop', 'help', 'helpdesk', 'it', 'dns', 'doc', 'docs', 'en', 'edu', 'fax', 'file', 'firewall', 'ftp', 'fw', 'git', 'game', 'svn', 'gw', 'gateway', 'gate', 'host', 'id', 'ids', 'account', 'im', 'rtx', 'intra', 'internet', 'job', 'jobs', 'lab', 'labs', 'live', 'list', 'local', 'login', 'log', 'logs', 'main', 'manage', 'member', 'members', 'mobile', 'm', 'monitor', 'my', 'new', 'news', 'auth', 'old', 'open', 's', 'search', 'pop3', 'smtp', 'pptp', 'project', 'projects', 'proxy', 'pub', 'public', 'reg', 'remote', 'sslvpn', 'test', 'update', 'user', 'users', 'i', 'u', 'zimbra' )

# 轮训DNS服务器，确保服务可用，以及返回的结果全球化
dns_server = {
	'google' : '8.8.8.8',
	'114' : '114.114.114.144',
	'opendns' : '208.67.222.222',
	'baidudns' : '180.76.76.76',
	'v2ex dns' : '199.91.73.222',
	'dyn dns' : '216.146.35.35',
	'comodo dns' : '8.26.56.26',
	'Neustar dns' : '156.154.70.1',
	'norton dns' : '199.85.126.10',
	'One dns' : '112.124.47.27',
	'opener dns' : '42.120.21.30',
	'alidns' : '223.5.5.5',
	'unioncom' : '123.125.81.6',
	'chinamobile' : '218.30.118.6',
	'10086_Guangdong' : '203.156.201.157',
	'10086_Shanghai' : '211.139.163.6',
	'10086_Beijing' : '211.136.28.228',
	'10000_Guangdong' : '202.96.128.86',
	'10000_Shanghai' : '202.96.199.132',
	'10000_Beijing' : '202.96.0.133',
	'10010_Beijing' : '202.102.227.68',
	'10010_Guangdong' : '210.21.4.130',
	'10010_Shanghai' : '211.95.1.97'
}

mx_whitelist = [
	'qq.com',
	'163.com',
	'googlemail.com',
	'outlook.com',
]

ip_whitelist = [
	'192.168.',
	'10.'
]

dns_whitelist = [
	'dnspod.net',
	'dnsv3.com',
	'dnsv2.com',
	'xinnet.com',
	'hichina.com',
	'360safe.com',
	'iidns.com',
]


