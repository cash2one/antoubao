# -*- coding: utf-8 -*-

import urllib
import urllib2

def http_request(uri, values):
    try:
        data = urllib.urlencode(values)
        headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36' }
        req = urllib2.Request(uri, data, headers)
        response = urllib2.urlopen(req)
        result = response.read()
        return result
    except Exception,e:
        print e
        return ''

