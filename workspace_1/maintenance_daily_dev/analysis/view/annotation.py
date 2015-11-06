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
from atbtools.header import * 

if __name__ == '__main__':
    sconn=MySQLdb.connect(host=DBHOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    scur=sconn.cursor()
    conn=MySQLdb.connect(host=DEVHOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT) 
    cur=conn.cursor()
    aCur=conn.cursor()
    bCur=conn.cursor()

    scur.execute("SET NAMES 'UTF8'")
    scur.execute("SET CHARACTER SET UTF8")
    scur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")
    
    SUMMARY_DB = "view_summary_condition"
    SCORE_DB = "view_score_condition"

    scoreArr = {}
    arrKeys = []
    stringSQL = "SHOW FULL COLUMNS FROM "+SCORE_DB
    cur.execute(stringSQL)
    for col in cur.fetchall():
        if (col[0] == "id") or (col[0] == "date"):
            continue
        arrKeys.append(col[0])
    stringSQL = "SELECT "+','.join(arrKeys)+" FROM "+SCORE_DB
    cur.execute(stringSQL)
    for col in cur.fetchall():
        for i in range(1, len(col)):
            if col[0] not in scoreArr.keys():
                scoreArr[col[0]] = {}
            scoreArr[col[0]][i-1] = col[i]
    
    summaryArr = {}
    arrKeys = []
    stringSQL = "SHOW FULL COLUMNS FROM "+SUMMARY_DB
    cur.execute(stringSQL)
    for col in cur.fetchall():
        if (col[0] == "id"):
            continue
        arrKeys.append(col[0])
    stringSQL = "SELECT "+','.join(arrKeys)+" FROM "+SUMMARY_DB
    cur.execute(stringSQL)
    for col in cur.fetchall():
        for i in range(1, len(col)):
            if col[0] not in summaryArr.keys():
                summaryArr[col[0]] = {}
            summaryArr[col[0]][arrKeys[i]] = col[i]

    FDB = ["vc_cap_usd", "borrower_transparency", "debt_transfer", "customer_service", "third_entrust", "bill_debt", "car_debt", "small_credit_bid", "big_credit_bid", "house_debt"]

    stringSQL = "SELECT DISTINCT date FROM view_mobile ORDER BY `date` DESC LIMIT 1"
    cur.execute(stringSQL)
    date = str(cur.fetchone()[0])

    stringSQL = "SELECT platform_id,platform_name,level FROM view_mobile WHERE `date` = '"+date+"'"
    cur.execute(stringSQL)
    for platId,platName,level in cur.fetchall():
        if platName == "前海理想":
            platName = "前海理想金融"
        good = 0
        bad = 0
        if (level == "A++"):
            good = 3
            bad = 1
        elif (level == "A+"):
            good = 2
            bad = 2
        elif (level == "A"):
            good = 2
            bad = 2
        elif (level == "B++"):
            good = 2
            bad = 2
        elif (level == "B+"):
            good = 1
            bad = 3
        elif (level == "B"):
            good = 1
            bad = 3
        else:
            good = 1
            bad = 3
        i = 0
        _date = date
        while True:
            _date = str(int(_date)-(i*7*24*3600))
            stringSQL = "SELECT "+','.join(scoreArr.keys())+" FROM platform_quantitative_data_E3 WHERE `platform_id` = '"+platId+"' AND `date` = '"+_date+"'"
            ret = aCur.execute(stringSQL)
            if ret != 0 or _date < "0":
                break
            i+=1

        if ret == 0:
            stringSQL = "UPDATE view_mobile SET `summary` = '' WHERE `platform_id` = '"+platId+"'"
            aCur.execute(stringSQL)
            conn.commit()
            continue

        _list = aCur.fetchone()
        rankArr = {}
        for i in range(0, len(_list)):
            stringSQL = "SELECT count(*) FROM platform_quantitative_data_E3 WHERE `"+scoreArr.keys()[i]+"` >= "+str(_list[i])+" AND `date` = '"+date+"'"
            bCur.execute(stringSQL)
            rankArr[i] = bCur.fetchone()[0]

        goodArr = []
        for i in range(0, good):
            _min = 9999
            _minPos = -1
            for j in range(0, len(rankArr)):
                if _list[j] == 0:
                    continue
                if rankArr[j] < _min and scoreArr.keys()[j] not in goodArr:
                    _min = rankArr[j]
                    _minPos = j
            goodArr.append(scoreArr.keys()[_minPos])

        badArr = []
        for i in range(0, bad):
            _max = 0
            _maxPos = -1
            for j in range(0, len(rankArr)):
                if _list[j] == 0:
                    continue
                if rankArr[j] > _max and scoreArr.keys()[j] not in badArr:
                    _max = rankArr[j]
                    _maxPos = j
            badArr.append(scoreArr.keys()[_maxPos])

        summary = ""
        flag = 0
        for prop in goodArr:
            if prop == 'registered_cap':
                stringSQL = "SELECT "+prop+" FROM "+summaryArr[prop]['prop_table']+" WHERE `platform_name` = '"+platName+"'"
                ret = scur.execute(stringSQL)
                if ret == 0:
                    continue
                value = scur.fetchone()[0]
            else:
                stringSQL = "SELECT "+prop+" FROM "+summaryArr[prop]['prop_table']+" WHERE `platform_name` = '"+platName+"' AND `date` = '"+date+"'"
                ret = aCur.execute(stringSQL)
                if ret == 0:
                    continue
                value = aCur.fetchone()[0]
            for i in range(0, len(scoreArr[prop])):
                if value > scoreArr[prop][i]:
                    if len(goodArr) == 1 and i > 1:
                        continue
                    if summaryArr[prop]["summary"+str(i)] is not None:
                        flag = 1
                        summary += summaryArr[prop]['prop_name']+summaryArr[prop]["summary"+str(i)]+","
                    break

        for prop in badArr:
            if prop == 'registered_cap':
                stringSQL = "SELECT "+prop+" FROM "+summaryArr[prop]['prop_table']+" WHERE `platform_name` = '"+platName+"'"
                ret = scur.execute(stringSQL)
                if ret == 0:
                    continue
                value = scur.fetchone()[0]
            else:
                stringSQL = "SELECT "+prop+" FROM "+summaryArr[prop]['prop_table']+" WHERE `platform_name` = '"+platName+"' AND `date` = '"+date+"'"
                ret = aCur.execute(stringSQL)
                if ret == 0:
                    continue
                value = aCur.fetchone()[0]
            for i in range(0, len(scoreArr[prop])):
                if value > scoreArr[prop][i]:
                    if summaryArr[prop]["summary"+str(i)] is not None:
                        if flag == 1 and i > 2:
                            summary += "但"
                            flag = 2
                        summary += summaryArr[prop]['prop_name']+summaryArr[prop]["summary"+str(i)]+","
                    break

        summary = summary[:-1].replace(',', '，')
        if summary != "":
            summary += '。'

        s = ""
        v = {}
        stringSQL = "SELECT "+','.join(FDB)+" FROM platform_qualitative_F WHERE `platform_name` = '"+platName+"'"
        ret = scur.execute(stringSQL)
        if ret != 0:
            s = "该平台"
            _list = scur.fetchone()
            for i in range(0, len(_list)):
                v[FDB[i]] = _list[i]
            if v['vc_cap_usd'] > 4000:
                s = s + "已获得高额风投,"
            elif v['vc_cap_usd'] <= 4000 and v['vc_cap_usd'] >= 1000:
                s = s + "已获得较大额风投,"
            elif v['vc_cap_usd'] < 1000 and v['vc_cap_usd'] > 100:
                s = s + "已获得风投,"

            if v['borrower_transparency'] < 2:
                s = s + "借款信息披露欠充分,"
            elif v['borrower_transparency'] > 4:
                s = s + "借款信息披露较好,"

            if v['debt_transfer'] == 0:
                s = s + "无债权转让功能,"
            elif v['debt_transfer'] == 1:
                s = s + "允许债权转让,"

            if v['customer_service'] < 2:
                s = s + "客服水平有待提升,"
            elif v['customer_service'] > 4:
                s = s + "客服较专业,"

            if v['third_entrust'] == 0:
                s = s + "无第三方托管,"

            debt_c = 0
            debt_n = "以"
            if v['bill_debt'] == 1:
                debt_c += 1
                debt_n = debt_n + "票据标,"
            if v['car_debt'] == 1:
                debt_c += 1
                debt_n = debt_n + "车抵押标,"
            if v['small_credit_bid'] == 1:
                debt_c += 1
                debt_n = debt_n + "小额信用标,"
            if v['big_credit_bid'] == 1:
                debt_c += 1
                debt_n = debt_n + "大额信用标,"
            if v['house_debt'] == 1:
                debt_c += 1
                debt_n = debt_n + "大额或地产抵押标,"

            if debt_c < 3 and debt_c > 0:
                s = s + debt_n[:-1] + "为主,"
            elif debt_c < 5:
                s = s + "标的种类丰富,"
            else:
                s = s + "标的种类齐全,"

        s = s[:-1].replace(',', '，')
        if s != "":
            s += "。"

        if summary != "" or s != "":
            summary = "平台特征："+summary+s

        stringSQL = "UPDATE view_mobile SET `summary` = '"+summary+"' WHERE `platform_id` = '"+platId+"'"
        cur.execute(stringSQL)
        conn.commit()                
