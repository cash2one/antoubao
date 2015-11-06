# -*- coding: utf-8 -*-

import os
import sys
import time
import json
from conf import *

try:
    key, id, sid = sys.argv[1].split('_')

    # get detail
    uri = '%s/%s/%s.html' % ( TYPES_MAP[key]['detail_page'], id, sid )
    result = http_request(uri, {})
    
    filename = 'html/' + sys.argv[1]
    F = open(filename, 'w')
    F.write(result)
    F.close()

    # get investor
    invest_map = {'code':1, 'list':[]}
    num = 0
    page = 0
    total = 1
    
    while num < total:
        if key == 'plan':
            uri = TYPES_MAP[key]['invest_page']
            list_values = {
                'pageIndex' : 10 * page,
                'pageSize' : 10,
                'planId' : int(id),
                'sid' : sid }
        else:
            uri = TYPES_MAP[key]['invest_page'] + id + '?'
            list_values = {
                'pageIndex' : 10 * page,
                'pageSize' : 10,
                'sid' : sid }

        result = http_request(uri, list_values)
        if not result:
            break

        root = json.loads(result)

        if not root.has_key('code') or root['code'] != 1:
            continue

        total = root['bean']['total']

        invest_map['code'] = 1
        for item in root['bean']['list']:
            invest_map['list'].append(item)
            num += 1

    filename = 'html/' + sys.argv[1] + '.brec'
    F = open(filename, 'w')
    F.write(json.dumps(invest_map))
    F.close() 

except Exception, e:
    print e
    sys.exit(1)
