#!/usr/bin/python
#coding=utf-8
import math
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

if __name__ == '__main__':
    sconn=MySQLdb.connect(host="db-x1.antoubao.cn", user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    scur=sconn.cursor()
    conn=MySQLdb.connect(host=HOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT) 
    cur=conn.cursor()
    aCur=conn.cursor()

    scur.execute("SET NAMES 'UTF8'")
    scur.execute("SET CHARACTER SET UTF8")
    scur.execute("SET CHARACTER_SET_RESULTS=UTF8")
    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    stringSQL = "SELECT date FROM view_mobile ORDER BY `date` LIMIT 1"
    cur.execute(stringSQL)
    date = cur.fetchone()[0]

    descArr = {}
    statusArr = {}
    stringSQL = "SELECT platform_id, description, status FROM platform_problem_record_Y ORDER BY `date` DESC"
    scur.execute(stringSQL)
    platList = scur.fetchall()
    for platId, desc, status in platList:
        if platId in statusArr:
            continue
        descArr[platId] = desc
        statusArr[platId] = status

    stringSQL = "SELECT platform_id, summary FROM view_mobile"
    cur.execute(stringSQL)
    for platId, summary in cur.fetchall():
        if platId not in statusArr:
            continue
        status = statusArr[platId]
        if status == 0:
            summary = descArr[platId]
        elif status < 0.31 and status > 0.29:
            summary = descArr[platId]
        elif status < 0.61 and status > 0.59:
            summary = descArr[platId]+"\n"+summary
        elif status < 0.91 and status > 0.89:
            summary = descArr[platId]+"\n"+summary
        else:
            continue
        stringSQL = "UPDATE view_mobile SET `summary` = '"+summary+"', `status` = '"+str(statusArr[platId])+"' WHERE `platform_id` = '"+platId+"'"
        aCur.execute(stringSQL)
        conn.commit() 
