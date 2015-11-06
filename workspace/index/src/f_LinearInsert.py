# /usr/bin/python
# coding=utf8

#对index_weekly_report进行线性插值
from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
import time
import sys

if __name__ == '__main__':
    _start_time = time.time()
    
    #获得连接        
    conn_dev = getConn(DEVHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_dev = getCursors(conn_dev)
    initializeCursors(cur_dev)
    
    SRCDB_INDEX = "index_weekly_report"
    value_format = "%.4f"
    
    #获得所有指标
    del_list = ["Id", "date"]
    del_list += ["money_loss_ratio_history", "bad_debt_ratio_monthly", "bad_debt_ratio_quarterly"]
    del_list += ["average_interest_rate_ALL", "average_interest_rate_aboveA", "average_interest_rate_belowA", "average_interest_rate_B++", "average_interest_rate_B+", "average_interest_rate_B", "average_interest_rate_C"]
    del_list += ["average_real_interest_rate_300"]
    field_list = getAllColumnsFromTable(cur_dev, SRCDB_INDEX, del_list)
    field_number = len(field_list)
    ignore_list = [] #["bad_debt_ratio_monthly", "bad_debt_ratio_quarterly"]
    ignore_list_index = getIndexFromList(field_list, ignore_list)
    #获得时间节点
    date_list = getDifferentFieldlist(SRCDB_INDEX, cur_dev, "date")
    date_number = len(date_list)
    date_min = date_list[0]
    date_max = date_list[-1]
    date_real_list = range(date_min, date_max, SECONDSPERWEEK)
    date_real_number = len(date_real_list)
    
    #初始化指标字典
    field_index_dict = {}
    for field in field_list:
        field_index_dict[field] = [0] * date_real_number
    for i in range(date_real_number):
        _date = date_real_list[i]
        if _date in date_list:
            stringSQL = "SELECT `" + "`,`".join(field_list) + "` FROM " + SRCDB_INDEX + " WHERE `date` = '" + str(_date) + "'" 
            cur_dev.execute(stringSQL)
            rets = cur_dev.fetchone()
            for j in range(field_number):
                field_index_dict[field_list[j]][i] = float(rets[j])
                
    #线性插值
    for i in range(date_real_number):
        _date = date_real_list[i]
        if _date not in date_list:
            #查找两个时间端点
            for j in range(i-1,-1,-1):
                if date_real_list[j] in date_list:
                    data_index_min = j
                    break
            for j in range(i+1,date_real_number,1):
                if date_real_list[j] in date_list:
                    data_index_max = j
                    break
            value_list = []
            for j in range(field_number):
                if j in ignore_list_index:
                    value_list.append("0")
                else:
                    value_list.append(str(calculateLinearValue(i,field_index_dict[field_list[j]], data_index_min, data_index_max)))
            field_list_temp = field_list + ["date"]
            value_list = getString(value_list) + [str(_date)]
            stringSQL = "INSERT INTO " + SRCDB_INDEX + "(`" + "`,`".join(field_list_temp) + "`) VALUES('" + "','".join(value_list) + "')"
            cur_dev.execute(stringSQL)
            conn_dev.commit()
     
    closeCursors(cur_dev)
    closeConns(conn_dev)
    _end_time = time.time()
    print "The whole program costs " + str(_end_time - _start_time) + " seconds."  
    
