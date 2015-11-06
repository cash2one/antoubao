#!/usr/bin/python
#coding=utf-8
import numpy as np
from scipy import interpolate
import time
import hashlib
from atbtools.header import *
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from utils import *

#线性拟合结果
def linearfit(x,y):
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
    
#B样条插值(7周数据)的预测值误差
def warning1(_list, _threshold_value):
    if None in _list or _list[6] == 0:
        return "f1"
    else:
        y = _list[0:6]
        x = np.array(range(0,6))
        x_new = np.array(range(0,7))
    #     f_linear = interpolate.interp1d(y,x)
        tck = interpolate.splrep(x,y) #B样条插值函数
        x_bspline = interpolate.splev(x_new,tck) #B样条插值结果
        value = abs(float(x_bspline[6]/_list[6]) - 1)
        if value >= _threshold_value:
            return "w1"
        else:
            return ""
    
#线性拟合(4周数据)的预测值误差
def warning2(_list, _threshold_value):
    if None in _list:
        return "f2"
    else:
        r = linearfit([1,2,3,4],_list)[2]
        if (abs(r) > _threshold_value):
            return "w2"
        else:
            return ""

#本周和上一周的差的绝对值
def warning3(_list, _threshold_value):
    if None in _list:
        return"f3"
    else:
        if abs(_list[0] - _list[1]) > _threshold_value:
            return "w3"
        else:
            return ""
    
#是否在拟定最大值和最小值之间（包含等于）
def warning4(_value, _threshold_list):
    _minn = min(_threshold_list)
    _maxx = max(_threshold_list)
    if None == _value:
        return "f4"
    else:
        if (_value < _minn) or (_value > _maxx):
            return "w4"
        else:
            return ""
        
#是否在拟定最大值和最小值之间（包含等于）
def warning5(_list, _threshold_list):
    threshold_value_min = min(_threshold_list)
    threshold_value_max = max(_threshold_list)
    if _list[-1] != None and _list[-3] != None:
        numerator = float(abs(_list[-1] - _list[-3]))
    else:
        return "f5"
    denominator = 0.0
    count = 0
    for i in range(7):
        if _list[i + 2] != None and _list[i] != None:
            denominator += abs(_list[i + 2] - _list[i])
            count += 1
    if count == 0 or denominator == 0:
        return "f5"
    else:
        denominator /= count
    value = numerator / denominator
    if value <= threshold_value_min or value >= threshold_value_max:
        return "w5"
    else:
        return ""

#本周和上一周的差的绝对值
def warning6(_list, _threshold_value):
    if None in _list:
        return"f6"
    else:
        if abs(_list[0] - _list[1]) > _threshold_value:
            return "w6"
        else:
            return ""
        
#计算每个平台每个时间各个指标的punishment
def computeWarnings(_warning, _date_list, _value_dict, _field_list, _threshold_value):
    warning_dict = {}
    date_number = len(_date_list)
    for platform_name in _value_dict:
        if platform_name not in warning_dict:
            warning_dict[platform_name] = {}
        for i in range(0,date_number):
            date = _date_list[i]
            if date not in warning_dict[platform_name]:
                warning_dict[platform_name][date] = {}.fromkeys(_field_list, "")
             
            if  "w1" in _warning:
                #w1，最近7周B样条插值
                if i >= 6:
                    for field in _field_list:
                        last7week_list = _value_dict[platform_name][field][i-6:i+1]
                        warning_dict[platform_name][date][field] += warning1(last7week_list, _threshold_value)
             
                              
            if  "w2" in _warning:
                #w2，最近4周线性拟合
                if i >= 3:
                    for field in _field_list:
                        last4week_list = _value_dict[platform_name][field][i-3:i+1]
                        warning_dict[platform_name][date][field] += warning2(last4week_list, _threshold_value)
                     
            if  "w3" in _warning:
                #w3，相邻两周数据差
                if i >= 1:
                    for field in _field_list:
                        last2week_list = _value_dict[platform_name][field][i-1:i+1]
                        warning_dict[platform_name][date][field] += warning3(last2week_list, _threshold_value)
                        
            if  "w4" in _warning:
                #w4，特殊指标是否在3sigma内
                for field in _field_list:
                    this_date_value = _value_dict[platform_name][field][i]
                    warning_dict[platform_name][date][field] += warning4(this_date_value, [sigma3_dict_low[field][i], sigma3_dict_high[field][i]])
             
            if  "w5" in _warning:            
                if i >= 8:
                    for field in _field_list:
                        last9week_list = _value_dict[platform_name][field][i-8:i+1]
                        warning_dict[platform_name][date][field] += warning5(last9week_list, _threshold_value)
            
            if  "w6" in _warning:
                #w3，相邻两周数据差
                if i >= 1:
                    for field in _field_list:
                        last2week_list = _value_dict[platform_name][field][i-1:i+1]
                        warning_dict[platform_name][date][field] += warning6(last2week_list, _threshold_value)
                         
    return warning_dict

