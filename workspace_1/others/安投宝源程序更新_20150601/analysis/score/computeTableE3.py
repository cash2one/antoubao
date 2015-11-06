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
import numpy as np
from header import *

def foo1(_min, _val, _max):
    _min = _min*0.999
    _max = _max*1.001
    if (_val == 0):
        return 0
    _min = (_min <= 0 and 1) or _min
    _max = (_max <= 0 and 1) or _max
    _val = (_val < _min and _min) or _val
    _val = (_val > _max and _max) or _val
    if (_val <= 0) or ((_max == 1) and (_min == 1)):
        return 0    
    return (log(_val)-log(_min))/(log(_max)-log(_min))*100

def foo2(_min, _val, _max):
    _min = _min*0.999
    _max = _max*1.001
    if (_val == 0):
        return 0
    _min = (_min <= 0 and 1) or _min
    _max = (_max <= 0 and 1) or _max
    _val = (_val < _min and _min) or _val
    _val = (_val > _max and _max) or _val
    _val = (_val == 0 and _max) or _val
    if (_max == 1) and (_min == 1):
        return 0
    return abs((log(_max)-log(_val))/(log(_max)-log(_min)))*100

def foo3(_min, _val, _max, _avg):
    _min = _min*0.999
    _max = _max*1.001
    if (_val == 0):
        return 0
    _val = (_val < _min and _min) or _val
    _val = (_val > _max and _max) or _val
    if _val < _avg:
        _val = abs((log(_min)-log(_val))/(log(_min)-log(_avg)))
    else:
        _val = abs((log(_val)-log(_max))/(log(_avg)-log(_max)))
    return _val*100

