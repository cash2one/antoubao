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
from atbtools.header import *

def cal_change(v1,v2):
    if v2 == 0:
        return None
    else:
        return (v1-v2+0.0)/v2

def cal_change_list(list):
    tmp = []
    for i in range(len(list)-1):
        tmp.append(cal_change(list[i],list[i+1]))
    sum = 0.0
    n = 0
    for i in range(len(tmp)):
        if tmp[i] == None:
            continue
        else:
            sum = sum + tmp[i]
            n = n+1
    if n==0:
        return None
    else:
        return sum/n

if __name__ == "__main__":
    LEVEL=["C", "B", "B+", "B++", "A", "A+", "A++"]
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

    SRCDB = "platform_score_H"
    DSTDB = "platform_score_P"
    E2DB = "platform_quantitative_data_E2"
    FDB = "platform_qualitative_F"
    ZDB = "platform_level_Z"

    arrKeys = []    
    stringSQL = "SHOW FULL COLUMNS FROM "+SRCDB
    cur.execute(stringSQL)
    for col in cur.fetchall():
        if (col[0] == "id") or (col[0] == "date"):
            continue
        arrKeys.append(col[0])
    
    kv = {}
    stringSQL = "SELECT DISTINCT date FROM "+SRCDB+" ORDER BY date ASC"
    cur.execute(stringSQL)
    dates = cur.fetchall()
    
    start = len(dates)-1
    if (len(sys.argv) == 2):
        if (sys.argv[1] == "reset"):
            start = 0
            cur.execute("TRUNCATE "+DSTDB)
            conn.commit()
    else:
        cur.execute("DELETE FROM "+DSTDB+" WHERE `date` = '"+str(dates[start][0])+"'")
        conn.commit()

    w1 = 0.283
    w2 = 0.141
    w3 = 0.232
    w4 = 0.2

    for date_index in range(start, len(dates)):
        kv = {}
        pro = {}
        kv['date'] = str(dates[date_index][0])
        scoreArr = {}
        bscoreArr = {}

        stringSQL = "SELECT "+",".join(arrKeys)+" FROM "+SRCDB+" WHERE `date` = '"+kv['date']+"'"
        cur.execute(stringSQL)
        for _list in cur.fetchall():
            i = 0
            k = ""
            v = ""
            for key in arrKeys:
                kv[arrKeys[i]] = _list[i]
                i+=1

            #凸点惩罚
            w = 0.844
            stringSQL = "SELECT weekly_total_investor, weekly_ratio_new_old, ave_annualized_return, weekly_ave_lending_per_borrower, top5_ratio_loan, top10_ratio_loan, not_returned_yet, weekly_ave_investment FROM "+E2DB+" WHERE `platform_id` = '"+kv['platform_id']+"' AND `date` = '"+kv['date']+"'"
            aCur.execute(stringSQL)
            weekly_total_investor, weekly_ratio_new_old, ave_annualized_return, weekly_ave_lending_per_borrower, top5_ratio_loan, top10_ratio_loan, not_returned_yet, weekly_ave_investment = aCur.fetchone()
            punishment = 0 
            punishment_info = ""
            if (weekly_total_investor < 100):
                kv['capital_adequacy_ratio'] -= 2/w
                kv['activeness_credibility'] -= 2/w
                kv['distribution'] -= 2/w
                kv['mobility'] -= 2/w
                kv['security'] -= 2/w     
                punishment += -2
                punishment_info += "#PU01#"
            if (ave_annualized_return > 23.45):
                kv['capital_adequacy_ratio'] -= 5/w
                kv['activeness_credibility'] -= 5/w
                kv['distribution'] -= 5/w
                kv['mobility'] -= 5/w
                kv['security'] -= 5/w
                punishment += -5
                punishment_info += "#PU021#"
            elif (ave_annualized_return > 18.5):
                kv['capital_adequacy_ratio'] -= 2/w
                kv['activeness_credibility'] -= 2/w
                kv['distribution'] -= 2/w
                kv['mobility'] -= 2/w
                kv['security'] -= 2/w
                punishment += -2
                punishment_info += "#PU022#"
            if (top5_ratio_loan > 0.5):
                kv['capital_adequacy_ratio'] -= 5/w
                kv['activeness_credibility'] -= 5/w
                kv['distribution'] -= 5/w
                kv['mobility'] -= 5/w
                kv['security'] -= 5/w
                punishment += -5
                punishment_info += "#PU041#"
            elif (top5_ratio_loan > 0.3):
                kv['capital_adequacy_ratio'] -= 2/w
                kv['activeness_credibility'] -= 2/w
                kv['distribution'] -= 2/w
                kv['mobility'] -= 2/w
                kv['security'] -= 2/w
                punishment += -2
                punishment_info += "#PU042#"
            if (top10_ratio_loan > 0.5):
                kv['capital_adequacy_ratio'] -= 2/w
                kv['activeness_credibility'] -= 2/w
                kv['distribution'] -= 2/w
                kv['mobility'] -= 2/w
                kv['security'] -= 2/w
                punishment += -2
                punishment_info += "#PU10#"
            if (not_returned_yet < 0.667):
                kv['capital_adequacy_ratio'] -= 5/w
                kv['activeness_credibility'] -= 5/w
                kv['distribution'] -= 5/w
                kv['mobility'] -= 5/w
                kv['security'] -= 5/w
                punishment += -5
                punishment_info += "#PU051#"
            elif (not_returned_yet < 1):
                kv['capital_adequacy_ratio'] -= 3/w
                kv['activeness_credibility'] -= 3/w
                kv['distribution'] -= 3/w
                kv['mobility'] -= 3/w
                kv['security'] -= 3/w
                punishment += -3
                punishment_info += "#PU052#"
            if weekly_ratio_new_old > 5:
                kv['capital_adequacy_ratio'] -= 5/w
                kv['activeness_credibility'] -= 5/w
                kv['distribution'] -= 5/w
                kv['mobility'] -= 5/w
                kv['security'] -= 5/w
                punishment += -5
                punishment_info += "#PU092#"
            elif weekly_ratio_new_old > 1:
                kv['capital_adequacy_ratio'] -= 2/w
                kv['activeness_credibility'] -= 2/w
                kv['distribution'] -= 2/w
                kv['mobility'] -= 2/w
                kv['security'] -= 2/w
                punishment += -2
                punishment_info += "#PU091#"
            stringSQL = "SELECT avg("+E2DB+".weekly_ave_lending_per_borrower), avg("+E2DB+".weekly_ave_investment), avg("+E2DB+".weekly_ratio_new_old) FROM "+E2DB+", platform_score_H WHERE "+E2DB+".platform_id = platform_score_H.platform_id AND platform_score_H.date = '"+kv['date']+"' ORDER BY platform_score_H.score DESC LIMIT 20"
            aCur.execute(stringSQL)
            weekly_ave_lending_per_borrower_top20, weekly_ave_investment_top20, weekly_ratio_new_old_top20 = aCur.fetchone()
            if weekly_ratio_new_old/weekly_ratio_new_old_top20 > 10:
                kv['capital_adequacy_ratio'] -= 5/w
                kv['activeness_credibility'] -= 5/w
                kv['distribution'] -= 5/w
                kv['mobility'] -= 5/w
                kv['security'] -= 5/w
                punishment += -5
                punishment_info += "#PU094#"
            elif weekly_ratio_new_old/weekly_ratio_new_old_top20 > 3:
                kv['capital_adequacy_ratio'] -= 2/w
                kv['activeness_credibility'] -= 2/w
                kv['distribution'] -= 2/w
                kv['mobility'] -= 2/w
                kv['security'] -= 2/w
                punishment += -2
                punishment_info += "#PU093#"
            if (weekly_ave_lending_per_borrower/weekly_ave_lending_per_borrower_top20 > 45):
                kv['capital_adequacy_ratio'] -= 10/w
                kv['activeness_credibility'] -= 10/w
                kv['distribution'] -= 10/w
                kv['mobility'] -= 10/w
                kv['security'] -= 10/w
                punishment += -10
                punishment_info += "#PU032#"
            elif (weekly_ave_lending_per_borrower/weekly_ave_lending_per_borrower_top20 > 18):
                kv['capital_adequacy_ratio'] -= 2/w
                kv['activeness_credibility'] -= 2/w
                kv['distribution'] -= 2/w
                kv['mobility'] -= 2/w
                kv['security'] -= 2/w
                punishment += -2
                punishment_info += "#PU031#"
            if kv['platform_id'] in LEVEL:
                stringSQL = "SELECT third_entrust, real_name, compensation FROM "+ZDB+" WHERE `platform_id` = '"+kv['platform_id']+"'"
                aCur.execute(stringSQL)
                A = aCur.fetchone()
            else:
                stringSQL = "SELECT third_entrust, real_name, compensation FROM "+FDB+" WHERE `platform_id_real` = '"+kv['platform_id']+"'"
                scur.execute(stringSQL)
                A = scur.fetchone()
            if A is None:
                third_entrust, real_name, compensation = [0]*3
            else:            
                third_entrust, real_name, compensation = A[0],A[1],A[2]
            if (third_entrust == 0.5):
                punishment += -0
                punishment_info += "#PU061#"
            elif(third_entrust == 0):
                punishment += -0
                punishment_info += "#PU062#"
            if (real_name < 0.7):
                kv['capital_adequacy_ratio'] -= 2/w
                kv['activeness_credibility'] -= 2/w
                kv['distribution'] -= 2/w
                kv['mobility'] -= 2/w
                kv['security'] -= 2/w
                punishment += -2
                punishment_info += "#PU07#"
            if compensation < 0.5:
                kv['capital_adequacy_ratio'] -= 5/w
                kv['activeness_credibility'] -= 5/w
                kv['distribution'] -= 5/w
                kv['mobility'] -= 5/w
                kv['security'] -= 5/w
                punishment += -5
                punishment_info += "#PU082#"
            elif compensation < 0.8:
                kv['capital_adequacy_ratio'] -= 2/w
                kv['activeness_credibility'] -= 2/w
                kv['distribution'] -= 2/w
                kv['mobility'] -= 2/w
                kv['security'] -= 2/w
                punishment += -2
                punishment_info += "#PU081#"
            if weekly_ave_investment/weekly_ave_investment_top20 > 20:
                kv['capital_adequacy_ratio'] -= 5/w
                kv['activeness_credibility'] -= 5/w
                kv['distribution'] -= 5/w
                kv['mobility'] -= 5/w
                kv['security'] -= 5/w
                punishment += -5
                punishment_info += "#PU111#"
            elif weekly_ave_investment/weekly_ave_investment_top20 > 7:
                kv['capital_adequacy_ratio'] -= 2/w
                kv['activeness_credibility'] -= 2/w
                kv['distribution'] -= 2/w
                kv['mobility'] -= 2/w
                kv['security'] -= 2/w
                punishment += -2
                punishment_info += "#PU112#"
            stringSQL = "SELECT cash_flow_in FROM "+E2DB+" WHERE `platform_id` = '"+kv['platform_id']+"' ORDER BY date DESC LIMIT 4"
            aCur.execute(stringSQL)
            sum_cash_flow_in = 0
            for cash_flow_in in aCur.fetchall():
                sum_cash_flow_in += float(cash_flow_in[0])
            if sum_cash_flow_in < -100000:
                kv['capital_adequacy_ratio'] -= 15/w
                kv['activeness_credibility'] -= 15/w
                kv['distribution'] -= 15/w
                kv['mobility'] -= 15/w
                kv['security'] -= 15/w
                punishment += -15
                punishment_info += "#PU121#"
            elif sum_cash_flow_in < -100000:
                kv['capital_adequacy_ratio'] -= 10/w
                kv['activeness_credibility'] -= 10/w
                kv['distribution'] -= 10/w
                kv['mobility'] -= 10/w
                kv['security'] -= 10/w
                punishment += -10
                punishment_info += "#PU122#"
            elif sum_cash_flow_in < -1:
                kv['capital_adequacy_ratio'] -= 5/w
                kv['activeness_credibility'] -= 5/w
                kv['distribution'] -= 5/w
                kv['mobility'] -= 5/w
                kv['security'] -= 5/w
                punishment += -5
                punishment_info += "#PU123#"
            elif sum_cash_flow_in < -0.5:
                kv['capital_adequacy_ratio'] -= 2/w
                kv['activeness_credibility'] -= 2/w
                kv['distribution'] -= 2/w
                kv['mobility'] -= 2/w
                kv['security'] -= 2/w
                punishment += -2
                punishment_info += "#PU124#"
            nry_list = []
            stringSQL = "SELECT not_returned_yet FROM "+E2DB+" WHERE `platform_id`='"+kv['platform_id']+"' AND `black` NOT LIKE '%#B%' AND `date`<='"+kv['date']+"' ORDER BY `date` DESC LIMIT 5"
            aCur.execute(stringSQL)
            for value in aCur.fetchall():
                nry_list.append(value[0])
            nry_change = cal_change_list(nry_list)
            if nry_change != None and nry_change < 0 and not_returned_yet < 1:
                kv['capital_adequacy_ratio'] -= 10/w
                kv['activeness_credibility'] -= 10/w
                kv['distribution'] -= 10/w
                kv['mobility'] -= 10/w
                kv['security'] -= 10/w
                punishment += -10
                punishment_info += "#TBD#"
            kv['score'] = str(float(kv['score']) + punishment)
            #scoreArr[kv['platform_id']] = float(kv['score'])
            #bscoreArr[kv['platform_id']] = float(kv['score'])
            kv['punishment'] = punishment
            kv['punishment_info'] = punishment_info
            _k = ""
            _v = ""
            for (k,v) in kv.items():
                _k = _k+"`"+k+"`,"
                _v = _v+"'"+str(v)+"',"
            stringSQL = "INSERT INTO "+DSTDB+"("+_k[:-1]+") VALUES("+_v[:-1]+")"
            aCur.execute(stringSQL)
            conn.commit()
