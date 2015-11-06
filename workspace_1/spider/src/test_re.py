# /usr/bin/python
# encoding=utf8

import time
import random
import urllib2
import urllib
import json
import re


if __name__ == '__main__':
    _start_time = time.time() 
    print re.search(r"FishC", "I love FishC.com")
    request = urllib2.Request('http://www.fish-xxxxx.com')
    try:
        urllib2.urlopen(request)
        print 111
    except urllib2.URLError, e:
        print e.reason
    
    print ""
    print "finished"
    _end_time = time.time()
    print "The whole program costs " + str(_end_time - _start_time) + " seconds."
    