#输出结果统计
def getWarningStatistics(_warning_dict, _w, _f):
    ratio = -1 #所有出现过某个w的站中，坏站的比例是多少
    ave_bad_w = -1 #所有出现过w的坏站中，平均每个坏站出现了几次w
    ave_good_w = -1 #所有出现过w的好站中，平均每个好站出现了几次w
    ave_bad_f = -1 #所有出现过f的坏站中，平均每个坏站出现了几次f
    ave_good_f = -1 #所有出现过f的好站中，平均每个好站出现了几次f
    ratio_bad = -1 #出现w的坏站占全部坏站的比例
    ratio_good = -1 #出现w的好站占全部好站的比例

    result_dict = {}.fromkeys(result_field_list, -1)
    w_appeared_list = []
    f_appeared_list = []
    w_number_dict = {}
    f_number_dict = {}
    platform_number_bad = 0 #坏站个数
    platform_number_good = 0 #好站个数
    for platform_name in _warning_dict:
        if status_dict[platform_name] < 0.89:
            platform_number_bad += 1
        else:
            platform_number_good += 1
        w_appeared = 0
        f_appeared = 0
        w_number_dict[platform_name] = 0
        f_number_dict[platform_name] = 0
        for date in date_list_E3:
            value_list = _warning_dict[platform_name][date].values()
            count_number_w = value_list.count(_w)
            count_number_f = value_list.count(_f)
            if count_number_w != 0:
                w_appeared = 1
                w_number_dict[platform_name] += count_number_w
            if count_number_f != 0:
                f_appeared = 1
                f_number_dict[platform_name] += count_number_f
        if w_appeared == 1:        
            w_appeared_list.append(platform_name)
        if f_appeared == 1:        
            f_appeared_list.append(platform_name)
    
    w_appeared_platform_number = len(w_appeared_list) #出现w的平台个数
