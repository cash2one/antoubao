#!/usr/bin/python
#coding=utf-8
import numpy as np
from scipy import interpolate
import time
import hashlib
from atbtools.header import *
from atbtools.mysqlTools import *
from atbtools.computeTools import *

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
    _start_time = time.time()
    conn_dev=MySQLdb.connect(host=DEVHOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT) 
    conn_ddpt=MySQLdb.connect(host=DDPT_DATAHOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT) 
    cur_dev=getCursors(conn_dev)
    cur_ddpt=getCursors(conn_ddpt)
    initializeCursors(cur_dev, cur_ddpt)
    SRCDB_R = "platform_alert_info_R"
    SRCDB_E3 = "E3_quantitative_score"
   
    cur_dev.execute("TRUNCATE " + SRCDB_R)
    conn_dev.commit()
 
    del_list = ["date", "id", "platform_id", "platform_name", "provision_of_risk_num", "cap_background"]
    field_list = getAllColumnsFromTable(cur_ddpt, SRCDB_E3, del_list = del_list, merge_list = None)
    field_number = len(field_list)
    
    date_list = getDifferentFieldlist(SRCDB_E3, cur_ddpt, "date")
    date_number = len(date_list)
    for i in range(1, date_number):
        date = date_list[i]
        print date
        last_date = date_list[i - 1]
        platform_name_list = getDifferentFieldlistByDate(SRCDB_E3, cur_ddpt, "platform_name", date)
        for platform_name in platform_name_list:
            print platform_name
            platform_id = hashlib.md5(platform_name).hexdigest()[0:10]
            v = {}.fromkeys(field_list, "")
            for field in field_list:
                #W1
                last7week_list = getlatestValueByDate(SRCDB_E3, cur_ddpt, field, platform_name, date, 7)
                if last7week_list != None:
                    if len(last7week_list) < 7 or last7week_list[6] == 0:
                        v[field] += "f1"
                    else:
                        ret = warning1(last7week_list)
                        if ret >= 0.5:
                            v[field] += "w1" 
                        
                #W2
                last4week_list = getlatestValueByDate(SRCDB_E3, cur_ddpt, field, platform_name, date, 4)
                if last4week_list != None:
                    ret = warning2(last4week_list)
                    if ret == 2:
                        v[field] += "f2"
                    else:
                        v[field] += "w2" 

                #W3
                this_date_value = getValueByDate(SRCDB_E3, cur_ddpt, field, platform_name, date)
                if this_date_value == None:
                    continue
#                 print field, this_date_value
                last_date_value = getValueByDate(SRCDB_E3, cur_ddpt, field, platform_name, last_date)
                if last_date_value != None:
                    ret = warning3(this_date_value, last_date_value)
                    if (ret == 1):
                        v[field] += "w3"
                    
                #W4
                if field in ["turnover_registed", "weekly_ave_bid_close_time", "weekly_ratio_new_old", "not_return_yet", "outstanding_loan"]:
                    stringSQL = "SELECT `" + field + "` FROM platform_quantitative_data_3sigma_O WHERE `date` = '" + date + "'  ORDER BY `type` DESC LIMIT 2"
                    ret = cur_dev.execute(stringSQL)
                    if ret != 0:
                        sigma3_low, sigma3_high = cur_dev.fetchall()
                        ret = warning4(this_date_value, sigma3_low, sigma3_high)
                        if (ret == 1):
                            v[field] += "w4"
                
                #W5
                ret = warning5(this_date_value, -10000, 10000)
                if (ret == 1):
                    v[field] += "w5"     
            field_list_new = ["platform_name", "platform_id", "date"] + field_list         
            value_list = [platform_name, platform_id, date]
            for field in field_list:
                value_list.append(v[field])
            stringSQL = "INSERT INTO " + SRCDB_R + "(`" + "`,`".join(field_list_new) + "`) VALUES('" + "','".join(value_list) + "')"
#             print stringSQL
            cur_dev.execute(stringSQL)
            conn_dev.commit()
    closeCursors(cur_dev, cur_ddpt)
    closeConns(conn_dev, conn_ddpt)  
    _end_time = time.time()
    print "The whole program costs " + str(_end_time - _start_time) + " seconds." 