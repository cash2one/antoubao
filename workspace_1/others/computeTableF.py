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

    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    _file = open("platform_FF.csv")

    i = 0
    k = {} 
    while True:
        _line = _file.readline()
        if not _line:
            break
        stringSQL = ""
        if i == 0:
            j = 0
            for _prop in _line.strip().split(','):
                if _prop != "unknown":
                    k[_prop] = j
                j+=1
        else:
            strSQL = ""
            _val = _line.strip().split(',')
            stringSQL = "SELECT count(*) FROM platform_qualitative_F WHERE `platform_name` = '"+_val[k['platform_name']]+"'"
            cur.execute(stringSQL)
            count = int(cur.fetchone()[0])
            if count == 0:
                stringSQL = "INSERT INTO platform_qualitative_F(`platform_name`) VALUES('"+_val[k['platform_name']]+"')"
                cur.execute(stringSQL)
                conn.commit()
            #print _line
            #technical_security = 0
            for (key,value) in k.items():
                if _val[value] == '':
                    continue
                #if key == "website1":
                #    w1 = float(_val[value])
                #elif key == "website2":
                #    technical_security = w1*0.3+float(_val[value])*0.7
                if key == "advanced_repayment":
                    if _val[value] == "全体垫付本息":
                        strSQL = strSQL + "`compensation` = '1',"
                    elif _val[value] == "VIP或部分会员垫付本息" or _val[value] == "垫付全部本金":
                        strSQL = strSQL + "`compensation` = '0.8',"
                    elif _val[value] == "垫付80%-99%本金":
                        strSQL = strSQL + "`compensation` = '0.7',"
                    elif _val[value] == "垫付50%-79%本金":
                        strSQL = strSQL + "`compensation` = '0.5',"
                    elif _val[value] == "其他垫付手段":
                        strSQL = strSQL + "`compensation` = '0.3',"
                    else:
                        strSQL = strSQL + "`compensation` = '0',"
                strSQL = strSQL + "`"+key+"` = '"+str(_val[value]).strip('"')+"',"
            stringSQL = "UPDATE platform_qualitative_F SET "+strSQL[:-1]+" WHERE `platform_name` = '"+_val[k['platform_name']]+"'"
            cur.execute(stringSQL)
            print stringSQL
            conn.commit()
        i+=1
