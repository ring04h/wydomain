#!/usr/bin/env python
# encoding: utf-8

def gender_domian_view(wydomains):
	html_contend = '''
	<!DOCTYPE html>
	<HTML>
	<HEAD>
		<TITLE> Domain View </TITLE>
		<meta http-equiv="content-type" content="text/html; charset=UTF-8">
		<link rel="stylesheet" href="./css/zTreeStyle/zTreeStyle.css" type="text/css">
		<script type="text/javascript" src="./js/jquery-1.4.4.min.js"></script>
		<script type="text/javascript" src="./js/jquery.ztree.core-3.5.js"></script>
		<SCRIPT type="text/javascript">
			<!--
			var setting = {
				view: {
					showIcon: showIconForTree,
					showLine: true,
					txtSelectedEnable: true,
				},
				data: {
					simpleData: {
						enable: true
					}
				}
			};
	'''
	pid = 1
	did = 1
	html_contend = html_contend + 'var zNodes =['
	html_contend = html_contend + '{ id:"1", pId:"0", name:"Domains", open:true,},'
	for domain in wydomains['domain'].keys():
		sid = str(did) + '-1'
		html_contend = html_contend + '{ id:"%s", pId:"%s", name:"%s", open:true,},' % (sid, pid, domain)
		for subdomain in wydomains['domain'][domain].keys():
			did += 1
			mid = str(pid) + '-' + str(did)
			html_contend = html_contend + '{ id:"%s", pId:"%s", name:"%s"},' % (mid, sid, subdomain)
			if len(wydomains['domain'][domain][subdomain]['a']) > 0:
				a_id = mid + '-1'
				html_contend = html_contend + '{ id:"%s", pId:"%s", name:"A"},' % (a_id, mid)
				i = 0
				for a_ipaddr in wydomains['domain'][domain][subdomain]['a']:
					i += 1
					aa_id = a_id + '-' + str(i)
					html_contend = html_contend + '{ id:"%s", pId:"%s", name:"%s"},' % (aa_id, a_id, a_ipaddr)
			if len(wydomains['domain'][domain][subdomain]['cname']) > 0:
				cname_id = mid + '-2'
				html_contend = html_contend + '{ id:"%s", pId:"%s", name:"CNAME"},' % (cname_id, mid)
				i = 0
				for c_cname in wydomains['domain'][domain][subdomain]['cname']:
					i += 1
					ccname_id = cname_id + '-' + str(i)
					html_contend = html_contend + '{ id:"%s", pId:"%s", name:"%s"},' % (ccname_id, cname_id, c_cname)

	html_contend = html_contend + '{ id:"2", pId:"0", name:"IPAddress", open:true,},'
	iid = 0
	for c_block_rfc in wydomains['ipaddress'].keys():
		iid += 1
		i_id = '2-' + str(iid)
		html_contend = html_contend + '{ id:"%s", pId:"2", name:"%s"},' % (i_id, c_block_rfc)
		i = 0
		for ipaddress in wydomains['ipaddress'][c_block_rfc].keys():
			i += 1
			ip_id = i_id + '-' + str(i)
			html_contend = html_contend + '{ id:"%s", pId:"%s", name:"%s"},' % (ip_id, i_id, ipaddress)
			di = 0
			for ip_domains in wydomains['ipaddress'][c_block_rfc][ipaddress]:
				di += 1
				dm_id = ip_id + '-' + str(i)
				html_contend = html_contend + '{ id:"%s", pId:"%s", name:"%s"},' % (dm_id, ip_id, ip_domains)

	html_contend = html_contend + '{ id:"3", pId:"0", name:"DNS", open:true,},'
	fid = 0
	for domain in wydomains['dns'].keys():
		fid += 1
		fpid = '3-' + str(fid)
		html_contend = html_contend + '{ id:"%s", pId:"3", name:"%s"},' % (fpid, domain)
		sid = 0
		for ns_server in wydomains['dns'][domain]:
			sid += 1
			spid = fpid + '-' + str(sid)
			html_contend = html_contend + '{ id:"%s", pId:"%s", name:"%s"},' % (spid, fpid, ns_server)

	html_contend = html_contend + '{ id:"4", pId:"0", name:"MX", open:true,},'
	fid = 0
	for mxdomain in wydomains['mx'].keys():
		fid += 1
		fpid = '4-' + str(fid)
		html_contend = html_contend + '{ id:"%s", pId:"4", name:"%s"},' % (fpid, mxdomain)
		sid = 0
		for mx_server in wydomains['mx'][mxdomain]:
			sid += 1
			spid = fpid + '-' + str(sid)
			html_contend = html_contend + '{ id:"%s", pId:"%s", name:"%s"},' % (spid, fpid, mx_server)

	html_contend = html_contend + '{ id:"5", pId:"0", name:"SOA", open:true,},'
	fid = 0
	for soadomain in wydomains['soa'].keys():
		fid += 1
		fpid = '5-' + str(fid)
		html_contend = html_contend + '{ id:"%s", pId:"5", name:"%s"},' % (fpid, soadomain)
		sid = 0
		for soa_server in wydomains['soa'][soadomain]:
			sid += 1
			spid = fpid + '-' + str(sid)
			html_contend = html_contend + '{ id:"%s", pId:"%s", name:"%s"},' % (spid, fpid, soa_server)

	html_contend = html_contend + '];'

	html_contend = html_contend + '''
	function showIconForTree(treeId, treeNode) {
				return !treeNode.isParent;
			};

			$(document).ready(function(){
				$.fn.zTree.init($("#treeDemo"), setting, zNodes);
			});
			//-->
		</SCRIPT>

	</HEAD>

	<BODY>
	<div>
		<div>
			<ul id="treeDemo" class="ztree"></ul>
		</div>
	</div>
	</BODY>
	</HTML>
	'''

	return html_contend