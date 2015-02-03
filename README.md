# wydomain
目标系统信息收集组件

BUG反馈
-----------------------------------
> 微博：http://weibo.com/ringzero
> 邮箱：ringzero@0x557.org

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