if __name__ == "__main__":
    conn=MySQLdb.connect(host=HOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    cur=conn.cursor()
    inlineCur=conn.cursor()

    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    SRCDB = "platform_quantitative_data_E2"
    DSTDB = "platform_quantitative_data_E3"

    stringSQL = "SHOW FULL COLUMNS FROM "+DSTDB
    cur.execute(stringSQL)
    arrKeys = []
    for col in cur.fetchall():
        if (col[0] == "id") or (col[0] == "platform_id") or (col[0] == "platform_name") or (col[0] == "provision_of_risk_num"):
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
        where = "`date` = '"+v['date']+"' AND `black` NOT LIKE '%B%' AND `black` NOT LIKE '%P%' AND `platform_name` != 'strategy_report'"
        arrValue = {}
        for table in ["3sigma_O_high", "3sigma_O_low","max_I", "min_J", "ave_K", "2sigma_N_high", "2sigma_N_low"]:
            if (table == "3sigma_O_high"):
                stringSQL = "SELECT "+','.join(arrKeys)+" FROM platform_quantitative_data_3sigma_O WHERE `date` = '"+v['date']+"' AND `type` = 'high'"

            elif (table == "3sigma_O_low"):
                stringSQL = "SELECT "+','.join(arrKeys)+" FROM platform_quantitative_data_3sigma_O WHERE `date` = '"+v['date']+"' AND `type` = 'low'"
            elif (table == "max_I"):
                stringSQL = "SELECT "+','.join(arrKeys)+" FROM platform_quantitative_data_"+table+" WHERE `date` = '"+v['date']+"'"
            elif (table == "min_J"):
                stringSQL = "SELECT "+','.join(arrKeys)+" FROM platform_quantitative_data_"+table+" WHERE `date` = '"+v['date']+"'"
            elif (table == "2sigma_N_high"):
                stringSQL = "SELECT "+','.join(arrKeys)+" FROM platform_quantitative_data_2sigma_N WHERE `date` = '"+v['date']+"' AND `type` = 'high'"
            elif (table == "2sigma_N_low"):
                stringSQL = "SELECT "+','.join(arrKeys)+" FROM platform_quantitative_data_2sigma_N WHERE `date` = '"+v['date']+"' AND `type` = 'low'"
            else:
                stringSQL = "SELECT "+','.join(arrKeys)+" FROM platform_quantitative_data_"+table+" WHERE `date` = '"+v['date']+"'"
            ret = cur.execute(stringSQL)
            if ret == 0:
                break
            if (table not in arrValue):
                arrValue[table] = {}
            List = cur.fetchone()
            for i in range(0, len(List)):
                arrValue[table][arrKeys[i]] = float(List[i])
        if ret == 0:
            continue

        #stringSQL = "SELECT weekly_lending/weekly_ave_investment_per_bid FROM "+SRCDB+" WHERE `date` = '"+v['date']+"'"
        #inlineCur.execute(stringSQL)
        #list_weekly_ave_investment_per_bid = inlineCur.fetchone()
        #stringSQL = "SELECT weekly_ave_investment_per_bid FROM "+SRCDB+" WHERE `date` = '"+v['date']+"'"
        #inlineCur.execute(stringSQL)
        #weekly_ave_investment_per_bid = inlineCur.fetchone()
        #ave_weekly_ave_investment_per_bid = np.average(weekly_ave_investment_per_bid, weights=list_weekly_ave_investment_per_bid)

        #stringSQL = "SELECT sum(weekly_new_investor)/sum(weekly_total_investor-weekly_new_investor) FROM "+SRCDB+" WHERE `date` = '"+v['date']+"'"
        #inlineCur.execute(stringSQL)
        #ave_weekly_ratio_new_old = inlineCur.fetchone()[0]

        ave = {}
        aveKeys = ["sum(weekly_new_investor)/sum(weekly_total_investor-weekly_new_investor)", "weekly_lending/weekly_ave_investment_per_bid", "weekly_ave_investment", "weekly_total_investor", "weekly_ave_investment_old", "weekly_total_investor-weekly_new_investor", "weekly_loan_period", "weekly_lending", "weekly_ave_lending_per_borrower", "weekly_ave_lending_per_bid", "weekly_ave_bid_close_time", "weekly_ave_investment_per_bid"]
        stringSQL = "SELECT "+','.join(aveKeys)+" FROM "+SRCDB+" WHERE "+where
        cur.execute(stringSQL)
        for _list in cur.fetchall():
            for i in range(0, len(_list)):
                if aveKeys[i] == "weekly_total_investor-weekly_new_investor":
                    aveKeys[i] = "totalnew"
                elif aveKeys[i] == "weekly_lending/weekly_ave_investment_per_bid":
                    aveKeys[i] = "lendinginvestment"
                if aveKeys[i] not in ave:
                    ave[aveKeys[i]] = []
                ave[aveKeys[i]].append(_list[i])
        top20_close_time = []
        top20_new_old = []
        top20_lending = []
        stringSQL = "SELECT weekly_ave_bid_close_time, weekly_ratio_new_old, weekly_lending FROM "+SRCDB+" WHERE "+where+" ORDER BY `weekly_lending` DESC LIMIT 20"
        cur.execute(stringSQL)
        for _list in cur.fetchall():
            top20_close_time.append(_list[0])
            top20_new_old.append(_list[1])
            top20_lending.append(_list[2])

        stringSQL = "SELECT platform_id,platform_name,"+','.join(arrKeys)+" FROM "+SRCDB+" WHERE "+where
        cur.execute(stringSQL)
        for resList in cur.fetchall():
            i = 0
            for value in resList:
                if (i == 0):
                    v['platform_id'] = str(value)
                elif (i == 1):
                    aveKeys[i] = "investor"
                    v['platform_name'] = str(value)
                else:
                    v[arrKeys[i-2]] = float(value)
                i+=1
            kv = {}
            kv['date'] = v['date']
            kv['platform_id'] = v['platform_id']
            kv['platform_name'] = v['platform_name']
            kv['registered_cap'] = foo1(arrValue['3sigma_O_low']['registered_cap'], v['registered_cap'], arrValue['3sigma_O_high']['registered_cap'])#3sigma
            kv['vc_cap_usd'] = foo1(arrValue['3sigma_O_low']['vc_cap_usd'], v['vc_cap_usd'], arrValue['3sigma_O_high']['vc_cap_usd'])#3sigma
            kv['turnover_registered'] = foo1(arrValue['2sigma_N_low']['turnover_registered'], v['turnover_registered'], arrValue['2sigma_N_high']['turnover_registered'])#2sigma
            kv['weekly_new_investor'] = foo1(arrValue['3sigma_O_low']['weekly_new_investor'], v['weekly_new_investor'], arrValue['3sigma_O_high']['weekly_new_investor'])#3sigma
            kv['weekly_total_investor'] = foo1(arrValue['3sigma_O_low']['weekly_total_investor'], v['weekly_total_investor'], arrValue['3sigma_O_high']['weekly_total_investor'])#3sigma
            kv['weekly_lending'] = foo1(arrValue['3sigma_O_low']['weekly_lending'], v['weekly_lending'], arrValue['3sigma_O_high']['weekly_lending'])#3sigma
            kv['weekly_ave_investment'] = foo3(arrValue['3sigma_O_low']['weekly_ave_investment'], v['weekly_ave_investment'], arrValue['3sigma_O_high']['weekly_ave_investment'], arrValue['ave_K']['weekly_ave_investment'])#3sigma
        
            kv['weekly_ave_investment_old'] = foo3(arrValue['3sigma_O_low']['weekly_ave_investment_old'], v['weekly_ave_investment_old'], arrValue['3sigma_O_high']['weekly_ave_investment_old'], arrValue['ave_K']['weekly_ave_investment_old'])#3sigma
            kv['weekly_ave_investment_per_bid'] = foo3(arrValue['3sigma_O_low']['weekly_ave_investment_per_bid'], v['weekly_ave_investment_per_bid'], arrValue['3sigma_O_high']['weekly_ave_investment_per_bid'], arrValue['ave_K']['weekly_ave_investment_per_bid'])#3sigma
            kv['weekly_ave_bid_close_time'] = foo3(arrValue['3sigma_O_low']['weekly_ave_bid_close_time'], v['weekly_ave_bid_close_time'], arrValue['3sigma_O_high']['weekly_ave_bid_close_time'], arrValue['ave_K']['weekly_ave_bid_close_time'])#3sigma
            
            kv['investor_HHI'] = foo2(arrValue['3sigma_O_low']['investor_HHI'], v['investor_HHI'], arrValue['3sigma_O_high']['investor_HHI'])#3sigma
            kv['weekly_ratio_new_old'] = foo3(arrValue['3sigma_O_low']['weekly_ratio_new_old'], v['weekly_ratio_new_old'], arrValue['3sigma_O_high']['weekly_ratio_new_old'], arrValue['ave_K']['weekly_ratio_new_old'])#3sigma
            kv['weekly_ave_lending_per_borrower'] = foo3(arrValue['3sigma_O_low']['weekly_ave_lending_per_borrower'], v['weekly_ave_lending_per_borrower'], arrValue['3sigma_O_high']['weekly_ave_lending_per_borrower'], arrValue['ave_K']['weekly_ave_lending_per_borrower'])#3sigma
            kv['weekly_ave_lending_per_bid'] = foo3(arrValue['3sigma_O_low']['weekly_ave_lending_per_bid'], v['weekly_ave_lending_per_bid'], arrValue['3sigma_O_high']['weekly_ave_lending_per_bid'], arrValue['ave_K']['weekly_ave_lending_per_bid'])#3sigma
            kv['weekly_total_borrower'] = foo1(arrValue['3sigma_O_low']['weekly_total_borrower'], v['weekly_total_borrower'], arrValue['3sigma_O_high']['weekly_total_borrower'])#3sigma
            kv['top10_ratio_loan'] = foo2(arrValue['3sigma_O_low']['top10_ratio_loan'], v['top10_ratio_loan'], arrValue['3sigma_O_high']['top10_ratio_loan'])#3sigma
            kv['top5_ratio_loan'] = foo2(arrValue['3sigma_O_low']['top5_ratio_loan'], v['top5_ratio_loan'], arrValue['3sigma_O_high']['top5_ratio_loan'])#3sigma
            kv['top5_ratio_investment'] = foo2(arrValue['3sigma_O_low']['top5_ratio_investment'], v['top5_ratio_investment'], arrValue['3sigma_O_high']['top5_ratio_investment'])#3sigma
            kv['top10_ratio_investment'] = foo2(arrValue['3sigma_O_low']['top10_ratio_investment'], v['top10_ratio_investment'], arrValue['3sigma_O_high']['top10_ratio_investment'])#3sigma
            kv['borrower_HHI'] = foo2(arrValue['3sigma_O_low']['borrower_HHI'], v['borrower_HHI'], arrValue['3sigma_O_high']['borrower_HHI'])#3sigma
            kv['not_returned_yet'] = foo1(arrValue['3sigma_O_low']['not_returned_yet'], v['not_returned_yet'], arrValue['3sigma_O_high']['not_returned_yet'])#3sigma
            kv['weekly_loan_period'] = foo3(arrValue['3sigma_O_low']['weekly_loan_period'], v['weekly_loan_period'], arrValue['3sigma_O_high']['weekly_loan_period'], arrValue['ave_K']['weekly_loan_period'])#3sigma
            kv['outstanding_loan'] = foo1(arrValue['3sigma_O_low']['outstanding_loan'], v['outstanding_loan'], arrValue['3sigma_O_high']['outstanding_loan'])#3sigma
            kv['compensation'] = v['compensation']*100
            kv['provision_of_risk'] = foo1(arrValue['3sigma_O_low']['provision_of_risk'],v['provision_of_risk'],arrValue['3sigma_O_high']['provision_of_risk'])#3sigma
            kv['third_entrust'] = v['third_entrust']*100
            kv['technical_security'] = v['technical_security']*20
            kv['third_assurance'] = v['third_assurance']*100
            kv['real_name'] = v['real_name']*20
            kv['debt_transfer'] = v['debt_transfer']*100
            kv['financial_transparency'] = v['financial_transparency']*20
            kv['overdue_transparency'] = v['overdue_transparency']*20
            kv['borrower_transparency'] = v['borrower_transparency']*20
            kv['customer_service'] = v['customer_service']*20
            kv['PR_transparency1'] = foo1(arrValue['3sigma_O_low']['PR_transparency1'], v['PR_transparency1'], arrValue['3sigma_O_high']['PR_transparency1'])#3sigma
            kv['PR_transparency2'] = v['PR_transparency2']
            kv['money_growth'] = foo1(arrValue['2sigma_N_low']['money_growth'], v['money_growth'], arrValue['2sigma_N_high']['money_growth'])#2sigma
            kv['borrower_growth'] = foo1(arrValue['3sigma_O_low']['borrower_growth'], v['borrower_growth'], arrValue['3sigma_O_high']['borrower_growth']);#3sigma
            kv['investor_growth'] = foo1(arrValue['3sigma_O_low']['investor_growth'], v['investor_growth'], arrValue['3sigma_O_high']['investor_growth']);#3sigma
            kv['market_share_growth'] = foo1(arrValue['3sigma_O_low']['market_share_growth'], v['market_share_growth'], arrValue['3sigma_O_high']['market_share_growth']);#3sigma
            kv['short_term_debt_ratio'] = foo2(arrValue['3sigma_O_low']['short_term_debt_ratio'], v['short_term_debt_ratio'], arrValue['3sigma_O_high']['short_term_debt_ratio']);
            if (v['ave_annualized_return'] >= 22):
                kv['ave_annualized_return'] = 1
            elif (v['ave_annualized_return'] >= 18.5):
                kv['ave_annualized_return'] = 30
            elif (v['ave_annualized_return'] >= 15.4):
                kv['ave_annualized_return'] = 55
            elif (v['ave_annualized_return'] >= 12.5):
                kv['ave_annualized_return'] = 85
            else:
                kv['ave_annualized_return'] = 100
            kv['turnover_period'] = foo1(arrValue['3sigma_O_low']['turnover_period'], v['turnover_period'], arrValue['3sigma_O_high']['turnover_period'])
            if v['cash_flow_in'] <= 0:
                kv['cash_flow_in'] = 0
            else:
                kv['cash_flow_in'] = foo1(arrValue['3sigma_O_low']['cash_flow_in'], v['cash_flow_in'], arrValue['3sigma_O_high']['cash_flow_in']);

            key = ""
            value = ""
            for (_k, _v) in kv.items():
                key = key+"`"+str(_k)+"`,"
                value = value+"'"+str(_v)+"'," 
            stringSQL = "INSERT INTO "+DSTDB+"("+key[:-1]+") VALUES("+value[:-1]+")"
            inlineCur.execute(stringSQL)
            conn.commit()