#     f_appeared_platform_number = len(f_appeared_list) #出现f的平台个数
    w_appeared_platform_number_bad = 0 #出现w的坏平台个数
    w_appeared_platform_number_good = 0 #出现w的好平台个数
    f_appeared_platform_number_bad = 0 #出现f的坏平台个数
    f_appeared_platform_number_good = 0 #出现f的好平台个数
    w_appeared_total_number_bad = 0 #坏平台中w的总数
    w_appeared_total_number_good = 0 #好平台中w的总数
    f_appeared_total_number_bad = 0 #坏平台中f的总数
    f_appeared_total_number_good = 0 #好平台中f的总数
    
    for platform_name in w_appeared_list:       
        if status_dict[platform_name] < 0.89:
            w_appeared_platform_number_bad += 1
            w_appeared_total_number_bad += w_number_dict[platform_name]
        else:
            w_appeared_platform_number_good += 1
            w_appeared_total_number_good += w_number_dict[platform_name]
    
    for platform_name in f_appeared_list:       
        if status_dict[platform_name] < 0.89:
            f_appeared_platform_number_bad += 1
            f_appeared_total_number_bad += f_number_dict[platform_name]
        else:
            f_appeared_platform_number_good += 1
            f_appeared_total_number_good += f_number_dict[platform_name]
    
    if w_appeared_platform_number != 0:
        result_dict["ratio"] = float(w_appeared_platform_number_bad) / w_appeared_platform_number
    if w_appeared_platform_number_bad != 0:
        result_dict["ave_bad_w"] = float(w_appeared_total_number_bad) / w_appeared_platform_number_bad / date_number_E3 
    if w_appeared_platform_number_good != 0:
        result_dict["ave_good_w"] = float(w_appeared_total_number_good) / w_appeared_platform_number_good / date_number_E3 
    if f_appeared_platform_number_bad != 0:
        result_dict["ave_bad_f"] = float(f_appeared_total_number_bad) / f_appeared_platform_number_bad / date_number_E3 
    if f_appeared_platform_number_good != 0:
        result_dict["ave_good_f"] = float(f_appeared_total_number_good) / f_appeared_platform_number_good / date_number_E3 
    if platform_number_bad != 0:
        result_dict["ratio_bad"] = float(w_appeared_platform_number_bad) / platform_number_bad 
    if platform_number_good != 0:
        result_dict["ratio_good"] = float(w_appeared_platform_number_good) / platform_number_good
              
    return result_dict

#统一格式字符串输出
def getStringForOutput(_result_dict):
    result_str = ""
    for field in result_field_list:
        result_str += "    " + field + " = " + "%.4f" % _result_dict[field]
    result_str += "\n\n"
    print result_str
    return result_str

if __name__ == '__main__':
    _start_time = time.time()
    
    #获取连接
    conn_dev=MySQLdb.connect(host=DEVHOST_OUT, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT) 
    conn_ddpt_data=MySQLdb.connect(host=DDPT_DATAHOST_OUT, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT) 
    conn_db=MySQLdb.connect(host=DBHOST_OUT, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT) 
    cur_dev=getCursors(conn_dev)
    cur_ddpt_data=getCursors(conn_ddpt_data)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_dev, cur_ddpt_data, cur_db)
    
    SRCDB_R = "platform_alert_info_R"
    SRCDB_E3 = "E3_quantitative_score"
    SRCDB_H = "H_score"
    SRCDB_SIGMA3 = "K_statis_3sigma"
    SRCDB_Y = "total_status"
   
    cur_dev.execute("DELETE FROM " + SRCDB_R)
    conn_dev.commit()
 
    #准备源数据列表
    del_list = ["date", "id", "platform_id", "platform_name", "source"]
    field_list_E3 = getAllColumnsFromTable(cur_ddpt_data, SRCDB_E3, del_list = del_list, merge_list = None)
    field_number_E3 = len(field_list_E3)
