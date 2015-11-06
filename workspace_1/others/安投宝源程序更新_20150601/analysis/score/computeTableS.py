#!/use/bin/python
#coding=utf-8

import re
import json
import datetime
import time
import sys
import string
from urllib import *
from urllib2 import *
import urllib
import urllib2
import MySQLdb
import random
from header import *

if __name__ == "__main__":
    conn=MySQLdb.connect(host=HOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    cur=conn.cursor()
    inlineCur=conn.cursor()
    insertCur=conn.cursor()
    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    SRCDB = "platform_score_P"
    DSTDB = "platform_score_S"

    kv = {}
    stringSQL = "SELECT DISTINCT date FROM "+SRCDB+" ORDER BY date ASC"
    cur.execute(stringSQL)
    dates = cur.fetchall()
    
    start = len(dates)-1
    if (len(sys.argv) == 2):
        if (sys.argv[1] == "reset"):
            start = 3
            cur.execute("TRUNCATE "+DSTDB)
            conn.commit()
    else:
        cur.execute("DELETE FROM "+DSTDB+" WHERE `date` = '"+str(dates[start][0])+"'")
        conn.commit()

    for date_index in range(start, len(dates)):
        kv = {}
        pro = {}
        kv['date'] = str(dates[date_index][0])

        stringSQL = "SELECT platform_id, platform_name FROM "+SRCDB+" WHERE `date` = '"+kv['date']+"'"
        cur.execute(stringSQL)
        for kv['platform_id'], kv['platform_name'] in cur.fetchall():
            for prop in ["score", "capital_adequacy_ratio", "activeness_credibility", "distribution", "mobility", "security", "pellucidity", "growth", "punishment"]:
                values = []
                i = 0
                while True:
                    if date_index-i < 0 or len(values) == 4:
                        break
                    stringSQL = "SELECT "+prop+" FROM "+SRCDB+" WHERE `platform_id` = '"+kv['platform_id']+"' AND `date` = '"+str(dates[date_index-i][0])+"'"
                    i += 1
                    ret = inlineCur.execute(stringSQL)
                    if ret == 0:
                        continue
                    values.append(inlineCur.fetchone()[0])
                if (len(values) == 1):
                    kv[prop] = values[0]
                elif (len(values) == 2):
                    kv[prop] = values[0]*0.7+values[1]*0.3
                elif (len(values) == 3):
                    kv[prop] = values[0]*0.6+values[1]*0.2+values[2]*0.2
                elif (len(values) == 4):
                    kv[prop] = values[0]*0.4+values[1]*0.3+values[2]*0.2+values[3]*0.1

            _k = ""
            _v = ""
            for (k,v) in kv.items():
                _k = _k+"`"+k+"`,"
                _v = _v+"'"+str(v)+"',"
            stringSQL = "INSERT INTO "+DSTDB+"("+_k[:-1]+") VALUES("+_v[:-1]+")"
            insertCur.execute(stringSQL)
            conn.commit()
