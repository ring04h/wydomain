#! /usr/bin/env python
#-*- coding: utf-8 -*-
import urllib2
import sys
import re
import HTMLParser
import socket
import cookielib
import math
import json
from StringIO import StringIO
import gzip
import signal
import time

reload(sys)
sys.setdefaultencoding('utf-8')

domains = {}
cj = cookielib.LWPCookieJar()
cookie_support = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
urllib2.install_opener(opener)

class TimeOutException(Exception):
    pass

def timeout(seconds, *args, **kwargs):
    def fn(f):
        def wrapped_fn(*args, **kwargs):
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            f(*args, **kwargs)
        return wrapped_fn
    return fn

def handler(signum, frame):
    pass
    # raise TimeOutException("Timeout")

# http://dns.aizhan.com/index.php?r=index/getress&q=59.32.181.65&page=1
def getHtml(ip,page):
    trytime = 0
    while True:
        try:
           request = urllib2.Request("http://dns.aizhan.com/?q="+ ip +"&page="+ str(page) )
           request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0')
           request.add_header('Accept-encoding', 'gzip')
           request.add_header('X-FORWARDED-FOR', ip)
           request.add_header('Referer', request.get_full_url())
           u = urllib2.urlopen(request , timeout = 30)
           content = ''
           if u.info().get('Content-Encoding') == 'gzip':
              buf = StringIO(u.read())
              f = gzip.GzipFile(fileobj=buf)
              content = f.read()
           else:
              content = u.read()
           type = sys.getfilesystemencoding()
           return content.decode("UTF-8").encode(type)
        except:
            trytime+=1
            if trytime>3:
                return ""         

def getDomains(ip,page):
    global domains
    trytime = 0
    while True:
        try:
           request = urllib2.Request("http://dns.aizhan.com/index.php?r=index/domains&ip="+ ip +"&page="+ str(page) )
           request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0')
           request.add_header('Accept-encoding', 'gzip')
           request.add_header('X-FORWARDED-FOR', ip)
           request.add_header('Referer', request.get_full_url())
           u = urllib2.urlopen(request , timeout = 30)
           content = ''
           if u.info().get('Content-Encoding') == 'gzip':
              buf = StringIO(u.read())
              f = gzip.GzipFile(fileobj=buf)
              content = f.read()
           else:
              content = u.read()
           type = sys.getfilesystemencoding()
           content = content.decode("UTF-8").encode(type)
           domaintemp = json.loads(content,encoding="utf-8")
           for d in domaintemp["domains"]:
                 try:
                     proto, rest = urllib2.splittype("http://"+ str(d))
                     host, rest = urllib2.splithost(rest) 
                     host, port = urllib2.splitport(host)
                     if port == None:
                        port = 80
                     if not domains.has_key(host):
                        domains[host] = port
                 except:
                     pass
           return
        except:
            trytime+=1
            if trytime>0:
                return 

def getIp(domain):
    trytime = 0
    while True:
         try:
            myaddr = socket.getaddrinfo(domain,'http')[0][4][0]
            return myaddr
         except:
            trytime+=1
            if trytime>3:
                return ""

@timeout(10)     
def getHtmlByUrl(url):
    global domains
    try:
           u = urllib2.urlopen(url,timeout = 10.0)
           content = u.read()
           if content !="":
               try:
                  proto, rest = urllib2.splittype(url)
                  host, rest = urllib2.splithost(rest) 
                  host, port = urllib2.splitport(host)
                  domains[host] = int(port)
               except:
                  pass
           return content
    except:
           pass

def reverse_aizhan(arges):
    ipandport = arges
    try :
         info = getHtmlByUrl("http://"+ ipandport)
    except:
         pass
    ip = ipandport.split(':')[0]
    info = getHtml(ip,1)
    if info!="":
        match =re.search(r'<font color="#FF0000" id="yhide">(\d*)</font>',info)
        if match:
            count = int(match.group(1))
            count = int(math.ceil(count / 20.0))
            for i in range(count):
                getDomains(ip,(i+1))
    # print (json.dumps(domains,encoding="utf-8"))
    return (json.dumps(domains,encoding="utf-8"))

if __name__ == "__main__":
   if len(sys.argv) == 2:
       print reverse_aizhan(sys.argv[1])
       sys.exit(0)
   else:
       print ("usage: %s ip" % sys.argv[0])
       sys.exit(-1)
