# encoding: utf-8

import os
from tools.skynet import SkynetDomain
from utils.fileutils import FileUtils
from common import read_json

# init path
script_path = os.path.dirname(os.path.abspath(__file__))
result_file = os.path.join(script_path, 'domains.log')

# upload subdomains dict to skynet.
_subdomains = read_json(result_file)
skynet = SkynetDomain()
skynet.bulk_sync(_subdomains)