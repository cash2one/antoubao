# -*- coding: utf-8 -*-

import os
import sys
import time
import json
from conf import *

HOST = 'http://www.iqianbang.com'

id = sys.argv[1]

# detail
try:
    uri = '%s/%s.html' % (HOST, id)
    result = http_request(uri, {})
    
    filename = 'html/' + id
    F = open(filename, 'w')
    F.write(result)
    F.close()
except Exception, e:
    print e
    sys.exit(1)

# invest
try:
    arr = id.split('chanpin-')
    if len(arr) <= 1:
        sys.exit(1)

    # get page one ann total page
    uri = '%s/home-invest-investlogajax' % HOST
    params = {
        'id' : arr[1],
        'page' : 1
    }
    result = http_request(uri, params)
    if not result:
        sys.exit(1)

    root = json.loads(result)
    totalpage = int(root['totalpage'])

    # get pages and merge
    i = 2
    while i <= totalpage:
        params['page'] = i
        result = http_request(uri, params)
        if result:
            sub_root = json.loads(result)
            for item in sub_root['list']:
                root['list'].append(item)
        i += 1

    filename = 'html/' + id + '.brec'
    F = open(filename, 'w')
    F.write(json.dumps(root))
    F.close()

except Exception, e:
    print e
    sys.exit(1)

