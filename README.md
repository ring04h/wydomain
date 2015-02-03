# wydomain
目标系统信息收集组件，完全模块化，脚本均可拆可并、可合可分的使用！
流程
	0、利用FOFA插件，获取兄弟域名
		* 根域名透视
		* 兄弟域名透视
			用FOR循环便利兄弟域名的节点
			aizhan IP 反查
			bing IP 反查
	1、检查是否存在域传送漏洞
		* 存在
			* 遍历ZONE记录，返回到总域名表
			* 流程结束 exit(0)
		* 不存在
			* 跳转到 step: 2
	2、取得公开记录
		* 获取 NS 记录
		* 获取 MX 记录
		* 获取 SOA 记录
	3、二级域名字典暴力破解
		* 返回
		* 结果剔除与公开记录重合的记录
	4、使用第三方API查询域名的二级域名，并合并去重
	5、过滤掉泛域名解析
		* 方法
			* 利用dns_serverlist里面的NS服务器，逐个解析一个不存在的域名，IP设置黑名单
			* 剔除掉域名解析结果为IP列表里面的结果，保留RANK值高的可信域名
	6、递归获取已有域名的CNAME记录、TXT记录、A记录
		* 返回IP列表

BUG反馈
-----------------------------------
> 微博：http://weibo.com/ringzero<br />
> 邮箱：ringzero@0x557.org<br />

### 运行环境
* CentOS 6.x
* Python 2.7.x
* phantomjs (http://www.phantomjs.org)
* dnsdict6 (https://www.thc.org/thc-ipv6/)

INSTALL
-----------------------------------
### 安装phantomjs
    http://phantomjs.org/download.html
    wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.8-linux-x86_64.tar.bz2
    tar vxf phantomjs-1.9.8-linux-x86_64.tar.bz2
    yum install openssl-devel freetype-devel fontconfig-devel
    cp ./bin/phantomjs /usr/bin/
    
### 安装dnsdict6
    wget http://www.thc.org/releases/thc-ipv6-2.7.tar.gz
    tar zvxf thc-ipv6-2.7.tar.gz
    cd thc-ipv6-2.7
    yum install libpcap-devel openssl-devel
    make
    cp dnsdict6 /usr/bin/

使用方法
-----------------------------------
### 命令行使用
    python wydomain.py wooyun.org
### 扫描结果报告
    使用浏览器打开：report/result_wooyun.org.html
### 返回结果数据结构
    wydomains = {
     'domain': {
          'weibo.com': {
               'm.weibo.com': {},
               'wwww.weibo.com': {},
               'movie.weibo.com': {},
               'data.weibo.com': {},
          },
          'weibo.cn': {
               'www.weibo.cn': {},
               'm.weibo.cn': {},
               'game.weibo.cn': {},
          },
          'sina.com.cn': {
               'news.sina.com.cn': {},
               'blog.sina.com.cn': {},
               'my.sina.com.cn': {},
          },
          'sina.cn' : {
               'www.sina.cn': {},
               'news.sina.cn': {},
          },
     },
     'ipaddress': {
          '42.62.52.0/24': {
               '192.168.1.23': {
                    'www.bizmyth.net': {},
                    'www.189.com': {},
               },
               '192.168.1.58': {
                    'www.xiaomi.com': {},
                    'z.aizhan.com': {},
               },
          },
          '42.62.14.0/24': {
               '192.168.2.23': {
                    'www.aizhan.net': {},
                    'www.wanda.cn': {},
               },
               '192.168.2.22': {
                    'wuyun.org': {},
                    'zone.wooyun.org': {},
               },
          },
     },
     'mx': {
          ‘weibo.com': ['mxbiz2.qq.com', 'mxbiz1.qq.com’],
          ‘weibo.cn': ['mxbiz2.qq.com', 'mxbiz1.qq.com’],
          ’sina.com.cn': ['mxbiz2.qq.com', 'mxbiz1.qq.com’],
          ’sina.cn': ['mxbiz2.qq.com', 'mxbiz1.qq.com’]
     },
     'dns': {
          ‘weibo.com': ['ns1.dnsv2.com', 'ns2.dnsv2.com’],
          ‘weibo.cn': ['ns1.dnsv2.com', 'ns2.dnsv2.com’],
          ’sina.com.cn': ['ns1.dnsv2.com', 'ns2.dnsv2.com’],
          ’sina.cn': ['ns1.dnsv2.com', 'ns2.dnsv2.com’],
     }
     ’soa': {
          ‘weibo.com': ['ns1.dnsv2.com', 'ns2.dnsv2.com’],
          ‘weibo.cn': ['ns1.dnsv2.com', 'ns2.dnsv2.com’],
          ’sina.com.cn': ['ns1.dnsv2.com', 'ns2.dnsv2.com’],
          ’sina.cn': ['ns1.dnsv2.com', 'ns2.dnsv2.com’],          
     }

    }
