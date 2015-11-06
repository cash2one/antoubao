# -*- coding: utf-8 -*-

import os
import sys
import time
from conf import *

detail_values = {
    'method' : 'detail',
}

id = int(sys.argv[1])

try:
    # get detail
    detail_values['id'] = id
    detail_values['subtime'] = int(time.time())
    result = http_request(uri, detail_values)
    
    filename = 'html/' + str(id)
    F = open(filename, 'w')
    F.write(result)
    F.close()

except Exception, e:
    print e
    sys.exit(1)
