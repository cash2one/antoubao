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
from header import *

if __name__ == "__main__":
    conn=MySQLdb.connect(host=HOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    cur=conn.cursor()
    inlineCur=conn.cursor()
    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    DB = "platform_quantitative_data_E1"
    DSTDB = "platform_problem_record_Y"

    stringSQL = "SELECT date FROM "+DB+" ORDER BY `date` DESC LIMIT 1"
    cur.execute(stringSQL)
    date = cur.fetchone()[0]

    stringSQL = "SELECT count(*) FROM "+DSTDB+" WHERE `date` = '"+str(date)+"'"
    cur.execute(stringSQL)
    count = cur.fetchone()[0]
    if count != 0:
        print "date is existed!"
        exit(0)

    stringSQL = "SELECT date FROM "+DSTDB+" ORDER BY `date` DESC LIMIT 1"
    cur.execute(stringSQL)
    lastdate = cur.fetchone()[0]

    stringSQL = "SELECT platform_id, platform_name, status, discription FROM "+DSTDB+" WHERE `date` = '"+lastdate+"'"
    cur.execute(stringSQL)
    for platId, platName, status, disc in cur.fetchall():
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `status`, `discription`, `date`) VALUES('"+platId+"', '"+platName+"', '"+str(status)+"', '"+disc+"', '"+str(date)+"')"
        inlineCur.execute(stringSQL)
        conn.commit()
