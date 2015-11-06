#!/usr/bin/python
#coding=utf-8
import math
import numpy as np
from scipy import interpolate
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
from atbtools.header import *


def warning1(temp):
    if len(temp) < 7 or temp[6] == 0:
        return 2
    x = temp[0:6]
    y = np.array(range(0,6))
    y_new = np.array(range(0,7))
#     f_linear = interpolate.interp1d(y,x)
    tck = interpolate.splrep(y,x) #B样条插值函数
    x_bspline = interpolate.splev(y_new,tck) #B样条插值结果
    return abs(float(x_bspline[6]/temp[6])-1)

def warning2(temp):
    def linefit(x,y):
        N = len(x)
        sx,sy,sxx,syy,sxy = 0,0,0,0,0
        for i in range(0,N):
            sx += x[i]
            sy += y[i]
            sxx += x[i]*x[i]
            syy += y[i]*y[i]
            sxy += x[i]*y[i]
        a = (sy*sx/N - sxy)/(sx*sx/N - sxx)
        b = (sy - a*sx)/N
        if (sxx-sx*sx/N)*(syy-sy*sy/N) == 0:
            r = 0
        else:
            r = abs(sy*sx/N - sxy)/math.sqrt((sxx-sx*sx/N)*(syy-sy*sy/N))
        return a,b,r
    if len(temp) < 4 or temp[3] == 0:
        return 2
    r = linefit([1,2,3,4],temp)[2]
    if (abs(r) > 0.85):
        return 1

def warning3(thisweek,lastweek):
    if abs(thisweek - lastweek) > 10:
        return 1

def warning4(value,minn,maxx):
    if (value < minn) or (value > maxx):
        return 1

def warning5(value,minn,maxx):
    if (value < minn) or (value > maxx):
        return 1

def warning6():
        return 0

if __name__ == '__main__':
    conn=MySQLdb.connect(host=DEVHOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT) 
    cur=conn.cursor()
    inlineCur=conn.cursor()
    insertCur=conn.cursor()

    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    SRCDB = "platform_alert_Q1"
    DSTDB = "platform_alert_Q2"

    stringSQL = "SELECT DISTINCT date FROM "+SRCDB+" ORDER BY date ASC"
    cur.execute(stringSQL)
    dates = cur.fetchall()

    start = len(dates)-1
    if (len(sys.argv) == 2):
        if (sys.argv[1] == "reset"):
            start = 0
            cur.execute("TRUNCATE "+DSTDB)
            conn.commit()

    stringSQL = "SHOW FULL COLUMNS FROM "+SRCDB
    cur.execute(stringSQL)
    arrKeys = []
    for col in cur.fetchall():
        if (col[0] == "date") or (col[0] == "id") or (col[0] == "platform_id") or (col[0] == "platform_name"):
            continue
        arrKeys.append(col[0])

    for date_index in range(start, len(dates)):
        kv = {}
        kv['date'] = str(dates[date_index][0])

        for prop in arrKeys:
            stringSQL = "SELECT count(*) FROM "+SRCDB+" WHERE `date` = '"+kv['date']+"' AND `"+prop+"` != '10000'"
            cur.execute(stringSQL)
            count = int(cur.fetchone()[0])

            stringSQL = "SELECT count(*) FROM "+SRCDB+" WHERE `date` = '"+kv['date']+"' AND `"+prop+"` = '10000'"
            cur.execute(stringSQL)
            invalid = int(cur.fetchone()[0])
            pos = count*0.2+invalid

            stringSQL = "SELECT "+prop+" FROM "+SRCDB+" WHERE `date` = '"+kv['date']+"' ORDER BY `"+prop+"` DESC LIMIT "+str(int(pos))+",1"
            ret = cur.execute(stringSQL)
            if (ret != 0):
                value = cur.fetchone()[0]
            else:
                value = 0
            kv[prop] = value

        key = ""
        value = ""
        for (k,v) in kv.items():
            key = key+"`"+k+"`,"
            value = value+"'"+str(v)+"',"

        stringSQL = "INSERT INTO "+DSTDB+"("+key[:-1]+") VALUES("+value[:-1]+")"
        cur.execute(stringSQL)
        conn.commit()
