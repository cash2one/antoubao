#!/usr/bin/python
#coding=utf-8
import math
import numpy as np
from scipy import interpolate
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

#B样条插值(7周数据)的预测值误差
def warning1(temp):
    x = temp[0:6]
    y = np.array(range(0,6))
    y_new = np.array(range(0,7))
#     f_linear = interpolate.interp1d(y,x)
    tck = interpolate.splrep(y,x) #B样条插值函数
    x_bspline = interpolate.splev(y_new,tck) #B样条插值结果
    return abs(float(x_bspline[6]/temp[6])-1)

#线性拟合(4周数据)的预测值误差
def warning2(temp):
    def linefit(x,y):
        N = len(x)
        sx,sy,sxx,syy,sxy = 0,0,0,0,0
        for i in range(N):
            sx += x[i]
            sy += y[i]
            sxx += x[i]*x[i]
            syy += y[i]*y[i]
            sxy += x[i]*y[i]
        a = (sy*sx/N - sxy)/(sx*sx/N - sxx)
        b = (sy - a*sx)/N
        if (sxx-sx*sx/N)*(syy-sy*sy/N) == 0:
            r = 0
        else:
            r = abs(sy*sx/N - sxy)/math.sqrt((sxx-sx*sx/N)*(syy-sy*sy/N))
        return a,b,r
    if len(temp) < 4 or temp[3] == 0:
        return 2
    r = linefit([1,2,3,4],temp)[2]
    if (abs(r) > 0.95):
        return 1

#本周和上一周的差的绝对值
def warning3(thisweek,lastweek):
    if abs(thisweek - lastweek) > 10:
        return 1
    
#是否在拟定最大值和最小值之间（包含等于）
def warning4(value,minn,maxx):
    if (value < minn) or (value > maxx):
        return 1

#是否在拟定最大值和最小值之间（包含等于）
def warning5(value,minn,maxx):
    if (value < minn) or (value > maxx):
        return 1