#     field_list_H = getAllColumnsFromTable(cur_ddpt_data, SRCDB_H, del_list = del_list, merge_list = None)
    field_list_H = ["capital_adequacy_ratio", "activeness_credibility", "distribution", "mobility", "security", "pellucidity", "growth"]
    field_number_H = len(field_list_H)
     
    w4_field_list = ["turnover_registered", "weekly_ave_bid_close_time", "weekly_ratio_new_old", "not_returned_yet", "outstanding_loan"]
    w4_field_number = len(w4_field_list)
     
    date_list_E3 = getDifferentFieldlist(SRCDB_E3, cur_ddpt_data, "date")
    date_number_E3 = len(date_list_E3)
    date_list_H = getDifferentFieldlist(SRCDB_H, cur_ddpt_data, "date")
    date_number_H = len(date_list_H)
    platform_name_list_E3 = getDifferentFieldlist(SRCDB_E3, cur_ddpt_data, "platform_name")
    platform_name_number_E3 = len(platform_name_list_E3)
    platform_name_list_H = getDifferentFieldlist(SRCDB_H, cur_ddpt_data, "platform_name")
    platform_name_number_H = len(platform_name_list_H)
     
    #获取E3中所有数据，没有的用None代替
    value_dict_E3 = {}
    for platform_name in platform_name_list_E3:
        value_dict_E3[platform_name] = {}
        for field in field_list_E3:
            value_dict_E3[platform_name][field] = [None] * date_number_E3
    stringSQL = "SELECT `platform_name`, `date`, `" + "`, `".join(field_list_E3) + "` FROM " + SRCDB_E3
    print "正在从数据库传输E3数据回本地..."
    cur_ddpt_data.execute(stringSQL)
    rows = cur_ddpt_data.fetchall()
    for row in rows:
        platform_name = row[0]
        date = row[1]
        value_list = row[2:]
        date_index = date_list_E3.index(date)
        for i in range(field_number_E3):
            value_dict_E3[platform_name][field_list_E3[i]][date_index] = value_list[i]
 
    #获取H中所有数据，没有的用None代替
    value_dict_H = {}
    for platform_name in platform_name_list_H:
        value_dict_H[platform_name] = {}
        for field in field_list_H:
            value_dict_H[platform_name][field] = [None] * date_number_H
    stringSQL = "SELECT `platform_name`, `date`, `" + "`, `".join(field_list_H) + "` FROM " + SRCDB_H
    print "正在从数据库传输H数据回本地..."
    cur_ddpt_data.execute(stringSQL)
    rows = cur_ddpt_data.fetchall()
    for row in rows:
        platform_name = row[0]
        date = row[1]
        value_list = row[2:]
        date_index = date_list_H.index(date)
        for i in range(field_number_H):
            value_dict_H[platform_name][field_list_H[i]][date_index] = value_list[i]
            
    #获取3sigma数据
    sigma3_dict_high = {}
    sigma3_dict_low = {}
    for field in w4_field_list:
        sigma3_dict_high[field] = [None] * date_number_E3
        sigma3_dict_low[field] = [None] * date_number_E3
    stringSQL = "SELECT `type`, `date`, `" + "`, `".join(w4_field_list) + "` FROM " + SRCDB_SIGMA3
    cur_ddpt_data.execute(stringSQL)
    rows = cur_ddpt_data.fetchall()
    for row in rows:
        _type = row[0]
        date = row[1]
        value_list = row[2:]
        date_index = date_list_E3.index(date)
        for i in range(w4_field_number):
            if _type == "h":
                sigma3_dict_high[w4_field_list[i]][date_index] = value_list[i]
            else:
                sigma3_dict_low[w4_field_list[i]][date_index] = value_list[i]
     
    #获得所有平台的status属性
    status_dict = {}
    stringSQL = "SELECT A.platform_name, A.status FROM total_status AS A,(SELECT `platform_name`, MAX(`date`) AS `date` FROM total_status GROUP BY `platform_name`) AS B WHERE A.platform_name = B.platform_name AND A.`date` = B.`date`"
    ret = cur_db.execute(stringSQL)
    rows = cur_db.fetchall()
    for row in rows:
        platform_name = row[0]
        status = row[1]
        status_dict[platform_name] = status
    
    #开始计算预警
    warning_dict = getWarningDict()
    result_field_list = ["ratio", "ave_bad_w", "ave_good_w", "ave_bad_f", "ave_good_f", "ratio_bad", "ratio_good"]
    warning_file = open("warning_statistics.txt", 'w')
    
    w1_value = warning_dict["w1"]["weight"]
    _str = "W1 value = " + str(w1_value) + "\n"
    print _str
    warning_file.write(_str)
    warning_dict_1 = computeWarnings("w1", date_list_E3, value_dict_E3, field_list_E3, w1_value)
    output_dict = getWarningStatistics(warning_dict_1, "w1", "f1")
    warning_file.write(getStringForOutput(output_dict))
  
    w2_value = warning_dict["w2"]["weight"]
    _str = "W2 value = " + str(w2_value) + "\n"
    print _str
    warning_file.write(_str)
    warning_dict_2 = computeWarnings("w2", date_list_E3, value_dict_E3, field_list_E3, w2_value)
    output_dict = getWarningStatistics(warning_dict_2, "w2", "f2")
    warning_file.write(getStringForOutput(output_dict))
           
    w3_value = warning_dict["w3"]["weight"]
    _str = "W3 value = " + str(w3_value) + "\n"
    print _str
    warning_file.write(_str)
    warning_dict_3 = computeWarnings("w3", date_list_E3, value_dict_E3, field_list_E3, w3_value)
    output_dict = getWarningStatistics(warning_dict_3, "w3", "f3")
    warning_file.write(getStringForOutput(output_dict))
    
    _str = "W4\n"
    print _str
    warning_file.write(_str)
    warning_dict_4 = computeWarnings("w4", date_list_E3, value_dict_E3, w4_field_list, -1)
    output_dict = getWarningStatistics(warning_dict_4, "w4", "f4")
    warning_file.write(getStringForOutput(output_dict))
          
    w5_value_min = warning_dict["w5"]["weight_min"]
    w5_value_max = warning_dict["w5"]["weight_max"]
    _str = "W5 value_min = " + str(w5_value_min) + ", value_min = " + str(w5_value_max) + "\n"
    print _str
    warning_file.write(_str)
    warning_dict_5 = computeWarnings("w5", date_list_E3, value_dict_E3, field_list_E3, [w5_value_min, w5_value_max])
    output_dict = getWarningStatistics(warning_dict_5, "w5", "f5")
    warning_file.write(getStringForOutput(output_dict))
    
    w6_value = warning_dict["w6"]["weight"]
    _str = "W6 value = " + str(w6_value) + "\n"
    print _str
    warning_file.write(_str)
    warning_dict_6 = computeWarnings("w6", date_list_H, value_dict_H, field_list_H, w6_value)
    output_dict = getWarningStatistics(warning_dict_6, "w6", "f6")
    warning_file.write(getStringForOutput(output_dict))
            
    warning_file.close()

    #将最后一次结果插入数据库
    date_list = list(set(date_list_E3) | set(date_list_H))
    platform_name_list = list(set(platform_name_list_E3) | set(platform_name_list_H))
    field_list = list(set(field_list_E3) | set(field_list_H))
    warning_dict = {}
    for platform_name in platform_name_list:
        warning_dict[platform_name] = {}
        for date in date_list:
            warning_dict[platform_name][date] = {}.fromkeys(field_list, "")
    
    for dict_temp in [warning_dict_1, warning_dict_2, warning_dict_3, warning_dict_4, warning_dict_5, warning_dict_6]:
        for platform in dict_temp:
            for date in dict_temp[platform]:
                for field in dict_temp[platform][date]:
                    warning_dict[platform][date][field] += dict_temp[platform][date][field]
    
    print "向" + SRCDB_R + "写入数据..."
    platform_number = len(platform_name_list)
    count = 0
    for platform_name in platform_name_list:
        print platform_name
        count += 1
        print str(count) + "//" + str(platform_number)
        platform_id = hashlib.md5(platform_name).hexdigest()[0:10]
        for date in date_list:
            field_list_new = ["platform_name", "platform_id", "date"] + field_list       
            value_list = [platform_name, platform_id, date]
            for field in field_list:
                value_list.append(warning_dict[platform_name][date][field])
            if platform_name in status_dict:
                field_list_new += ['status']
                value_list += [str(status_dict[platform_name])]
            stringSQL = "INSERT INTO " + SRCDB_R + "(`" + "`,`".join(field_list_new) + "`) VALUES('" + "','".join(value_list) + "')"
#             print stringSQL
            cur_dev.execute(stringSQL)
            conn_dev.commit()

        
    closeCursors(cur_dev, cur_ddpt_data, cur_db)
    closeConns(conn_dev, conn_ddpt_data, conn_db)  
    _end_time = time.time()
    print "The whole program costs " + str(_end_time - _start_time) + " seconds." 