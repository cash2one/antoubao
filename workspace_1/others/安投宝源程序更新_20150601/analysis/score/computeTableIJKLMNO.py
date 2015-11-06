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
from math import floor
from math import log
import numpy as np

#方差
def variance(_List):
    sum1=0.0
    sum2=0.0
    for i in range(len(_List)):
        sum1 += _List[i]
    ave = sum1/len(_List)
    for i in range(len(_List)):
        sum2 += (_List[i]-ave)**2
    return sum2/len(_List)

#定义list的除法
def list_divide(list1,list2):
    list3 = []
    for i in range(0,len(list1)):
        if list2[i] != 0:
            list3.append((list1[i]+0.0)/list2[i])
        else:
            list3.append(0)
    return list3

#定义list的减法
def list_minus(list1,list2):
    list3 = []
    for i in range(0,len(list1)):
        list3.append(list1[i]-list2[i])
    return list3

#定义去除q%极值后的加权平均
def ave_weights_quantile(dict_a,key,weights,quantile):
    _dict = {}
    _dict[key] = []
    _dict[weights] = []
    for i in range(0,len(dict_a[key])):
        if dict_a[key][i] == 0 or dict_a[weights] == 0:
            continue
        _dict[key].append(dict_a[key][i])
        _dict[weights].append(dict_a[weights][i])
    sorted_list = sorted(_dict[key])
    standard = sorted_list[int(round(len(sorted_list)*quantile))-1]
    dict_b = {}
    dict_b[key]=[]
    dict_b[weights]=[]
    for i in range(0,len(_dict[key])):
        if _dict[key][i] <= standard:
            dict_b[key].append(_dict[key][i])
            dict_b[weights].append(_dict[weights][i])
    return(np.average(dict_b[key],weights = dict_b[weights]))

#定义去除q%极值后的求和
def sum_quantile(dict_a,key,quantile):
    _dict = {}
    _dict[key] = []
    for i in range(0,len(dict_a[key])):
        if dict_a[key][i] == 0:
            continue
        _dict[key].append(dict_a[key][i])
    sorted_list = sorted(_dict[key])
    standard = sorted_list[int(round(len(sorted_list)*quantile))-1]
    dict_b = {}
    dict_b[key]=[]
    for i in range(0,len(_dict[key])):
        if _dict[key][i] <= standard:
            dict_b[key].append(_dict[key][i])
    return(sum(dict_b[key])+0.0)

def range_of_index(date_index, arrKeys, dates, count):
    ave = {}
    result = {}
    for key in arrKeys:
        ave[key] = 0
        result[key] = 0
    date2 = dates[date_index-1][0]
    keyStr = ""
    for key in arrKeys:
        keyStr = keyStr+"avg"+"("+str(key)+"), "
    stringSQL = "SELECT "+keyStr[:-2]+" FROM "+SRCDB+" WHERE `date` = '"+str(date2)+"' AND `black` = '' AND `platform_name` != 'strategy_report'"
    inlineCur.execute(stringSQL)
    _list = inlineCur.fetchone()
    for i in range(0,len(_list)):
        ave[arrKeys[i]] = _list[i]
    for key in arrKeys:
        if (key == 'weekly_ave_bid_close_time'):
            result['weekly_ave_bid_close_time'] = 600000
        else:
            result[key] = count/2*ave[key]
    return (result)

