# -*- coding: utf-8 -*-

import os
import sys
import json
import shutil
import urllib
import urllib2

PAGESIZE = 50
uri = 'https://www.dianrong.com/mobile/searchLoans'
values = {
    'includeFullyFunded' : 'true',
    'primaryTabShow' : 'true',
    'tabSwitch' : 'false',
    'page' : 0,
    'pageSize' : PAGESIZE,
}

detail_uri = 'https://www.dianrong.com/mobile/loanDetail'
detail_values = {
    'loan_id' : 0,
}

invest_uri = 'https://www.dianrong.com/mobile/getInvestRecords'
invest_values = {
    'loanId' : 0,
    'page'   : 0,
    'pageSize' : 1000,
    'sortBy' : 'buyDate',
    'sortDir' : 'desc',
}

if not os.path.isdir('data'):
    os.makedirs('data')

if not os.path.isdir('html'):
    os.makedirs('html')


total_num = 0
try:
    data = urllib.urlencode(values)
    req = urllib2.Request(uri, data)
    response = urllib2.urlopen(req)
    result = response.read()
    root = json.loads(result)

    total_num = int(root['content']['totalRecords'])
    page_num = total_num / PAGESIZE + 1

    p = 0
    while p < page_num:
        values['page'] = p
        data = urllib.urlencode(values)
        req = urllib2.Request(uri, data)
        response = urllib2.urlopen(req)
        result = response.read()
        root = json.loads(result)
        
        for loan in root['content']['loans']:
            # get detail
            detail_values['loan_id'] = loan['loanGUID']
            data = urllib.urlencode(detail_values)
            req = urllib2.Request(detail_uri, data)
            response = urllib2.urlopen(req)
            result = response.read()
            #detail_root = json.loads(result)

            filename = 'html/' + loan['loanGUID']
            F = open(filename, 'w')
            #F.write(json.dumps(result))
            F.write(result)
            F.close()

            # add to id.list
            cmd = 'echo %s >> data/id.list.tmp' % loan['loanGUID']
            os.system(cmd)

            # get invest info
            invest_values['loanId'] = loan['loanGUID']
            data = urllib.urlencode(invest_values)
            req = urllib2.Request(invest_uri, data)
            response = urllib2.urlopen(req)
            result = response.read()
            #invest_root = json.loads(result)

            filename = 'html/' + loan['loanGUID'] + '.brec'
            F = open(filename, 'w')
            #F.write(json.dumps(result))
            F.write(result)
            F.close()

        p += 1

except:
    sys.exit(1)


