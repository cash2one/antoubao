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

	
	#随机函数
def r1():
    return 1.02+((random.random()-0.5)**3)%0.03 #结果在[1.02, 1.05]

def r2():
    return 0.96+((random.random()-0.5)**3)%0.02 #结果在[0.96, 0.98]
	
	#双源查找函数，如果a、b中有零，则把零换成另外一个数，否则返回自身
def checkzero(a,b):
    if a == 0:
        return b,b
    if b == 0:
        return a,a
    return a,b

if __name__ == "__main__":
    conn=MySQLdb.connect(host=HOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    aCur=conn.cursor()
    bCur=conn.cursor()    
    cCur=conn.cursor()

    aCur.execute("SET NAMES 'UTF8'")
    aCur.execute("SET CHARACTER SET UTF8")
    aCur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    TableB = "platform_quantitative_dcq_weekly_B"
    TableA = "platform_quantitative_wdzj_weekly_A"
    TableF = "platform_qualitative_F"
    DSTDB = "platform_quantitative_data_E1"

    arrKeys = {}
    arrKeys[TableF] = ["PR_transparency1", "PR_transparency2", "third_assurance", "customer_service", "technical_security", "third_entrust", "compensation", "overdue_transparency", "financial_transparency", "borrower_transparency", "registered_cap", "parent_company_cap", "vc_cap_usd", "provision_of_risk1", "provision_of_risk2", "real_name", "debt_transfer"]
    for table in [TableA, TableB]:
        arrKeys[table] = []
        stringSQL = "SHOW FULL COLUMNS FROM "+table
        aCur.execute(stringSQL)
        for col in aCur.fetchall():
            if (col[0] == "id") or (col[0] == "platform_id") or (col[0] == "platform_name"):
                continue
            arrKeys[table].append(col[0])
    
    v = {}
    stringSQL = "SELECT DISTINCT date FROM "+TableB+" ORDER BY date ASC"
    aCur.execute(stringSQL)
    dates = aCur.fetchall()
    risk1_dates = "1422115200"

    start = len(dates)-1
    if (len(sys.argv) == 2):
        if (sys.argv[1] == "reset"):
            start = 0
            aCur.execute("TRUNCATE "+DSTDB)
            conn.commit()
    else:
        aCur.execute("DELETE FROM "+DSTDB+" WHERE `date` = '"+str(dates[start][0])+"'")
        conn.commit()

    provision_of_risk1 = {}
    for date_index in range(start, len(dates)):
        v = {}
        v['date'] = str(dates[date_index][0])
        stringSQL = "SELECT platform_id, wdzj_id, dcq_id, name FROM platform_id_name WHERE `dcq_id` != 'NOID'"
        aCur.execute(stringSQL)
        for platform_id, wdzj_id, dcq_id, platform_name in aCur.fetchall():
            arrValues = {}
            if platform_id not in provision_of_risk1:
                provision_of_risk1[platform_id] = 0
            #从A、B表获取定量数据
            for table in [TableA, TableB]:
                arrValues[table] = {}
                _id = dcq_id
                if table == TableA:
                    _id = wdzj_id
                stringSQL = "SELECT "+','.join(arrKeys[table])+" FROM "+table+" WHERE `date` = '"+v['date']+"' AND `platform_id` = '"+_id+"'"
                ret = bCur.execute(stringSQL)
                values = bCur.fetchone()
                for i in range(0, len(arrKeys[table])):
                    value = ((values is not None) and values[i] or 0) #不是None就是自身，否则为0
                    arrValues[table][arrKeys[table][i]] = float(value)
            if ret == 0:
                continue
        
            #从F表获取定性数据
            arrValues[TableF] = {}
            stringSQL = "SELECT "+','.join(arrKeys[TableF])+" FROM "+TableF+" WHERE `platform_name` = '"+platform_name+"'"
            bCur.execute(stringSQL)
            qualitativeList = bCur.fetchone()
            if qualitativeList is None:
                qualitativeList = [0]*len(arrKeys[TableF])
            for i in range(0, len(qualitativeList)):
                arrValues[TableF][arrKeys[TableF][i]] = qualitativeList[i]

            #数据整合
            v['platform_id'] = platform_id
            v['platform_name'] = platform_name
            v['vc_cap_usd'] = arrValues[TableF]['vc_cap_usd']*6*0.8
            v['registered_cap'] = arrValues[TableF]['registered_cap']+0.1*arrValues[TableF]['parent_company_cap']
            v['borrower_transparency'] = arrValues[TableF]['borrower_transparency']
            A = arrValues[TableA]['weekly_total_investor']
            B = arrValues[TableB]['weekly_total_investor']
            A,B=checkzero(A,B)
            v['weekly_total_investor'] = int((A*0.5+B*0.5)*r1())
            if arrValues[TableB]['weekly_total_investor'] == 0:
                v['weekly_new_investor'] = 0
            else:
                v['weekly_new_investor'] = arrValues[TableB]['weekly_new_investor']/arrValues[TableB]['weekly_total_investor']*v['weekly_total_investor']
            A = arrValues[TableA]['weekly_lending']
            B = arrValues[TableB]['weekly_lending']
            A,B=checkzero(A,B)
            v['weekly_lending'] = (B*0.5+A*0.5)*r1()
            if v['date'] == risk1_dates:
                provision_of_risk1[platform_id] = arrValues[TableF]['provision_of_risk1']

            if v['date'] >= risk1_dates:
                provision_of_risk1[platform_id] = provision_of_risk1[platform_id]+arrValues[TableF]['provision_of_risk2']/100*v['weekly_lending']
                v['provision_of_risk_num'] = provision_of_risk1[platform_id]
                if arrValues[TableB]['weekly_outstanding_loan'] != 0:
                    v['provision_of_risk'] = provision_of_risk1[platform_id]/arrValues[TableB]['weekly_outstanding_loan']
                else:
                    v['provision_of_risk'] = 0
            else:
                v['provision_of_risk_num'] = 0
                v['provision_of_risk'] = 0
            A = arrValues[TableA]['weekly_ave_investment']
            B = arrValues[TableB]['weekly_ave_investment']
            A,B=checkzero(A,B)
            if v['weekly_total_investor'] == 0:
                v['weekly_ave_investment'] = 0
            else:
                v['weekly_ave_investment'] = v['weekly_lending']/v['weekly_total_investor']
            v['weekly_ave_investment_per_bid'] = arrValues[TableB]['weekly_ave_investment_per_bid']*r1()
            v['weekly_ave_bid_close_time'] = arrValues[TableB]['weekly_ave_bid_close_time']*r1()
            v['investor_HHI'] = arrValues[TableA]['investor_HHI']*r1()
            v['weekly_ave_lending_per_bid'] = arrValues[TableB]['weekly_ave_lending_per_bid']*r1()
            A = arrValues[TableA]['weekly_total_borrower']
            B = arrValues[TableB]['weekly_total_borrower']
            A,B=checkzero(A,B)
            v['weekly_total_borrower'] = int((0.5*B+0.5*A)*r1())
            if v['weekly_total_borrower'] == 0:
                v['weekly_ave_lending_per_borrower'] = 0
            else:
                v['weekly_ave_lending_per_borrower'] = v['weekly_lending']/v['weekly_total_borrower']
            v['borrower_HHI'] = arrValues[TableA]['borrower_HHI']*r1()
            A = arrValues[TableA]['weekly_loan_period']
            B = arrValues[TableB]['weekly_loan_period']
            A,B=checkzero(A,B)
            v['weekly_loan_period'] = (0.5*B+0.5*A)*r1()
            v['compensation'] = arrValues[TableF]['compensation']
            v['third_entrust'] = arrValues[TableF]['third_entrust']
            v['technical_security'] = arrValues[TableF]['technical_security']
            v['customer_service'] = arrValues[TableF]['customer_service']
            v['third_assurance'] = arrValues[TableF]['third_assurance']
            v['financial_transparency'] = arrValues[TableF]['financial_transparency']
            v['overdue_transparency'] = arrValues[TableF]['overdue_transparency']
            v['borrower_transparency'] = arrValues[TableF]['borrower_transparency']
            v['PR_transparency1'] = arrValues[TableF]['PR_transparency1']
            v['PR_transparency2'] = arrValues[TableF]['PR_transparency2']
            v['debt_transfer'] = arrValues[TableF]['debt_transfer']
            v['real_name'] = arrValues[TableF]['real_name']
            A = arrValues[TableA]['ave_annualized_return']
            B = arrValues[TableB]['ave_annualized_return']
            A,B=checkzero(A,B)
            v['ave_annualized_return'] = (0.5*B+0.5*A)*r2()
            weekly_old_investor = v['weekly_total_investor']-v['weekly_new_investor']
            if weekly_old_investor == 0:
                v['weekly_ave_investment_old'] = 0
            else:
                v['weekly_ave_investment_old'] = arrValues[TableB]['weekly_total_investment_old']/weekly_old_investor
            if weekly_old_investor == 0:
                v['weekly_ratio_new_old'] = 0
            else:
                v['weekly_ratio_new_old'] = v['weekly_new_investor']/weekly_old_investor
            A = arrValues[TableA]['future4week_maturity']
            B = arrValues[TableB]['future4week_maturity']
            A,B=checkzero(A,B)
            v['future4week_maturity'] = (0.5*B+0.5*A)*r1()
            A = arrValues[TableA]['weekly_outstanding_loan']
            B = arrValues[TableB]['weekly_outstanding_loan']
            A,B=checkzero(A,B)
            v['weekly_outstanding_loan'] = (0.5*B+0.5*A)*r1()
            A = arrValues[TableA]['weekly_top10_lending']
            B = arrValues[TableB]['weekly_top10_lending']
            A,B=checkzero(A,B)
            weekly_top10_lending = (0.5*B+0.5*A)*r1()
            if v['weekly_outstanding_loan'] == 0 :
                v['top10_ratio_loan'] = 0
            else:
                if weekly_top10_lending >= v['weekly_outstanding_loan']:
                    weekly_top10_lending = v['weekly_outstanding_loan']*r2()
                v['top10_ratio_loan'] = weekly_top10_lending/v['weekly_outstanding_loan']
            if arrValues[TableB]['weekly_top10_lending'] == 0:
                v['top5_ratio_loan'] = 0
            else:
                if arrValues[TableB]['weekly_top5_lending'] >= v['weekly_outstanding_loan']:
                    arrValues[TableB]['weekly_top5_lending'] = v['weekly_outstanding_loan']*r2()
                v['top5_ratio_loan'] = arrValues[TableB]['weekly_top5_lending']/arrValues[TableB]['weekly_top10_lending']*v['top10_ratio_loan']
            v['latest4week_lending'] = 0
            if date_index >= 4:
                for i in range(0, date_index+1-4)[::-1]:
                    stringSQL = "SELECT weekly_total_borrower, weekly_total_investor FROM "+DSTDB+" WHERE `platform_id` = '"+v['platform_id']+"' AND `date` = '"+str(dates[i][0])+"'"
                    ret = bCur.execute(stringSQL)
                    if ret != 0:
                        break
                if ret == 0:
                    v['borrower_growth'] = 0
                    v['investor_growth'] = 0
                else:
                    month_ago_total_borrower, month_ago_total_investor = bCur.fetchone()
                if month_ago_total_borrower == 0:
                    v['borrower_growth'] = 0
                else:
                    v['borrower_growth'] = v['weekly_total_borrower']/float(month_ago_total_borrower)
                if month_ago_total_investor == 0:
                    v['investor_growth'] = 0
                else:
                    v['investor_growth'] = v['weekly_total_investor']/float(month_ago_total_investor)
                
                weekly_outstanding_loan_sum = 0
                j = 0
                for i in range(0, date_index+1)[::-1]:
                    stringSQL = "SELECT weekly_lending, weekly_outstanding_loan FROM "+DSTDB+" WHERE `platform_id` = '"+v['platform_id']+"' AND `date` = '"+str(dates[i][0])+"'"
                    ret = bCur.execute(stringSQL)
                    if ret == 0:
                        continue
                    weekly_lending, weekly_outstanding_loan = bCur.fetchone()
                    v['latest4week_lending'] += weekly_lending
                    weekly_outstanding_loan_sum += weekly_outstanding_loan
                    j += 1
                    if j == 4:
                        break
                if v['weekly_outstanding_loan'] != 0:
                    v['outstanding_loan'] = v['latest4week_lending']/v['weekly_outstanding_loan']
                else:
                    v['outstanding_loan'] = 0
                sumValue = v['registered_cap'] + v['vc_cap_usd']
                if weekly_outstanding_loan_sum == 0:
                    v['turnover_registered'] = 0
                else:
                    v['turnover_registered'] = sumValue/weekly_outstanding_loan_sum
                if v['future4week_maturity'] == 0:
                    v['not_returned_yet'] = 0
                else:
                    v['not_returned_yet'] = v['latest4week_lending']/v['future4week_maturity']
                
                if v['weekly_loan_period'] == 0:
                    v['money_growth'] = 0
                    v['turnover_period'] = 0
                else:
                    v['money_growth'] = v['not_returned_yet']**(1/v['weekly_loan_period'])
                    v['turnover_period'] = v['latest4week_lending']*v['weekly_loan_period']/12
            
            key = ""
            value = ""
            for (_k,_v) in v.items():
                key = key+"`"+str(_k)+"`,"
                value = value+"'"+str(_v)+"'," 
            stringSQL = "INSERT INTO "+DSTDB+"("+key[:-1]+") VALUES("+value[:-1]+")"
            bCur.execute(stringSQL)
            conn.commit()

        stringSQL = "SELECT sum(weekly_lending) FROM "+DSTDB+" WHERE `date` = '"+str(v['date'])+"' AND `weekly_lending` > 193"
        bCur.execute(stringSQL)
        weekly_total_lending = bCur.fetchone()[0]

        stringSQL = "SELECT platform_id, weekly_lending FROM "+DSTDB+" WHERE `date` = '"+str(v['date'])+"'"
        bCur.execute(stringSQL)
        for platId, weekly_lending in bCur.fetchall():
            market_share = weekly_lending/weekly_total_lending
            month_ago_weekly_lending = 0
            month_ago_weekly_total_lending = 1
            for i in range(0, date_index+1-4)[::-1]:
                stringSQL = "SELECT weekly_lending FROM "+DSTDB+" WHERE `date` = '"+str(dates[i][0])+"' AND `platform_id` = '"+platId+"'"
                ret = cCur.execute(stringSQL)
                if ret == 0:
                    continue
                month_ago_weekly_lending = cCur.fetchone()[0]
                stringSQL = "SELECT sum(weekly_lending) FROM "+DSTDB+" WHERE `date` = '"+str(dates[i][0])+"' AND `weekly_lending` > 200"
                ret = cCur.execute(stringSQL)
                month_ago_weekly_total_lending = cCur.fetchone()[0]
                if ret != 0:
                    break
            month_ago_market_share = month_ago_weekly_lending/month_ago_weekly_total_lending
            if month_ago_market_share == 0:
                continue
            stringSQL = "UPDATE "+DSTDB+" SET `market_share_growth` = '"+str(market_share/month_ago_market_share)+"' WHERE `platform_id` = '"+platId+"' AND `date` = '"+str(v['date'])+"'"
            cCur.execute(stringSQL)
            conn.commit()
