# -*- coding: utf-8 -*-

import urllib
import urllib2

def http_request(uri, values):
    try:
        data = urllib.urlencode(values)
        req = urllib2.Request(uri + '?' + data)
        response = urllib2.urlopen(req)
        result = response.read()
        return result
    except Exception,e:
        print e
        return ''


HOST = 'http://www.iqianjin.com/'

# plan 整存宝
# loan 零钱通
TYPES_MAP = { 
    'plan' : { 
        'index_page'  : HOST + 'plan/newlists?',
        'detail_page' : HOST + 'plan/',
        'invest_page' : HOST + 'plan/detail/buyRecord?',
    },

    'loan' : {
        'index_page'  : HOST + 'transfer/newlists?',
        'detail_page' : HOST + 'loan/',
        'invest_page' : HOST + 'loan/detail/lendRecord/',
    }
}
