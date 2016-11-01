# wydomain
To Discover Subdomains Of Your Target Domain

## 使用帮助
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

#### 1.1 实际使用演示
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
