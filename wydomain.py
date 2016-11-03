#!/usr/bin/env python
# encoding: utf-8
# email: ringzero@0x557.org
# weibo: @ringzero

import os
import sys
import json
import argparse
import logging

from common import save_result, read_json
from utils.fileutils import FileUtils

from utils.alexa import Alexa
from utils.threatminer import Threatminer
from utils.threatcrowd import Threatcrowd
from utils.sitedossier import Sitedossier
from utils.netcraft import Netcraft
from utils.ilinks import Ilinks
from utils.chaxunla import Chaxunla
from utils.googlect import TransparencyReport

logging.basicConfig(
    level=logging.INFO, # filename='/tmp/wyproxy.log',
    format='%(asctime)s [%(levelname)s] %(message)s',
)

def run(args):
    domain = args.domain
    outfile = args.out

    if not domain:
        print('usage: wydomain.py -d aliyun.com')
        sys.exit(1)

    # init _cache_path
    script_path = os.path.dirname(os.path.abspath(__file__))
    _cache_path = os.path.join(script_path, 'result/{0}'.format(domain))
    if not os.path.exists(_cache_path):
        os.makedirs(_cache_path, 0777)

    # alexa result json file
    logging.info("starting alexa fetcher...")
    _cache_file = os.path.join(_cache_path, 'alexa.json')
    result = Alexa(domain=domain).run()
    save_result(_cache_file, result)
    logging.info("alexa fetcher subdomains({0}) successfully...".format(len(result)))

    # threatminer result json file
    logging.info("starting threatminer fetcher...")
    _cache_file = os.path.join(_cache_path, 'threatminer.json')
    result = Threatminer(domain=domain).run()
    save_result(_cache_file, result)
    logging.info("threatminer fetcher subdomains({0}) successfully...".format(len(result)))

    # threatcrowd result json file
    logging.info("starting threatcrowd fetcher...")
    _cache_file = os.path.join(_cache_path, 'threatcrowd.json')
    result = Threatcrowd(domain=domain).run()
    save_result(_cache_file, result)
    logging.info("threatcrowd fetcher subdomains({0}) successfully...".format(len(result)))

    # sitedossier result json file
    logging.info("starting sitedossier fetcher...")
    _cache_file = os.path.join(_cache_path, 'sitedossier.json')
    result = Sitedossier(domain=domain).run()
    save_result(_cache_file, result)
    logging.info("sitedossier fetcher subdomains({0}) successfully...".format(len(result)))

    # netcraft result json file
    logging.info("starting netcraft fetcher...")
    _cache_file = os.path.join(_cache_path, 'netcraft.json')
    result = Netcraft(domain=domain).run()
    save_result(_cache_file, result)
    logging.info("netcraft fetcher subdomains({0}) successfully...".format(len(result)))

    # ilinks result json file
    logging.info("starting ilinks fetcher...")
    _cache_file = os.path.join(_cache_path, 'ilinks.json')
    result = Ilinks(domain=domain).run()
    save_result(_cache_file, result)
    logging.info("ilinks fetcher subdomains({0}) successfully...".format(len(result)))

    # chaxunla result json file
    logging.info("starting chaxunla fetcher...")
    _cache_file = os.path.join(_cache_path, 'chaxunla.json')
    result = Chaxunla(domain=domain).run()
    save_result(_cache_file, result)
    logging.info("chaxunla fetcher subdomains({0}) successfully...".format(len(result)))

    # google TransparencyReport result json file
    logging.info("starting google TransparencyReport fetcher...")
    result = TransparencyReport(domain=domain).run()
    _cache_file = os.path.join(_cache_path, 'googlect_subject.json')
    save_result(_cache_file, result.get('subjects'))
    _cache_file = os.path.join(_cache_path, 'googlect_dnsnames.json')
    save_result(_cache_file, result.get('dns_names'))
    logging.info("google TransparencyReport fetcher subdomains({0}) successfully...".format(len(result.get('dns_names'))))

    # Collection API Subdomains
    sub_files = [
        'alexa.json', 
        'chaxunla.json', 
        'ilinks.json', 
        'netcraft.json', 
        'sitedossier.json',
        'threatcrowd.json',
        'threatminer.json']

    # process all cache files
    subdomains = []
    for file in sub_files:
        _cache_file = os.path.join(_cache_path, file)
        json_data = read_json(_cache_file)
        if json_data:
            subdomains.extend(json_data)

    # process openssl x509 dns_names
    _cache_file = os.path.join(_cache_path, 'googlect_dnsnames.json')
    json_data = read_json(_cache_file)
    for sub in json_data:
        if sub.endswith(domain):
            subdomains.append(sub)

    # collection burte force subdomains
    _burte_file = os.path.join(_cache_path, 'dnsburte.json')
    if FileUtils.exists(_burte_file):
        json_data = read_json(_burte_file)
        if json_data:
            subdomains.extend(json_data)

    # save all subdomains to outfile
    subdomains = list(set(subdomains))
    _result_file = os.path.join(script_path, outfile)
    save_result(_result_file, subdomains)
    logging.info("{0} {1} subdomains save to {2}".format(
        domain, len(subdomains), _result_file))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="wydomain v 2.0 to discover subdomains of your target domain.")
    parser.add_argument("-d","--domain",metavar="",
        help="domain name")
    parser.add_argument("-o","--out",metavar="",default="domains.log",
        help="result out file")
    args = parser.parse_args()

    try:
        run(args)
    except KeyboardInterrupt:
        logging.info("Ctrl C - Stopping Client")
        sys.exit(1)
