#! /usr/bin/env python
#-*- coding: utf-8 -*-
#python domain_bing.py 38.105.175.5:80
import urllib2
import sys
import re
import HTMLParser
import socket
import cookielib
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
    # raise TimeOutException("Timeout")
    pass

# http://cn.bing.com/search?q=ip%3a222.73.236.238&first=1&FORM=PERE
def getHtml(ip):
    trytime = 0
    while True:
        try:
           request = urllib2.Request("http://cn.bing.com/search?q=ip%3A"+ ip)
           request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0')
           request.add_header('Accept-Language', 'en-us;q=0.5,en;q=0.3')
           request.add_header('Accept-encoding', 'gzip')
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

def getNextPage(url):
    trytime = 0
    while True:
        try:
            request = urllib2.Request("http://cn.bing.com" + url)
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0')
            request.add_header('Accept-Language', 'en-us;q=0.5,en;q=0.3')
            request.add_header('Referer', request.get_full_url())
            u = urllib2.urlopen(request,timeout = 20)
            content = u.read()
            type = sys.getfilesystemencoding()
            return content.decode("UTF-8").encode(type)
        except:
            trytime+=1
            if trytime>3:
                return ""
            

def getDomains(info):
    global domains
    if info != "":
          match = re.search(r'<ol[^>]*id="b_results">([\s\S]*?)</ol>', info)
          if match :
              info = match.group(1)
              match = re.findall('<a[^>]*href="([^"]*)"[^>]*>', info)
              if len(match) > 0:
                  for a in match:
                      try:
                         proto, rest = urllib2.splittype(a)
                         host, rest = urllib2.splithost(rest) 
                         host, port = urllib2.splitport(host)
                         if port == None:
                             port = 80
                         if not domains.has_key(host):
                            domains[host] = port
                      except:
                         pass

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

def count_is_regular(ipaddr):
    info = getHtml(ipaddr)
    result_count = re.compile(r'(?<=class\="sb_count">).*?(?= results</span>)')
    if len(result_count.findall(info)) > 0:
        count = result_count.findall(info)[0].replace(',','')
        if int(count) >= 3000:
            # print 'result is too big'
            return False
        else:
            return True
    else:
      return True

def reverse_bing(arges):
    ipandport = arges
    try :
        info = getHtmlByUrl("http://"+ ipandport)
    except:
        pass
    ip = ipandport.split(':')[0]
    if count_is_regular(ip):
        info = getHtml(ip)
        if info!="":
            getDomains(info)
            while True:
                match = re.search(r'<ul[^>]*>[\s\S]*?<li><a\s*href="([^"]*)"[^>]*><div\s*class="sw_next">Next</div></a></li></ul>',info)
                if match:
                    h = HTMLParser.HTMLParser()
                    url = h.unescape(match.group(1))
                    info = getNextPage(url)
                    if info != "":
                        getDomains(info)
                    else:
                        break
                else:
                    break
              
        for (k,v) in  domains.items():
            if getIp(k) != ip:
                del domains[k]
        # print (json.dumps(domains,encoding="utf-8"))
        return (json.dumps(domains,encoding="utf-8"))
    else:
      return (json.dumps(domains,encoding="utf-8"))
      pass

if __name__ == "__main__":
   if len(sys.argv) == 2:
      print reverse_bing(sys.argv[1])
      sys.exit(0)
   else:
       print ("usage: %s ip" % sys.argv[0])
       sys.exit(-1)