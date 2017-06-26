#!/usr/bin/env python
# encoding: utf-8
# email: ringzero@0x557.org

import time
import re
import os
import sys
import json
import Queue
import random
import logging
import argparse
import threading

import dns.query
import dns.resolver
import dns.rdatatype

from common import save_result
from utils.fileutils import FileUtils

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(message)s',
)

nameservers = [
    '119.29.29.29', '182.254.116.116',
    '8.8.8.8', '8.8.4.4',
    '180.76.76.76',
    '1.2.4.8', '210.2.4.8',
    '101.226.4.6', '218.30.118.6',
    '8.26.56.26', '8.20.247.20'
]

class Domain(object):
    """docstring for Domain base class"""
    def __init__(self, timeout=5):
        self.recursion = {}
        self.resolver = dns.resolver.Resolver()
        if timeout:
            self.resolver.timeout = timeout
            self.resolver.lifetime = timeout

    def get_type_name(self, typeid):
        return dns.rdatatype.to_text(typeid)

    def get_type_id(self, name):
        return dns.rdatatype.from_text(name)

    @staticmethod
    def is_domain(self, domain):
        domain_regex = re.compile(
            r'(?:[A-Z0-9_](?:[A-Z0-9-_]{0,247}[A-Z0-9])?\.)+(?:[A-Z]{2,6}|[A-Z0-9-]{2,}(?<!-))\Z', 
            re.IGNORECASE)
        return True if domain_regex.match(domain) else False

    def is_ipv4(self, address):
        ipv4_regex = re.compile(
            r'(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}',
            re.IGNORECASE)
        return True if ipv4_regex.match(address) else False

    def parser(self, answer):
        """result relationship only two format 

        @domain     domain name
        @address    ip address
        """

        result = {}
        for rrsets in answer.response.answer:
            for item in rrsets.items:
                rdtype = self.get_type_name(item.rdtype)

                if item.rdtype == self.get_type_id('A'):
                    if result.has_key(rdtype):
                        result[rdtype].append(item.address)
                    else:
                        result[rdtype] = [item.address]

                if item.rdtype == self.get_type_id('CNAME'):
                    if result.has_key(rdtype):
                        result[rdtype].append(item.target.to_text())
                    else:
                        result[rdtype] = [item.target.to_text()]

                if item.rdtype == self.get_type_id('MX'):
                    if result.has_key(rdtype):
                        result[rdtype].append(item.exchange.to_text())
                    else:
                        result[rdtype] = [item.exchange.to_text()]

                if item.rdtype == self.get_type_id('NS'):
                    if result.has_key(rdtype):
                        result[rdtype].append(item.target.to_text())
                    else:
                        result[rdtype] = [item.target.to_text()]

                if item.rdtype == self.get_type_id('TXT'):
                    rd_result = item.to_text()
                    if 'include' in rd_result:
                        regex = re.compile(r'(?<=include:).*?(?= )')
                        for record in regex.findall(rd_result):
                            if self.is_domain(record):
                                self.query(record, rdtype)
                    else:
                        regex = re.compile(r'(?<=ip4:).*?(?= |/)')
                        qname = rrsets.name.to_text()
                        self.recursion[qname] = []
                        for record in regex.findall(rd_result):
                            self.recursion[qname].append(record)
                    result[rdtype] = self.recursion
        return result

    def query(self, target, rdtype):
        try:
            self.resolver.nameservers = [random.choice(nameservers),random.choice(nameservers)]
            answer = self.resolver.query(target, rdtype)
            return self.parser(answer)
        except dns.resolver.NoAnswer:
            return None # catch the except, nothing to do
        except dns.resolver.NXDOMAIN:
            return None # catch the except, nothing to do
        except dns.resolver.Timeout:
            # timeout retry
            print(target, rdtype, '<timeout>')
        except Exception, e:
            logging.info(str(e))

    def brute(self, target, ret=False):
        """domain brute force fuzz

        @param target           burte force, domain name arg
        @param ret              return result flag
        """
        try:
            if not ret: # return_flag set false, using dns original query func
                if self.resolver.query(target, 'A'):
                    return True
            else: # return_flag set true
                return self.query(target, 'A')
        except dns.resolver.NoAnswer:
            return False # catch the except, nothing to do
        except dns.resolver.NXDOMAIN:
            return False # catch the except, nothing to do
        except dns.resolver.Timeout:
            return self.burte(target) # timeout retry
        except Exception, e:
            logging.info(str(e))
            return False

    def extensive(self, target):
        (ehost, esets) = ['wyspider{0}.{1}'.format(i, target) for i in range(3)], []
        for host in ehost:
            try:
                record = self.query(host, 'A')
                if record is not None:
                    esets.extend(record['A'])
            except Exception:
                pass
        return esets

