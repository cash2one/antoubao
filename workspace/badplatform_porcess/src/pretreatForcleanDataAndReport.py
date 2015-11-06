# /usr/bin/python
# encoding=utf8
# 将project_info中的脏数据去掉，方便后续处理

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.paymentTools import *
from atbtools.computeTools import *
import sys
import time

if __name__ == '__main__':
    #判断是增量还是全量
    if (len(sys.argv) <= 1):
        print "'pretreatForcleanDataAndReport'程序必须指定对应的分库个数."
        exit(1)
    else:
        division_number = int(sys.argv[1])
        
    # 获取连接
    srcdb_daily_error = "platform_error_daily_report"
    srcdb_V = "V_view"
    srcdb_info_F = "platform_qualitative_F"
    
    conn_db = getConn(DBHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    conn_ddpt_data = getConn(DDPT_DATAHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_ddpt_data = getCursors(conn_ddpt_data)
    initializeCursors(cur_db, cur_ddpt_data)
    
    #只在初始时候有用，平时只添加最新一周即可
    #在error中添加字段，分别为每周正确的标数以及正确的百分比
#     date_list = getDifferentFieldlist(srcdb_V, cur_ddpt_data, "date")
#     date_number = len(date_list)
#     for i in range(date_number)[::-1]:
#         date = date_list[i]
#         print date
#         date_field = "T_" + str(date)
#         correct_ratio_field = "P_" + str(date)
#         date_type = "INT(11) DEFAULT 0"
#         correct_ratio_type = "FLOAT DEFAULT 0"
#         if i == date_number - 1:
#             date_position = " AFTER `level`"
#         else:
#             date_position = " AFTER `P_" + str(date_list[i+1]) + "`"
#         correct_ratio_position = " AFTER `T_" + str(date) + "`"
#         insertField(conn_db, cur_db, srcdb_daily_error, date_field, date_type + date_position)    
#         insertField(conn_db, cur_db, srcdb_daily_error, correct_ratio_field, correct_ratio_type + correct_ratio_position)    
#     exit(0)

    date = int(getDateTimestamp(time.time()) + SECONDSPERWEEK)
    date_field = "T_" + str(date)
    correct_ratio_field = "P_" + str(date)
    date_type = "INT(11) DEFAULT 0"
    correct_ratio_type = "FLOAT DEFAULT 0"
    date_position = " AFTER `level`"
    correct_ratio_position = " AFTER `T_" + str(date) + "`"
    insertField(conn_db, cur_db, srcdb_daily_error, date_field, date_type + date_position)    
    insertField(conn_db, cur_db, srcdb_daily_error, correct_ratio_field, correct_ratio_type + correct_ratio_position)    
    
    this_date = time.strftime("%Y%m%d")
    stringSQL = "DELETE FROM " + srcdb_daily_error + " WHERE `date` = '" + this_date + "'"
    cur_db.execute(stringSQL)
    conn_db.commit()
    
    #获得历史上所有在project_info出现过的平台
    site_id_list_error = []
    #暂时只看有数据的站
#     site_id_list_error = getDifferentFieldlist(srcdb_daily_error, cur_db, "site_id")
    site_id_list_projectinfo = []
    for i in range(1, division_number + 1):
        site_id_list_projectinfo.extend(getListByTxt("platform_id_" + str(i) + ".txt"))
    site_id_list = list(set(site_id_list_error) | set(site_id_list_projectinfo))
    if "" in site_id_list:
        site_id_list.remove("")
    for site_id in site_id_list:
        #获得platform_name
        stringSQL = "SELECT platform_name FROM " + srcdb_info_F + " WHERE `platform_id` ='" + site_id + "' LIMIT 1"
        ret = cur_db.execute(stringSQL)
        if ret == 0:
            platform_name = site_id
        else:
            platform_name = cur_db.fetchone()[0]
            
        stringSQL = "INSERT "
        field_list = ["date", "site_id", "platform_name"]
        value_list = [this_date, site_id, platform_name]
        stringSQL = "INSERT INTO " + srcdb_daily_error + "(`" + "`,`".join(field_list) + "`) VALUES('" + "','".join(value_list) + "')"
        cur_db.execute(stringSQL)
        conn_db.commit()
    
    closeCursors(cur_db, cur_ddpt_data)
    closeConns(conn_db, conn_ddpt_data)
