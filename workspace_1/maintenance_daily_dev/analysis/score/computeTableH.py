#!/use/bin/python
#coding=utf-8

import re
import json
import datetime
import time
import sys
import string
import urllib
import urllib2
import MySQLdb
from urllib import *
from urllib2 import *
from math import log
from atbtools.header import *

if __name__ == "__main__":
    conn=MySQLdb.connect(host=DEVHOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    cur=conn.cursor()
    inlineCur=conn.cursor()
    insertCur=conn.cursor()
    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    SRCDB = "platform_quantitative_G"
    DSTDB = "platform_score_H"

    stringSQL = "SHOW FULL COLUMNS FROM "+SRCDB
    cur.execute(stringSQL)
    arrKeys = []
    for col in cur.fetchall():
        if (col[0] == "id"):
            continue
        arrKeys.append(col[0])

    stringSQL = "SELECT DISTINCT date FROM "+SRCDB+" ORDER BY date ASC"
    cur.execute(stringSQL)
    dates = cur.fetchall()
    v = {}

    start = len(dates)-1
    if (len(sys.argv) == 2):
        if (sys.argv[1] == "reset"):
            start = 0
            cur.execute("TRUNCATE "+DSTDB)
            conn.commit()
    else:
        cur.execute("DELETE FROM "+DSTDB+" WHERE `date` = '"+str(dates[start][0])+"'")
        conn.commit()

    BLACKLIST = ["快速贷", "金豪利", "每天美贷", "呱呱贷", "米牛网", "658金融网", "橙旗贷"]

    for date_index in range(start, len(dates)):
        v = {}
        v['date'] = str(dates[date_index][0])
        stringSQL = "SELECT "+','.join(arrKeys)+" FROM "+SRCDB+" WHERE `date` = '"+v['date']+"'"
        inlineCur.execute(stringSQL)
        for resList in inlineCur.fetchall():
            i = 0
            for value in resList:
                if (i < 2):
                    v[arrKeys[i]] = str(value)
                else:
                    v[arrKeys[i]] = float(value)
                i+=1
            kv = {}
            kv['date'] = v['date']
            kv['platform_id'] = v['platform_id']
            kv['platform_name'] = v['platform_name']
            if kv['platform_name'] in BLACKLIST:
                continue

            C1 = v['registered_cap'] 
            C2 = v['vc_cap_usd']
            C3 = v['turnover_registered']
            kv['capital_adequacy_ratio'] = 0.15*C1+0.40*C2+0.45*C3
            A1 = v['investor']
            A2 = v['turnover']
            A3 = v['weekly_ave_turnover']
            A4 = v['bidding_activeness']
            A5 = v['investor_HHI']
            A6 = v['new_old_investor_ratio']
            A7 = v['ave_annualized_return']
            A8 = v['turnover_period']
            A9 = v['investor_concentration']
            kv['activeness_credibility'] = 0.375*A1+0.094*A2+0.038*A3+0.05*A4+0*A5+0.063*A6+0*A7+0.28*A8+0.1*A9
            D1 = v['weekly_ave_lending_per_borrower']
            D2 = v['borrower']
            D3 = v['borrow_concentration']
            kv['distribution'] = 0.05*D1+0.35*D2+0.6*D3
            M1 = v['maturity']
            M2 = v['loan_period']
            M3 = v['outstanding_loan']
            M4 = v['short_term_debt_ratio']
            M5 = v['provision_of_risk']
            M6 = v['cash_flow_in']
            kv['mobility'] = 0.35*M1+0.05*M2+0.1*M3+0.25*M4+0.1*M5+0.15*M6
            S1 = v['compensation']
            S2 = v['technical_index']
            S3 = v['third_assurance']
            S4 = v['real_name']
            S5 = v['debt_transfer']
            kv['security'] = 0.2*S1+0.55*S2+0.15*S3+0.05*S4+0.05*S5
            P1 = v['financial_transparency']
            P2 = v['overdue_transparency']
            P3 = v['borrower_transparency']
            P4 = v['PR_transparency']
            P5 = v['customer_service']
            kv['pellucidity'] = 0.2*P1+0.25*P2+0.25*P3+0.2*P4+0.1*P5
            G1 = v['money_growth']
            G2 = v['client_growth']
            G3 = v['market_share_growth']
            kv['growth'] = 0.3*G1+0.4*G2+0.3*G3
            C = kv['capital_adequacy_ratio']
            A = kv['activeness_credibility']
            D = kv['distribution']
            M = kv['mobility']
            S = kv['security']
            P = kv['pellucidity']
            G = kv['growth']
            kv['score'] = 0.098*C+0.241*A+0.161*D+0.247*M+0.074*S+0.098*P+0.08*G

            if kv['platform_name'] == "点融网":
                kv['score'] -= 2.2
            if kv['platform_name'] == "365易贷":
                kv['score'] -= 2
            if kv['platform_name'] == "团贷网":
                kv['score'] -= 3
            if kv['platform_name'] == "安心贷":
                kv['score'] -= 9
            if kv['platform_name'] == "有利网":
                kv['score'] -= 13
            if kv['platform_name'] == "铭胜投资":
                kv['score'] -= 3
            if kv['platform_name'] == "积木盒子":
                kv['score'] += 5
            if kv['platform_name'] == "北城贷":
                kv['score'] -= 6
            if kv['platform_name'] == "铭胜投资":
                kv['score'] -= 5
            if kv['platform_name'] == "365金融":
                kv['score'] -= 5
            if kv['platform_name'] == "德众金融":
                kv['score'] -= 6
            '''
            if kv['platform_name'] == "通融易贷":
                kv['score'] -= 8
            if kv['platform_name'] == "净净贷":
                kv['score'] -= 4
            '''

            key = ""
            value = ""
            for (_k, _v) in kv.items():
                key = key+"`"+str(_k)+"`,"
                value = value+"'"+str(_v)+"'," 
            stringSQL = "INSERT INTO "+DSTDB+"("+key[:-1]+") VALUES("+value[:-1]+")"
            insertCur.execute(stringSQL)
            conn.commit()
