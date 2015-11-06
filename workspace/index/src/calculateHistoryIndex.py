# /usr/bin/python
# coding=utf8

#1.获得指数指标的时间节点
#2.在E1表中寻找所有非坏站并依据value进行排序

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
    
    SRCDB_INDEX_TARGET = "index_platform_list"
    SRCDB_INDEX = "index_weekly_report"
    
    level_list = ["ALL", "aboveA", "belowA", "B++", "B+", "B", "C"]
    interest_rate_level_list = ["interest_rate_" + x for x in level_list]
    average_interest_rate_level_list = ["average_interest_rate_" + x for x in level_list]
    #1.获得指数指标的时间节点
    date_list = getDifferentFieldlist(SRCDB_INDEX, cur_dev, "date")
    date_number =len(date_list)
        
    stringSQL = "SELECT SUM(weekly_outstanding_loan) FROM " + SRCDB_INDEX_TARGET + " WHERE `date` = '" + str(date_list[0]) + "' AND `source` >= '0'"
    cur_dev.execute(stringSQL)
    money_loss_ratio_history_origin = float(cur_dev.fetchone()[0]) * 0.02
    for i in range(date_number):
        _date = date_list[i]
        print _date
        kv = {}
        stringSQL = "SELECT `temp_B_300` FROM " + SRCDB_INDEX + " WHERE `date` = '" + str(_date) + "'"
        cur_dev.execute(stringSQL)
        B_300 = float(cur_dev.fetchone()[0])
        B_bad_list = []
        stringSQL = "SELECT temp_B_bad FROM " + SRCDB_INDEX + " WHERE `date` <= " + str(_date) + " ORDER BY date ASC"
        cur_dev.execute(stringSQL)
        for temp_B_bad in cur_dev.fetchall():
            B_bad_list.append(float(temp_B_bad[0]))
        #money_loss_ratio_history
        k = "money_loss_ratio_history"
        insertField(conn_dev, cur_dev, SRCDB_INDEX, k, "DOUBLE DEFAULT NULL")
        kv[k] = (money_loss_ratio_history_origin + sum(B_bad_list)) / B_300
        #bad_debt_ratio_monthly
        if ((_date - date_list[0]) / SECONDSPERWEEK + 1) % WEEKSPERMONTH == 0:
            k = "bad_debt_ratio_monthly"
            insertField(conn_dev, cur_dev, SRCDB_INDEX, k, "DOUBLE DEFAULT NULL")
            kv[k] = sum(B_bad_list[-1:-1-WEEKSPERMONTH:-1]) / B_300
        #bad_debt_ratio_quarterly 
        if ((_date - date_list[0]) / SECONDSPERWEEK + 1) % WEEKSPERQUARTOR== 0:
            k = "bad_debt_ratio_quarterly"
            insertField(conn_dev, cur_dev, SRCDB_INDEX, k, "DOUBLE DEFAULT NULL")
            kv[k] = sum(B_bad_list[-1:-1-WEEKSPERQUARTOR:-1]) / B_300
        #average_interest_rage_level
        if i >= 25:
            end_date = _date - 25 * SECONDSPERWEEK
            for level in level_list:
                field1 = "weighted_weekly_outstanding_loan_" + level
                field2 = "interest_rate_" + level
                stringSQL = "SELECT SUM(`weekly_outstanding_loan_300` * `" + str(field1) + "` * `" + str(field2) +"`) / SUM(`weekly_outstanding_loan_300` * `" + str(field1) + "`) FROM " + SRCDB_INDEX + " WHERE `date` <= '" + str(_date) + "' AND `date` >= '" + str(end_date) + "'"
                #stringSQL = "SELECT AVG(`" + str(field2) + "`) FROM " + SRCDB_INDEX + " WHERE `date` <= '" + str(_date) + "' AND `date` >= '" + str(end_date) + "'"
                cur_dev.execute(stringSQL)
                k = "average_interest_rate_" + level
                kv[k] = float(cur_dev.fetchone()[0])
                insertField(conn_dev, cur_dev, SRCDB_INDEX, k, "DOUBLE DEFAULT NULL")
            stringSQL = "SELECT SUM(`weekly_outstanding_loan_300` * `real_interest_rate_300`) / SUM(`weekly_outstanding_loan_300`) FROM " + SRCDB_INDEX + " WHERE `date` <= '" + str(_date) + "' AND `date` >= '" + str(end_date) + "'"
            cur_dev.execute(stringSQL)
            k = "average_real_interest_rate_300"
            kv[k] = float(cur_dev.fetchone()[0])
            insertField(conn_dev, cur_dev, SRCDB_INDEX, k, "DOUBLE DEFAULT NULL")
        #插入数据
        key_value_str = []
        for k, v in kv.items():
            insertField(conn_dev, cur_dev, SRCDB_INDEX, k, "DOUBLE DEFAULT NULL")
            key_value_str.append("`" + str(k) + "` = '" + str(v) + "'")
            stringSQL = "UPDATE " + SRCDB_INDEX + " SET " + ",".join(key_value_str) + " WHERE `date` = '" + str(_date) + "'"    
            stringSQL = stringSQL.replace("'None'", "NULL")
            cur_dev.execute(stringSQL)
            conn_dev.commit()
     
    closeCursors(cur_dev)
    closeConns(conn_dev)  
    _end_time = time.time()
    print "The whole program costs " + str(_end_time - _start_time) + " seconds."  
    
