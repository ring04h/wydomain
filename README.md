# wydomain
To Discover Subdomains Of Your Target Domain

## 使用帮助
### 提示
记得每次运行前git pull一下，有空的话都会修bug.   
   
### 库依赖安装
```
$ pip install -r requirements.txt	
```

### 1. 先使用字典穷举目标的子域名
```
$ python dnsburte.py -h
usage: dnsburte.py [-h] [-t] [-d] [-f] [-o]

wydomian v 2.0 to bruteforce subdomains of your target domain.

optional arguments:
  -h, --help      show this help message and exit
  -t , --thread   thread count
  -d , --domain   domain name
  -f , --file     subdomains dict file name
  -o , --out      result out file
```
   
字典说明   
   
* default.csv       
> top 200 子域名字典.   
 
* dnspod.csv   
> dnspod.com 官方提供的top 2000条子域名字典.   
 
* wydomian.csv   
> wyodmian 1.0 的top 3000子域名字典 (非常高效)   
    
* wydomian 1.0 大字典   
> https://github.com/ring04h/wydomain/blob/master/domain_larger.csv 
   
### 1.1 实际使用演示
子域名字典穷举结果保存在 result/aliyun.com 目录下的 dnsburte.json 文件。   
   
```
$ python dnsburte.py -d aliyun.com
2016-11-01 13:01:02,327 [INFO] starting bruteforce threading(16) : aliyun.com
2016-11-01 13:02:15,985 [INFO] dns bruteforce subdomains(51) successfully...
```
   
### 2. 使用API查询目标的子域名
各个API查询的结果保存在 result/aliyun.com 目录下 对应的json文件中。   
   
```
$ python wydomain.py -h
usage: wydomain.py [-h] [-d] [-o]

wydomain v 2.0 to discover subdomains of your target domain.

optional arguments:
  -h, --help      show this help message and exit
  -d , --domain   domain name
  -o , --out      result out file
```

### 3. 查看结果
domains.log 为最终的子域名结果集合。   
   
阿里云 aliyun.com 子域名结果    
https://github.com/ring04h/wydomain/tree/wydomain2/result/aliyun.com    
https://github.com/ring04h/wydomain/blob/wydomain2/domains.log    
   
微博 weibo.com 子域名结果   
https://github.com/ring04h/wydomain/tree/wydomain2/result/weibo.com
https://github.com/ring04h/wydomain/blob/wydomain2/weibo_domains.log   
