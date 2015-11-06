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
import numpy as np

def score_transfer(_dict, q):
    dict_result = {}
    for (key,_List) in _dict.items():
        if key == "platform_id":
            continue
        quantile = np.percentile(_List,q)
        maxvalue = None
        minvalue = 100
        for i in range(len(_List)):
            if _List[i] >= quantile:
                maxvalue = max(maxvalue,_List[i])
                minvalue = min(minvalue,_List[i])
        for i in range(len(_List)):
            if(_List[i] <= maxvalue and _List[i] > minvalue):
                _List[i] = (_List[i]-minvalue+0.0)/(maxvalue-minvalue)*75
            elif(_List[i] <= minvalue):
                _List[i] = 0.5 + random.random()
        dict_result[key] = _List
    return(dict_result)

if __name__ == '__main__':
    LEVEL=["C", "B", "B+", "B++", "A", "A+", "A++"]
    sconn=MySQLdb.connect(host=DBHOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    scur=sconn.cursor()
    conn=MySQLdb.connect(host=DEVHOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT) 
    cur=conn.cursor()
    inlineCur=conn.cursor()

    scur.execute("SET NAMES 'UTF8'")
    scur.execute("SET CHARACTER SET UTF8")
    scur.execute("SET CHARACTER_SET_RESULTS=UTF8")
    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    stringSQL = "SELECT DISTINCT date FROM platform_score_T ORDER BY `date` ASC"
    cur.execute(stringSQL)
    dates = cur.fetchall()

    dates = dates[len(dates)-2:]

    cur.execute("TRUNCATE view_mobile")
    conn.commit()

    tabBasic = {}
    tabBasic['platform_score_T'] = ["score", "activeness_credibility", "growth", "distribution", "security", "capital_adequacy_ratio", "pellucidity", "mobility", "status"]
    tabBasic['platform_quantitative_data_E2'] = ["turnover_period", "weekly_total_investor", "weekly_lending", "weekly_total_borrower", "ave_annualized_return", "weekly_loan_period", "turnover_registered", "top10_ratio_loan", "not_returned_yet", "money_growth", "cash_flow_in", "top5_ratio_investment", "top10_ratio_investment"]
    #tabBasic['platform_quantitative_data_E3'] = ["turnover_period"]
    tabBasic['platform_qualitative_F'] = ["website", "financing_status", "registered_cap", "established_date", "location", "debt_transfer", "cash_in_fee", "cash_out_fee", "management_fee", "advanced_repayment", "reserve_fund", "third_entrust", "listing", "state_owned", "bank", "third_assurance", "vc_cap_usd", "house_debt", "car_debt", "small_credit_bid", "big_credit_bid", "bill_debt"]

    tabLevel = {}
    tabLevel['R'] = ["score", "weekly_total_investor", "weekly_lending", "weekly_total_borrower", "ave_annualized_return", "weekly_loan_period", "turnover_registered", "top10_ratio_loan", "not_returned_yet", "money_growth"];
    tabLevel['RR'] = ["DESC", "DESC", "DESC", "DESC", "DESC", "ASC", "DESC", "ASC", "DESC", "DESC"]
    #tabLevel['RR'] = [">", ">", ">", ">", ">", "<", ">", "<", ">", ">"];
    #tabLevel['L'] = ["C", "B", "B+", "B++", "A", "A+", "A++"];

    proAll = {}
    tmp = []
    stringSQL = "SELECT platform_id, status, date FROM platform_problem_record_Y ORDER BY `date` DESC"
    scur.execute(stringSQL)
    for platid, status, date in scur.fetchall():
        if platid not in tmp and status < 0.89:
            proAll[platid] = int(date)
        tmp.append(platid)

    Integer = ["weekly_total_investor", "weekly_lending", "weekly_total_borrower", "turnover_period"]
    Decimal = ["ave_annualized_return", "weekly_loan_period", "activeness_credibility", "growth", "distribution", "security", "", "pellucidity", "mobility"]
    Decimal2 = ["not_returned_yet"]
    Decimal3 = ["top10_ratio_loan", "turnover_registered", "money_growth"]

    for date in dates:
        #基础数据填充
        if (date == dates[0]):
            lastdate = [0]
        else:
            lastdate = dates[0]
        date = str(date[0])
        lastdate = str(lastdate[0])
        v = {}
        indexLevel = 0
        stringSQL = "SELECT platform_id, platform_name FROM platform_score_T WHERE `date` = '"+date+"' ORDER BY `score` ASC"
        cur.execute(stringSQL)
        for v['platform_id'], v['platform_name'] in cur.fetchall():
            v['date'] = str(date)
            
            l = LEVEL[indexLevel]
            if v['platform_id'] in LEVEL:
                indexLevel += 1
                continue
            
            for (key, prop) in tabBasic.items():
                if (key == "platform_qualitative_F"):
                    stringSQL = "SELECT "+','.join(prop)+" FROM "+key+" WHERE `platform_name` = '"+v['platform_name']+"'"
                    ret = scur.execute(stringSQL)
                    if (ret == 0):
                        value = [0]*len(prop)
                    else:
                        value = scur.fetchone()
                else:
                    _date = date
                    if key == "platform_quantitative_data_E2" and v['platform_id'] in proAll.keys():
                        _date = (proAll[v['platform_id']]-((proAll[v['platform_id']]-1414252800)%(7*24*3600)))-(7*24*3600)

                    stringSQL = "SELECT "+','.join(prop)+" FROM "+key+" WHERE `platform_id` = '"+v['platform_id']+"' AND `date` = '"+str(_date)+"'"
                    ret = cur.execute(stringSQL)
                    if (ret == 0):
                        value = [0]*len(prop)
                    else:
                        value = cur.fetchone()
                for i in range(0, len(prop)):
#                     if value[i] == 0:
#                         continue
                    if prop[i] == "capital_adequacy_ratio":
                        capital_adequacy_ratio = value[i]
                        v[prop[i]] = value[i]
                    elif prop[i] == "security":
                        security = value[i]
                        v[prop[i]] = value[i]
                    elif prop[i] == "pellucidity":
                        v['reputation'] = (value[i]+security)/2
                        v[prop[i]] = value[i]
                    elif prop[i] == "third_entrust":
                        if value[i] == 0:
                            v[prop[i]] = "无第三方托管"
                        else:
                            v[prop[i]] = "有第三方托管"
                        v[prop[i]+"_num"] = value[i]
                    elif prop[i] == "mobility":
                        if capital_adequacy_ratio == 0 or value[i] == 0:
                            v[prop[i]] = None
                        else:
                            v['mobility_original'] = value[i]
                            v[prop[i]] = round(capital_adequacy_ratio*0.3367+value[i]*0.6633, 1)
                    elif prop[i] == "weekly_loan_period":
                        v[prop[i]] = round(value[i]/30, 2)
                    elif prop[i] == "top10_ratio_loan" or prop[i] == "turnover_registered":
                        v[prop[i]] = round(value[i]*100, 1)
                    elif prop[i] == "money_growth":
                        v[prop[i]] = round((value[i]-1)*100, 1)
                    elif prop[i] in Integer:
                        v[prop[i]] = round(value[i])
                    elif prop[i] in Decimal:
                        v[prop[i]] = round(value[i], 1)
                    elif prop[i] in Decimal2:
                        v[prop[i]] = round(value[i], 2)
                    elif prop[i] in Decimal3:
                        v[prop[i]] = round(value[i], 3)
                    else:
                        v[prop[i]] = value[i]

            strKey = ""
            strValue = ""
            debt_transfer_num = 0
            for (key, value) in v.items():
                strKey += "`"+key+"`,"
                if (key == "debt_transfer"):
                    debt_transfer_num = value
                    if (value == 0):
                        value = "不支持"
                    else:
                        value = "支持"
                if (value == "前海理想金融"):
                    value = "前海理想"
                strValue += "'"+str(value)+"',"

            stringSQL = "INSERT INTO view_mobile("+strKey[:-1]+", `debt_transfer_num`) VALUES("+strValue[:-1]+", "+str(debt_transfer_num)+")"
            inlineCur.execute(stringSQL)
            conn.commit()

            stringSQL = "UPDATE view_mobile SET `level` = '"+l+"' WHERE `platform_id` = '"+v['platform_id']+"' AND `date` = '"+date+"'"
            inlineCur.execute(stringSQL)
            conn.commit()

            v = {}

        #排序
        '''
        rankArr = {}
        stringSQL = "SELECT platform_id FROM view_mobile WHERE `date` = '"+date+"' ORDER BY `score` ASC"
        cur.execute(stringSQL)
        for platId in cur.fetchall():
            platId = platId[0]
            for i in range(0, len(tabLevel['R'])):
                if tabLevel['R'][i] not in rankArr.keys():
                    rankArr[tabLevel['R'][i]] = {}
                stringSQL = "SELECT "+tabLevel['R'][i]+" FROM view_mobile WHERE `platform_id` = '"+platId+"' AND `date` = '"+date+"'"
                inlineCur.execute(stringSQL)
                v = inlineCur.fetchone()[0]
                if v is None:
                    continue
                stringSQL = "SELECT count(*) FROM view_mobile WHERE `"+tabLevel['R'][i]+"` "+tabLevel['RR'][i]+" "+str(v-0.00001)+" AND `date` = '"+date+"'"
                inlineCur.execute(stringSQL)
                r = inlineCur.fetchone()[0]
                if r == 0:
                    r = 1
                if r not in rankArr[tabLevel['R'][i]].keys():
                    rankArr[tabLevel['R'][i]][r] = 0
                else:
                    rankArr[tabLevel['R'][i]][r] += 1
                stringSQL = "UPDATE view_mobile SET `rank_"+tabLevel['R'][i]+"` = '"+str(r+rankArr[tabLevel['R'][i]][r])+"' WHERE `platform_id` = '"+platId+"' AND `date` = '"+date+"'"
                inlineCur.execute(stringSQL)
                conn.commit()
        '''
        for i in range(0, len(tabLevel['R'])):
            stringSQL = "SELECT platform_id FROM view_mobile WHERE `date` = '"+date+"' ORDER BY `"+tabLevel['R'][i]+"` "+tabLevel['RR'][i]
            cur.execute(stringSQL)
            index = 1
            for platId in cur.fetchall():
                platId = platId[0]
                stringSQL = "UPDATE view_mobile SET `rank_"+tabLevel['R'][i]+"` = '"+str(index)+"' WHERE `platform_id` = '"+platId+"' AND `date` = '"+date+"'"
                inlineCur.execute(stringSQL)
                conn.commit()

                if (lastdate == "0"):
                    var = 0
                else:
                    stringSQL = "SELECT rank_"+tabLevel['R'][i]+" FROM view_mobile WHERE `platform_id` = '"+platId+"' AND `date` = '"+lastdate+"'"
                    inlineCur.execute(stringSQL)
                    lastRank = inlineCur.fetchone()
                    if lastRank is None or lastRank[0] is None:
                        var = 0
                    else:
                        var = lastRank[0]-index
                stringSQL = "UPDATE view_mobile SET `var_"+tabLevel['R'][i]+"` = '"+str(var)+"' WHERE `platform_id` = '"+platId+"' AND `date` = '"+date+"'"
                inlineCur.execute(stringSQL)
                conn.commit()
                index += 1
                
        if lastdate != "0":
            stringSQL = "DELETE FROM view_mobile WHERE `date` = '"+lastdate+"'"
            cur.execute(stringSQL)
            conn.commit()

            _dict = {}
            _dict['activeness_credibility'] = []
            _dict['distribution'] = []
            _dict['security'] = []
            _dict['mobility'] = []
            _dict['growth'] = []
            _dict['pellucidity'] = []
            _dict['platform_id'] = []
            stringSQL = "SELECT activeness_credibility, distribution, security, mobility, platform_id, growth, pellucidity FROM view_mobile"
            cur.execute(stringSQL)
            for _list in cur.fetchall():
                _dict['activeness_credibility'].append(_list[0])
                _dict['distribution'].append(_list[1])
                _dict['security'].append(_list[2])
                _dict['mobility'].append(_list[3])
                _dict['platform_id'].append(_list[4])
                _dict['growth'].append(_list[5])
                _dict['pellucidity'].append(_list[6])

            d = score_transfer(_dict, 1.5)
            i = 0
            for platId in _dict['platform_id']:
                stringSQL = "UPDATE view_mobile SET `activeness_credibility` = '"+str(round(d['activeness_credibility'][i], 1))+"', `distribution` = '"+str(round(d['distribution'][i], 1))+"', `security` = '"+str(round(d['security'][i], 1))+"', `mobility` = '"+str(round(d['mobility'][i], 1))+"' WHERE `platform_id` = '"+platId+"'"
                inlineCur.execute(stringSQL)
                conn.commit()
                i+=1

            for prop in tabBasic['platform_score_T']+["mobility_original", "reputation"]:
                if prop == "score" or prop == "status":
                    continue

                stringSQL = "SELECT avg("+prop+") FROM view_mobile"
                cur.execute(stringSQL)
                ave = cur.fetchone()[0]
                stringSQL = "UPDATE view_mobile SET `standard_"+prop+"` = '"+str(ave)+"'"
                cur.execute(stringSQL)
                conn.commit()
