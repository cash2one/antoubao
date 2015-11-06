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
   
    stringSQL = "SELECT date FROM platform_quantitative_dcq_weekly_B ORDER BY `date` DESC LIMIT 1"
    cur.execute(stringSQL)
    date = cur.fetchone()[0]

    d = {}
    d['wdzj_id'] = "platform_quantitative_wdzj_weekly_A"
    d['dcq_id'] = "platform_quantitative_dcq_weekly_B"

    for k,v in d.items():
        stringSQL = "SELECT platform_id, platform_name FROM "+v+" WHERE `date` = '"+str(date)+"'"
        cur.execute(stringSQL)

        for platId, platName in cur.fetchall():
            stringSQL = "SELECT count(*) FROM platform_id_name WHERE `name` = '"+str(platName)+"'"
            inlineCur.execute(stringSQL)
            if (inlineCur.fetchone()[0] == 0):
                stringSQL = "INSERT INTO platform_id_name(`"+k+"`, `name`) VALUES('"+str(platId)+"', '"+str(platName)+"')"
            else:
                stringSQL = "UPDATE platform_id_name SET `"+k+"` = '"+str(platId)+"' WHERE `name` = '"+str(platName)+"'"
            inlineCur.execute(stringSQL)
            conn.commit()

    stringSQL = "SELECT name FROM platform_id_name"
    cur.execute(stringSQL)
    for name in cur.fetchall():
        md5=hashlib.md5(name[0]).hexdigest()
        stringSQL = "UPDATE platform_id_name SET `platform_id` = '"+str(md5)[0:10]+"' WHERE `name` = '"+name[0]+"'"
        inlineCur.execute(stringSQL)
        conn.commit()
