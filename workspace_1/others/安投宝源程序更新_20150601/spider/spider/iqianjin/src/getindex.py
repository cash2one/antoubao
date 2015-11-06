# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import shutil
from conf import *


page_list = [0, 1, 2]

if not os.path.isdir('data'):
    os.makedirs('data')

if not os.path.isdir('html'):
    os.makedirs('html')


try:
    for key in TYPES_MAP.keys():
        for page in page_list:
            list_values = {
               'pageIndex' : 10 * page,
               'pageSize' : 10,
            }

            uri = TYPES_MAP[key]['index_page']
            result = http_request(uri, list_values)
            if not result:
                continue
            root = json.loads(result)

            if not root.has_key('code') or root['code'] != 1:
                continue

            for obj in root['bean']['list']:

                # add to id.list
                if key == 'plan':
                    cmd = 'echo plan_%d_%s >> data/id.list.tmp' % ( obj['planId'], obj['sid'] )
                else:
                    cmd = 'echo loan_%d_%s >> data/id.list.tmp' % ( obj['id'], obj['sid'] )
                os.system(cmd)

except Exception, e:
    print e
    sys.exit(1)


