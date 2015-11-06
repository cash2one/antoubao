# -*- coding: utf-8 -*-

import os
import sys 
import json
import shutil
import urllib
import urllib2

def http_request(uri, values):
    try:
        data = urllib.urlencode(values)
        req = urllib2.Request(uri, data)
        response = urllib2.urlopen(req)
        result = response.read()
        return result
    except Exception,e:
        print e
        return ''

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


try:
    id = int(sys.argv[1])

    # get detail
    detail_values['loan_id'] = id
    result = http_request(detail_uri, detail_values)

    filename = 'html/' + str(id)
    F = open(filename, 'w')
    F.write(result)
    F.close()

    # get invest info
    invest_values['loanId'] = id
    result = http_request(invest_uri, invest_values)

    filename = 'html/' + str(id) + '.brec'
    F = open(filename, 'w')
    F.write(result)
    F.close()

except Exception, e:
    print e
    sys.exit(1)

