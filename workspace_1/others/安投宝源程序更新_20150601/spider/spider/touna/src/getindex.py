# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import shutil
from conf import *

# 41 旺车贷
# 42 旺漏贷
# 43 旺薪贷
# 44 投投乐
# 45 多多盈
#type_list = [41, 42, 43, 44, 45]
type_list = [-1]
page_list = [0, 1, 2]

list_values = {
    'method' : 'list',
    'borrowType' : -1,
    'keyType' : 0,
    'page' : 0,
    'size' : 10,
    'subtime' : 0,
}

if not os.path.isdir('data'):
    os.makedirs('data')

if not os.path.isdir('html'):
    os.makedirs('html')


try:
    for type in type_list:
        for page in page_list:
            list_values['borrowType'] = type
            list_values['page'] = page
            list_values['subtime'] = int(time.time())

            result = http_request(uri, list_values)
            if not result:
                continue
            root = json.loads(result)

            if not root.has_key('status'):
                continue

            for obj in root['result']['list']:

                # add to id.list
                cmd = 'echo %d >> data/id.list.tmp' % obj['id'] 
                os.system(cmd)

except Exception, e:
    print e
    sys.exit(1)