class DomainFuzzer(object):
    """docstring for DomainFuzzer with brute force"""
    def __init__(self, target, dict_file='domain.csv', timeout=5):
        self.target = target
        self.dict = FileUtils.getLines(dict_file)
        self.resolver = Domain(timeout=timeout)

    def run(self, thread_cnt=16):
        iqueue, oqueue = Queue.Queue(), Queue.Queue()

        for line in self.dict:
            iqueue.put('.'.join([str(line),str(self.target)]))

        extensive, threads = self.resolver.extensive(self.target), []

        for i in xrange(thread_cnt):
            threads.append(self.bruteWorker(self, iqueue, oqueue, extensive))

        for t in threads: t.start()
        for t in threads: t.join()

        while not oqueue.empty():
            yield oqueue.get()

    class bruteWorker(threading.Thread):
        """domain name brute force threading worker class

        @param dfuzzer      DomainFuzzer base class
        @param iqueue       Subdomain dict Queue()
        @param oqueue       Brutefoce result Queue()
        @param extensive    Doman extensive record sets
        """
        def __init__(self, dfuzzer, iqueue, oqueue, extensive=[]):
            threading.Thread.__init__(self)
            self.queue = iqueue
            self.output = oqueue
            self.dfuzzer = dfuzzer
            self.extensive = extensive

        def run(self):
            try:
                while not self.queue.empty():
                    sub = self.queue.get_nowait()
                    if len(self.extensive) == 0: # not_extensive
                        if self.dfuzzer.resolver.brute(sub):
                            self.output.put(sub)
                    else:
                        rrset = self.dfuzzer.resolver.brute(sub, ret=True)
                        if rrset is not None:
                            for answer in rrset['A']:
                                if answer not in self.extensive:
                                    self.output.put(sub)
            except Exception, e:
                pass

def run(args):
    domain = args.domain
    thread_cnt = int(args.thread)
    timeout = int(args.timeout)
    dict_file = args.file
    outfile = args.out

    if not domain:
        print('usage: dnsburte.py -d aliyun.com')
        sys.exit(1)

    # init _cache_path
    script_path = os.path.dirname(os.path.abspath(__file__))
    _cache_path = os.path.join(script_path, 'result/{0}'.format(domain))
    if not os.path.exists(_cache_path):
        os.makedirs(_cache_path, 0777)

    subdomains = []
    dnsfuzz = DomainFuzzer(target=domain, dict_file=dict_file, timeout=timeout)

    logging.info("starting bruteforce threading({0}) : {1}".format(thread_cnt, domain))
    for subname in dnsfuzz.run(thread_cnt=thread_cnt):
        subdomains.append(subname)

    _cache_file = os.path.join(_cache_path, 'dnsburte.json')
    save_result(_cache_file, subdomains)

    script_path = os.path.dirname(os.path.abspath(__file__))
    _outfile_file = os.path.join(script_path, outfile)
    save_result(_outfile_file, subdomains)    

    logging.info("dns bruteforce subdomains({0}) successfully...".format(len(subdomains)))
    logging.info("result save in : {0}".format(_outfile_file))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="wydomian v 2.0 to bruteforce subdomains of your target domain.")
    parser.add_argument("-t","--thread",metavar="",default=16,
        help="thread count")
    parser.add_argument("-time","--timeout",metavar="",default=5,
        help="query timeout")
    parser.add_argument("-d","--domain",metavar="",
        help="domain name")
    parser.add_argument("-f","--file",metavar="",default="default.csv",
        help="subdomains dict file name")
    parser.add_argument("-o","--out",metavar="",default="bruteforce.log",
        help="result out file")
    args = parser.parse_args()

    try:
        run(args)
    except KeyboardInterrupt:
        logging.info("Ctrl C - Stopping Client")
        sys.exit(1)
