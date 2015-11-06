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

    SRCDB = "platform_quantitative_data_E3"
    DSTDB = "platform_quantitative_G"

    stringSQL = "SHOW FULL COLUMNS FROM "+SRCDB
    cur.execute(stringSQL)
    arrKeys = []
    for col in cur.fetchall():
        if (col[0] == "id") or (col[0] == "platform_id") or (col[0] == "platform_name"):
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

    for date_index in range(start, len(dates)):
        v = {}
        v['date'] = str(dates[date_index][0])
        stringSQL = "SELECT platform_id,platform_name,"+','.join(arrKeys)+" FROM "+SRCDB+" WHERE `date` = '"+v['date']+"'"
        inlineCur.execute(stringSQL)
        for resList in inlineCur.fetchall():
            i = 0
            for value in resList:
                if (i == 0):
                    v['platform_id'] = str(value)
                elif (i == 1):
                    v['platform_name'] = str(value)
                else:
                    v[arrKeys[i-2]] = float(value)
                i+=1
            kv = {}
            kv['date'] = v['date']
            kv['platform_id'] = v['platform_id']
            kv['platform_name'] = v['platform_name']
            kv['registered_cap'] = v['registered_cap']
            kv['vc_cap_usd'] = v['vc_cap_usd']
            kv['turnover_registered'] = v['turnover_registered']
            A11 = v['weekly_new_investor']
            A12 = v['weekly_total_investor']
            kv['investor'] = 0.3*A11+0.7*A12
            kv['turnover'] = v['weekly_lending']
            A31 = v['weekly_ave_investment']
            A32 = v['weekly_ave_investment_old']
            A33 = v['weekly_ave_investment_per_bid']
            kv['weekly_ave_turnover'] = 0.7*A31+0.3*A32+0*A33
            kv['bidding_activeness'] = v['weekly_ave_bid_close_time']
            kv['investor_HHI'] = v['investor_HHI']
            kv['new_old_investor_ratio'] = v['weekly_ratio_new_old']
            D11 = v['weekly_ave_lending_per_borrower']
            D12 = v['weekly_ave_lending_per_bid']
            kv['weekly_ave_lending_per_borrower'] = 0.8*D11+0.2*D12
            kv['borrower'] = v['weekly_total_borrower']
            D31 = v['top10_ratio_loan']
            D32 = v['top5_ratio_loan']
            D33 = v['borrower_HHI']
            kv['borrow_concentration'] = 0.45*D31+0.45*D32+0.10*D33
            kv['maturity'] = v['not_returned_yet']
            kv['loan_period'] = v['weekly_loan_period']
            kv['outstanding_loan'] = v['outstanding_loan']
            kv['compensation'] = v['compensation']
            kv['provision_of_risk'] = v['provision_of_risk']
            S21 = v['third_entrust']
            S22 = v['technical_security']
            kv['technical_index'] = 0.65*S21+0.35*S22
            kv['third_assurance'] = v['third_assurance']
            kv['financial_transparency'] = v['financial_transparency']
            kv['overdue_transparency'] = v['overdue_transparency']
            kv['borrower_transparency'] = v['borrower_transparency']
            P41 = v['PR_transparency1']
            P42 = v['PR_transparency2']
            kv['PR_transparency'] = 0.9*P41+0.1*P42
            kv['money_growth'] = v['money_growth']
            G21 = v['borrower_growth']
            G22 = v['investor_growth']
            kv['client_growth'] = 0.5*G21+0.5*G22
            I11 = v['top5_ratio_investment']
            I12 = v['top10_ratio_investment']
            kv['investor_concentration'] = 0.5*I11+0.5*I12
            kv['market_share_growth'] = v['market_share_growth']
            kv['ave_annualized_return'] = v['ave_annualized_return']
            kv['turnover_period'] = v['turnover_period']
            kv['debt_transfer'] = v['debt_transfer']
            kv['customer_service'] = v['customer_service']
            kv['real_name'] = v['real_name']
            kv['short_term_debt_ratio'] = v['short_term_debt_ratio']
            kv['cash_flow_in'] = v['cash_flow_in']

            key = ""
            value = ""
            for (_k, _v) in kv.items():
                key = key+"`"+str(_k)+"`,"
                value = value+"'"+str(_v)+"'," 
            stringSQL = "INSERT INTO "+DSTDB+"("+key[:-1]+") VALUES("+value[:-1]+")"
            insertCur.execute(stringSQL)
            conn.commit()