if __name__ == "__main__":
    conn=MySQLdb.connect(host=HOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    cur=conn.cursor()
    inlineCur=conn.cursor()
    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    SRCDB = "platform_quantitative_data_E2"
    table = {}
    table["max"] = "platform_quantitative_data_max_I"
    table["min"] = "platform_quantitative_data_min_J"
    table["avg"] = "platform_quantitative_data_ave_K"
    table["variance"] = "platform_quantitative_data_var_L"
    table["1sigma"] = "platform_quantitative_data_1sigma_M"
    table["2sigma"] = "platform_quantitative_data_2sigma_N"
    table["3sigma"] = "platform_quantitative_data_3sigma_O"

    _1SIGMA=0.6827
    _2SIGMA=0.9545
    _3SIGMA=0.98125

    where = "`black` = '' AND `platform_name` != 'strategy_report' AND `platform_id` != '6372008a69'"

    stringSQL = "SHOW FULL COLUMNS FROM "+table["max"]
    cur.execute(stringSQL)
    arrKeys = []
    keyStr = ""
    for col in cur.fetchall():
        if (col[0] == "id") or (col[0] == "date") or (col[0] == "provision_of_risk_num"):
            continue
        arrKeys.append(col[0])
        keyStr = keyStr + "`"+str(col[0])+"`,"

    stringSQL = "SELECT DISTINCT date FROM "+SRCDB+" WHERE "+where+" ORDER BY date ASC"
    cur.execute(stringSQL)
    dates = cur.fetchall()

    start = len(dates)-1
    if (len(sys.argv) == 2):
        if (sys.argv[1] == "reset"):
            start = 0
            for (k,v) in table.items():
                cur.execute("TRUNCATE "+v)
                conn.commit()
    else:
        for (k,v) in table.items():
            cur.execute("DELETE FROM "+v+" WHERE `date` = '"+str(dates[start][0])+"'")
            conn.commit()

    for date_index in range(start, len(dates)):
        v = {}
        date = str(dates[date_index][0])
        if date > LINEDATE:
            stringSQL = "SELECT count(*) FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND "+where
            cur.execute(stringSQL)
            count = cur.fetchone()[0]
            ceil = range_of_index(date_index, arrKeys, dates, count)
        #MAX/MIN/VAR
        for fun in ["max", "min", "variance", "avg"]:
            valueStr = ""
            for key in arrKeys:
                if date <= LINEDATE:
                    stringSQL = "SELECT "+fun+"("+key+") FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND `"+key+"` > '0' AND "+where
                else:
                    stringSQL = "SELECT "+fun+"("+key+") FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND `"+key+"` > '0' AND `"+key+"` < '"+str(ceil[key])+"' AND "+where
                cur.execute(stringSQL)
                value = cur.fetchone()[0]
                if value is None:
                    value = 0
                valueStr = valueStr+"'"+str(value)+"',"
            stringSQL = "INSERT INTO "+table[fun]+"(`date`, "+keyStr[:-1]+") VALUES('"+str(date)+"', "+valueStr[:-1]+")"
            cur.execute(stringSQL)
            conn.commit()
            if fun == "avg":
                stringSQL = "INSERT INTO "+SRCDB+"(`date`, `platform_id`, `platform_name`, "+keyStr[:-1]+") VALUES('"+str(date)+"', 'strategyC', 'strategy_report', "+valueStr[:-1]+")"
                cur.execute(stringSQL)
                conn.commit()

        #SIGMA
        for (_k, _v) in {"1sigma":_1SIGMA, "2sigma":_2SIGMA, "3sigma":_3SIGMA}.items():
            highStr = ""
            lowStr = ""
            for key in arrKeys:
                if date <= LINEDATE:
                    stringSQL = "SELECT count(*) FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND `"+key+"` > '0' AND "+where
                else:
                    stringSQL = "SELECT count(*) FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND `"+key+"` > '0' AND `"+key+"` < '"+str(ceil[key])+"' AND "+where
                cur.execute(stringSQL)
                count = cur.fetchone()[0]
                s = int(floor(_v*count))

                if date <= LINEDATE:
                    stringSQL = "SELECT "+key+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND `"+key+"` > '0' AND "+where+" ORDER BY "+key+" DESC"
                else:
                    stringSQL = "SELECT "+key+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND `"+key+"` > '0' AND `"+key+"` < '"+str(ceil[key])+"' AND "+where+" ORDER BY "+key+" DESC"
                cur.execute(stringSQL)
                List = cur.fetchall()
                dist = 9999999999999
                pos = 0
                for i in range(0, count-s+1):
                    _sum = 0
                    tmpList = []
                    for j in range(i, i+s-1):
                        tmpList.append(log(List[j][0]))
                    if len(tmpList) == 0:
                        _tmp = 0
                    else:
                        _tmp = variance(tmpList)
                    if (_tmp < dist):
                        dist = _tmp
                        pos = i
                if key not in v:
                    v[key] = {}
                if len(List) == 0:
                    v[key]['high'] = 0
                    v[key]['low'] = 0
                else:
                    v[key]['high'] = List[pos][0]
                    v[key]['low'] = List[pos+s-1][0]
                highStr = highStr + "'"+str(v[key]['high'])+"',"
                lowStr = lowStr + "'"+str(v[key]['low'])+"',"
                
                #报告数据生成
                if _k == "3sigma":
                    stringSQL = "SELECT avg("+key+") FROM "+SRCDB+" WHERE `"+key+"` < "+str(v[key]['high'])+" AND `"+key+"` > '"+str(v[key]['low'])+"'"
                    cur.execute(stringSQL)
                    stringSQL = "UPDATE "+SRCDB+" SET `"+key+"` = '"+str(cur.fetchone()[0])+"' WHERE `platform_id` = 'strategyC' AND `date` = '"+str(date)+"'"
                    cur.execute(stringSQL)
            stringSQL = "INSERT INTO "+table[_k]+"(`date`, `type`, "+keyStr[:-1]+") VALUES('"+str(date)+"', 'high', "+highStr[:-1]+")"
            cur.execute(stringSQL)
            conn.commit()
            stringSQL = "INSERT INTO "+table[_k]+"(`date`, `type`, "+keyStr[:-1]+") VALUES('"+str(date)+"', 'low', "+lowStr[:-1]+")"
            cur.execute(stringSQL)
            conn.commit()

        #AVE
        aveKeys = ["weekly_ave_investment", "weekly_ave_investment_old", "weekly_ratio_new_old", "weekly_loan_period", "weekly_ave_lending_per_borrower", "weekly_ave_lending_per_bid", "weekly_ave_investment_per_bid", "weekly_ave_bid_close_time"]
        aveKeys_all = aveKeys + ["weekly_lending", "weekly_total_investor", "weekly_new_investor", "weekly_total_borrower"]
        aveValue = {}
        aveStore = {}
        for key in aveKeys:
            aveValue[key] = 0

        if date <= LINEDATE:
            stringSQL = "SELECT "+','.join(aveKeys_all)+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND "+where
        else:
            stringSQL = "SELECT "+','.join(aveKeys_all)+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND `weekly_ave_investment` < '"+str(ceil['weekly_ave_investment'])+"' AND "+where
        inlineCur.execute(stringSQL)
        for _list in inlineCur.fetchall():
            for i in range(0,len(_list)):
                if aveKeys_all[i] not in aveStore:
                    aveStore[aveKeys_all[i]] = []
                aveStore[aveKeys_all[i]].append(_list[i])
        aveValue['weekly_ave_investment'] = ave_weights_quantile(aveStore,'weekly_ave_investment','weekly_total_investor',_3SIGMA)
        
        aveStore.clear()
        if date <= LINEDATE:
            stringSQL = "SELECT "+','.join(aveKeys_all)+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND "+where
        else:
            stringSQL = "SELECT "+','.join(aveKeys_all)+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND `weekly_ave_investment_old` < '"+str(ceil['weekly_ave_investment_old'])+"' AND "+where
        inlineCur.execute(stringSQL)
        for _list in inlineCur.fetchall():
            for i in range(0,len(_list)):
                if aveKeys_all[i] not in aveStore:
                    aveStore[aveKeys_all[i]] = []
                aveStore[aveKeys_all[i]].append(_list[i])
        aveStore['weekly_old_investor'] = list_minus(aveStore['weekly_total_investor'],aveStore['weekly_new_investor'])
        aveValue['weekly_ave_investment_old'] = ave_weights_quantile(aveStore,'weekly_ave_investment_old','weekly_old_investor',_3SIGMA)
        
        aveStore.clear()
        if date <= LINEDATE:
            stringSQL = "SELECT "+','.join(aveKeys_all)+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND "+where
        else:
            stringSQL = "SELECT "+','.join(aveKeys_all)+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND `weekly_ave_investment_per_bid` < '"+str(ceil['weekly_ave_investment_per_bid'])+"' AND "+where
        inlineCur.execute(stringSQL)
        for _list in inlineCur.fetchall():
            for i in range(0,len(_list)):
                if aveKeys_all[i] not in aveStore:
                    aveStore[aveKeys_all[i]] = []
                aveStore[aveKeys_all[i]].append(_list[i])
        aveStore['weekly_bid'] = list_divide(aveStore['weekly_lending'],aveStore['weekly_ave_investment_per_bid'])
        aveValue['weekly_ave_investment_per_bid'] = sum_quantile(aveStore,'weekly_lending',_3SIGMA)/sum_quantile(aveStore,'weekly_bid',_3SIGMA)
        
        aveStore.clear()
        if date <= LINEDATE:
            stringSQL = "SELECT "+','.join(aveKeys_all)+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND "+where
        else:
            stringSQL = "SELECT "+','.join(aveKeys_all)+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND `weekly_ratio_new_old` < '"+str(ceil['weekly_ratio_new_old'])+"' AND "+where
        inlineCur.execute(stringSQL)
        for _list in inlineCur.fetchall():
            for i in range(0,len(_list)):
                if aveKeys_all[i] not in aveStore:
                    aveStore[aveKeys_all[i]] = []
                aveStore[aveKeys_all[i]].append(_list[i])
        aveStore['weekly_old_investor'] = list_minus(aveStore['weekly_total_investor'],aveStore['weekly_new_investor'])
        aveValue['weekly_ratio_new_old'] = sum_quantile(aveStore,'weekly_new_investor',_3SIGMA)/sum_quantile(aveStore,'weekly_old_investor',_3SIGMA)
        
        aveStore.clear()
        if date <= LINEDATE:
            stringSQL = "SELECT "+','.join(aveKeys_all)+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND "+where
        else:
            stringSQL = "SELECT "+','.join(aveKeys_all)+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND `weekly_ave_lending_per_borrower` < '"+str(ceil['weekly_ave_lending_per_borrower'])+"' AND "+where
        inlineCur.execute(stringSQL)
        for _list in inlineCur.fetchall():
            for i in range(0,len(_list)):
                if aveKeys_all[i] not in aveStore:
                    aveStore[aveKeys_all[i]] = []
                aveStore[aveKeys_all[i]].append(_list[i])
        aveValue['weekly_ave_lending_per_borrower'] = ave_weights_quantile(aveStore,'weekly_ave_lending_per_borrower','weekly_total_borrower',_3SIGMA) 
        
        aveStore.clear()
        if date <= LINEDATE:
            stringSQL = "SELECT "+','.join(aveKeys_all)+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND "+where
        else:
            stringSQL = "SELECT "+','.join(aveKeys_all)+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND `weekly_ave_lending_per_bid` < '"+str(ceil['weekly_ave_lending_per_bid'])+"' AND "+where
        inlineCur.execute(stringSQL)
        for _list in inlineCur.fetchall():
            for i in range(0,len(_list)):
                if aveKeys_all[i] not in aveStore:
                    aveStore[aveKeys_all[i]] = []
                aveStore[aveKeys_all[i]].append(_list[i])
        aveStore['weekly_bid'] = list_divide(aveStore['weekly_lending'],aveStore['weekly_ave_investment_per_bid'])
        aveValue['weekly_ave_lending_per_bid'] = sum_quantile(aveStore,'weekly_lending',_3SIGMA)/sum_quantile(aveStore,'weekly_bid',_3SIGMA)
        
        aveStore.clear()
        if date <= LINEDATE:
            stringSQL = "SELECT "+','.join(aveKeys_all)+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND "+where
        else:
            stringSQL = "SELECT "+','.join(aveKeys_all)+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND `weekly_loan_period` < '"+str(ceil['weekly_loan_period'])+"' AND "+where
        inlineCur.execute(stringSQL)
        for _list in inlineCur.fetchall():
            for i in range(0,len(_list)):
                if aveKeys_all[i] not in aveStore:
                    aveStore[aveKeys_all[i]] = []
                aveStore[aveKeys_all[i]].append(_list[i])
        aveValue['weekly_loan_period'] = ave_weights_quantile(aveStore,'weekly_loan_period','weekly_lending',_3SIGMA)
        
        aveStore.clear()
        if date <= LINEDATE:
            stringSQL = "SELECT "+','.join(aveKeys_all)+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND "+where
        else:
            stringSQL = "SELECT "+','.join(aveKeys_all)+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"' AND `weekly_ave_bid_close_time` < '"+str(ceil['weekly_ave_bid_close_time'])+"' AND "+where
        inlineCur.execute(stringSQL)
        for _list in inlineCur.fetchall():
            for i in range(0,len(_list)):
                if aveKeys_all[i] not in aveStore:
                    aveStore[aveKeys_all[i]] = []
                aveStore[aveKeys_all[i]].append(_list[i])
        aveValue['weekly_ave_bid_close_time'] = ave_weights_quantile(aveStore, 'weekly_ave_bid_close_time', 'weekly_lending', _2SIGMA)
        
        for key in aveKeys:
            stringSQL = "UPDATE "+table["avg"]+" SET `"+key+"` = '"+str(aveValue[key])+"' WHERE `date` = '"+str(date)+"'"
            inlineCur.execute(stringSQL)                
            conn.commit()
