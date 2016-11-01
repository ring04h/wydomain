# wydomain
To Discover Subdomains Of Your Target Domain

## 使用帮助
### 库依赖安装
```
pip install -r requirements.txt	
```

### 使用字典穷举目标的子域名
```
python dnsburte.py -h
usage: dnsburte.py [-h] [-t] [-d] [-f] [-o]

wydomian v 2.0 to bruteforce subdomains of your target domain.

optional arguments:
  -h, --help      show this help message and exit
  -t , --thread   thread count
  -d , --domain   domain name
  -f , --file     subdomains dict file name
  -o , --out      result out file
```
   
### 使用API查询目标的子域名
```
$ python wydomain.py -h
usage: wydomain.py [-h] [-d] [-o]

wydomain v 2.0 to discover subdomains of your target domain.

optional arguments:
  -h, --help      show this help message and exit
  -d , --domain   domain name
  -o , --out      result out file
```

### 结果
domains.log 为最终的子域名结果集合。