if __name__ == '__main__':
    conn=MySQLdb.connect(host=DEVHOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT) 
    cur=conn.cursor()
    inlineCur=conn.cursor()
    insertCur=conn.cursor()

    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")
   
    cur.execute("TRUNCATE platform_alert_Q1")
    conn.commit()
 
    stringSQL = "SHOW FULL COLUMNS FROM platform_quantitative_data_E3"
    cur.execute(stringSQL)
    arrKeys = []
    for col in cur.fetchall():
        if (col[0] == "date") or (col[0] == "id") or (col[0] == "platform_id") or (col[0] == "platform_name") or (col[0] == "provision_of_risk_num"):
            continue
        arrKeys.append(col[0])
    arrKeys_number = len(arrKeys)
    #E3中最近一周的时间戳
    stringSQL = "SELECT DISTINCT date FROM platform_quantitative_data_E3 ORDER BY `date` DESC LIMIT 1"
    cur.execute(stringSQL)
    date = cur.fetchone()[0]
    
    #E3最近一周的数据
    stringSQL = "SELECT platform_id, platform_name FROM platform_quantitative_data_E3 WHERE `date` = '"+str(date)+"'"
    cur.execute(stringSQL)
    for plats in cur.fetchall():
        platId = plats[0]
        platName = plats[1]
        
        #E3最近7周的时间字符串
        stringSQL = "SELECT date FROM platform_quantitative_data_E3 WHERE `platform_id` = '"+platId+"' ORDER BY date DESC LIMIT 7"
        inlineCur.execute(stringSQL)
        dates = ""
        i = 0
        for date in inlineCur.fetchall():
            if (i == 0):
                d = str(date[0]) #最近一周
            elif (i == 1): #上一周
                lastweek_d = str(date[0])
            dates = dates+"`date` = '"+str(date[0])+"' OR "
            i += 1

        score = 0
        punishment = 0
        punishment_info = []
        #当周的罚分和罚分记录
        stringSQL = "SELECT score,punishment,punishment_info FROM platform_score_P WHERE `platform_id` = '"+platId+"' AND `date` = '"+d+"'"
        ret = inlineCur.execute(stringSQL)
        if ret == 0:
            continue
        score,punishment,punishment_info = inlineCur.fetchone()
        
        stringSQL = "SELECT "+','.join(arrKeys)+" FROM platform_quantitative_data_3sigma_O WHERE `date` = '" + d + "'  ORDER BY `type` DESC LIMIT 2"
        ret = inlineCur.execute(stringSQL)
        if ret == 0:
            continue
        tempsigma = inlineCur.fetchall()
 
        tempthreshold = [-10000, 10000]
        
        #最近7周的数据,从前到后排列
        stringSQL = "SELECT "+','.join(arrKeys)+" FROM platform_quantitative_data_E3 WHERE `platform_id` = '"+platId+"' AND ("+dates[:-4]+") ORDER BY `date` AESC"
        _number = inlineCur.execute(stringSQL)
        temp = inlineCur.fetchall()
        q = {}
        q['platform_id'] = platId
        q['platform_name'] = platName
        v = {}
        w = 0
        for i in range(arrKeys_number): #指标数
            if (arrKeys[i] not in v):
                v[arrKeys[i]] = ""
            
            #W1
            tmp = []
            for j in range(_number): #周数
                tmp.append(temp[j][i])
            
            #tmp为每一个指标最近7周的数据（实际数目可能小于7）
            ret = 10000
            if len(tmp) < 7 or tmp[6] == 0:
                v[arrKeys[i]] += "f1"
            else:
                ret = warning1(tmp)
                #最近一周相应指标的w1阈值
                stringSQL = "SELECT "+arrKeys[i]+" FROM platform_alert_Q2 WHERE `date` <= '" + str(d) + " ORDER BY `date` DESC LIMIT 1"
                inlineCur.execute(stringSQL)
                lim = inlineCur.fetchone()[0]

                if ret > lim and ret > 0.2:
                    v[arrKeys[i]] += "w1"
                    score -= 0.1
                    punishment -= 0.1
                    w += 1
            q[arrKeys[i]] = ret
            
            #W2
            tmp = []
            for j in range(0, _number):
                tmp.append(temp[j][i])

            ret = warning2(tmp)
            if (ret == 1):
                v[arrKeys[i]]+="w2"
                #score += -0.5
            elif (ret == 2):
                v[arrKeys[i]]+="f2"
            
            #W4
            if (arrKeys[i] == "turnover_registed") or (arrKeys[i] == "weekly_ave_bid_close_time") or (arrKeys[i] == "weekly_ratio_new_old") or (arrKeys[i] == "not_return_yet") or (arrKeys[i] == "outstanding_loan"):
                ret = warning4(temp[_number - 1][i],tempsigma[0][i],tempsigma[1][i])
                if (ret == 1):
                    v[arrKeys[i]]+="w4"
                    score -= 0.1
                    punishment -= 0.1
                    w += 1
            #W5
            ret = warning5(temp[_number - 1][i],float(tempthreshold[0]),float(tempthreshold[1]))
            if (ret == 1):
                v[arrKeys[i]]+="w5"
                score += -0.1
                punishment += -0.1
                w += 1

        ks = ""
        s = ""
        for (key, value) in q.items():
            ks = ks+"`"+key+"`,"
            s = s+"'"+str(value)+"',"

        stringSQL = "INSERT INTO platform_alert_Q1(`date`, "+ks[:-1]+") VALUES('"+str(d)+"', "+s[:-1]+")"
        inlineCur.execute(stringSQL)
        conn.commit()
        
        #W3
        stringSQL = "SHOW FULL COLUMNS FROM platform_score_P"
        inlineCur.execute(stringSQL)
        Keys = []
        for col in inlineCur.fetchall():
            if (col[0] == "level") or (col[0] == "score") or (col[0] == "punishment") or (col[0] == "punishment_info") or (col[0] == "date") or (col[0] == "id") or (col[0] == "platform_id") or (col[0] == "platform_name") or (col[0] == "status"):
                continue
            Keys.append(col[0])
        stringSQL = "SELECT "+','.join(Keys)+" FROM platform_score_P WHERE `platform_id` = '"+platId+"' AND (`date` = '"+str(d)+"' OR `date` = '"+str(lastweek_d)+"') ORDER BY date DESC"
        insertCur.execute(stringSQL)
        List = insertCur.fetchall()
        WW = ""
        if (len(List) == 2):     
            for i in range(0, len(List[0])):
                ret = warning3(float(List[0][i]), float(List[1][i]))
                if (ret == 1):
                    #v[Keys[i]]+="w3"
                    score -= 0.1
                    punishment -= 0.1
                    WW += "W3W"
        
        s = ""
        for (key,value) in v.items():
            s = s+"`"+key+"` = '"+value+"', "
        stringSQL = "UPDATE platform_alert_info_R SET "+s[:-2]+" WHERE `platform_id` = '"+platId+"' AND `date` = '"+d+"'"
        inlineCur.execute(stringSQL)
        conn.commit()
        stringSQL = "UPDATE platform_score_P SET `score` = '"+str(score)+"',`punishment` = '"+str(punishment)+"',`punishment_info` = '"+punishment_info+"W"+str(w)+WW+"' WHERE `platform_id` = '"+platId+"' AND `date` = '"+d+"'"  
        inlineCur.execute(stringSQL)
        conn.commit()
