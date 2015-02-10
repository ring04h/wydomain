# wydomain
目标系统信息收集组件，完全模块化，脚本均可拆可并、可合可分的使用！<br />

运行流程
-----------------------------------
* 利用FOFA插件获取兄弟域名，并透视获取到的子域名相关二级域名、IP信息
* 检查域名和兄弟域名是否存在域传送漏洞,存在就遍历zone记录，将结果集推到wydomians数据组
* 获取可以获取的公开信息 MX、DNS、SOA记录
* 子域名字典暴力穷举域名(60000条字典[domain_default.csv])
* 利用第三方API查询子域名(links、alexa、bing、google、sitedossier、netcraft)
* 逐个域名处理TXT记录, 加入总集合
* 解析获取到的所有子域名，生成IP列表集合，截取成RFC地址C段标准(42.42.42.0/24)
* 利用bing.com、aizhan.com的接口，查询所有C段旁站的绑定情况
* 生成数据可视化报告
* 返回wydomains数据结果

更新信息
-----------------------------------
一、有反馈说卡在子域名暴力穷举上，更新了默认字典的大小，启用大字典方法如下<br />
> mv domain_default.csv domain_default.csv.bak<br />
> mv domain_larger.csv domain_default.csv<br />

二、提升执行速度<br />
wydomain_ip2domain.py 第71行，修改processes=你认为能接受的进程数<br />
> 多进程，服务器要是好的话，可以提高，问题是bing.com可能会因为频率过高被封<br />
> pool = multiprocessing.Pool(processes=10)

BUG反馈
-----------------------------------
> 微博：http://weibo.com/ringzero<br />
> 邮箱：ringzero@0x557.org<br />

新版本结果演示
-----------------------------------
> http://wydomain.wuyun.org/report/result_xiaomi.com,xiaomi.cn,duokan.com.html

扫描结果演示
-----------------------------------
> http://wydomain.wuyun.org/report/result_wooyun.org.html<br />
> http://wydomain.wuyun.org/report/result_yiche.com.html<br />
> http://wydomain.wuyun.org/report/result_ablesky.com.html<br />
    

运行环境
-----------------------------------
* CentOS、Kali Linux、Ubuntu、Debian
* Python 2.7.x
* phantomjs (http://www.phantomjs.org)
* dnsdict6 (https://www.thc.org/thc-ipv6/)

使用方法
-----------------------------------
### 命令行使用
    python wydomain.py wooyun.org
    
    建议后台运行，然后去睡觉，一觉醒来会有新发现！
    nohup python wydomain.py wooyun.org &
### 扫描结果报告
    使用浏览器打开：report/result_wooyun.org.html

CentOS 安装
-----------------------------------
### 安装git & 下载wydomian
    yum -y install git
    git clone https://github.com/ring04h/wydomain.git
### 安装phantomjs
    http://phantomjs.org/download.html
    
    32位系统
    wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.8-linux-i686.tar.bz2
    tar vxf phantomjs-1.9.8-linux-i686.tar.bz2
    yum install openssl-devel freetype-devel fontconfig-devel
    cp ./bin/phantomjs /usr/bin/
    
    64位系统
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

Kali 安装(自带dnsdict6)
-----------------------------------
### 安装git & 下载wydomian
    apt-get install git
    git clone https://github.com/ring04h/wydomain.git
### 安装phantomjs
    http://phantomjs.org/download.html
    
    32位系统
    wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.8-linux-i686.tar.bz2
    tar vxf phantomjs-1.9.8-linux-i686.tar.bz2
    cp ./bin/phantomjs /usr/bin/
    
    64位系统
    wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.8-linux-x86_64.tar.bz2
    tar vxf phantomjs-1.9.8-linux-x86_64.tar.bz2
    cp ./bin/phantomjs /usr/bin/
    
Ubuntu & Debian Linux 安装
-----------------------------------
### 安装git & 下载wydomian
    apt-get install git
    git clone https://github.com/ring04h/wydomain.git
### 安装phantomjs
    http://phantomjs.org/download.html
    
    32位系统
    wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.8-linux-i686.tar.bz2
    tar vxf phantomjs-1.9.8-linux-i686.tar.bz2
    sudo apt-get install libsqlite3-dev libfontconfig1-dev libicu-dev libfreetype6 libssl-dev libpng-dev libjpeg-dev
    cp ./bin/phantomjs /usr/bin/
    
    64位系统
    wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.8-linux-x86_64.tar.bz2
    tar vxf phantomjs-1.9.8-linux-x86_64.tar.bz2
    sudo apt-get install libsqlite3-dev libfontconfig1-dev libicu-dev libfreetype6 libssl-dev libpng-dev libjpeg-dev
    cp ./bin/phantomjs /usr/bin/
    
### 安装dnsdict6
    wget http://www.thc.org/releases/thc-ipv6-2.7.tar.gz
    tar zvxf thc-ipv6-2.7.tar.gz
    cd thc-ipv6-2.7
    sudo apt-get install libpcap-dev libssl-dev
    make
    sudo cp dnsdict6 /usr/bin/

数据结构
-----------------------------------
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
