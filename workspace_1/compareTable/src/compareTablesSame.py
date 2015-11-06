# /usr/bin/python
# encoding=utf8
# 比较两个数据表的差别，所有因素取交集，同时取B/A的值

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from atbtools.paymentTools import *
from math import floor
import time
import hashlib

if __name__ == '__main__':
    
    conn_db = getConn(DBHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    
    conn_dev = getConn(DEVHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_dev = getCursors(conn_dev)
    initializeCursors(cur_dev)
    
    conn_ddpt_test = getConn(DDPT_TESTHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_ddpt_test = getCursors(conn_ddpt_test)
    initializeCursors(cur_ddpt_test)
    
    conn_ddpt_data = getConn(DDPT_DATAHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_ddpt_data = getCursors(conn_ddpt_data)
    initializeCursors(cur_ddpt_data)
    
    list_1 = ["0_E1_quantitative_data", "0_E2_quantitative_data", "2_total_status", "4_E3_quantitative_score", "5_H_score", "6_P_punishment", "7_S_smooth", "8_T_rank", "9_V_view"]
    list_2 = ["platform_quantitative_data_E1", "E2_quantitative_data", "total_status", "E3_quantitative_score", "H_score", "P_punishment", "S_smooth", "T_rank", "V_view"]
    
    cur_dict = {}
    cur_dict.update({}.fromkeys(list_1, cur_ddpt_test))
    cur_dict.update({}.fromkeys(list_2, cur_ddpt_data))
    cur_dict.update({}.fromkeys(["platform_quantitative_data_E1", "total_status"], cur_db))
    cur_dict.update({}.fromkeys(["E2_quantitative_data", "T_rank"], cur_dev))
#     list_1 = ["9_V_view"]
#     list_2 = ["V_view"]
    
    list_1_number = len(list_1)
    list_2_number = len(list_2)
    if list_1_number != list_2_number:
        print "列表大小不一致."
        exit(-1)
    
    for i in range(0, list_1_number):
        value_dict_1 = {}
        value_dict_2 = {}
        for table in [list_1[i], list_2[i]]:
            print table
            value_dict = value_dict_1
            if table in list_2:
                value_dict = value_dict_2
            cur = cur_dict[table]
            field_list = getAllColumnsFromTable(cur, table, del_list = ["id", "Id", "platform_name", "date"])
            field_number = len(field_list)
            field_list.sort()
            stringSQL = "SELECT `platform_name`, `date`, `" + "`, `".join(field_list) + "` FROM " + table
            print "等待数据传输。。。。"
            cur.execute(stringSQL)
            for rets in cur.fetchall():
                platform_name = rets[0]
                date = rets[1]
                value_list = rets[2:]
                if platform_name not in value_dict:
                    value_dict[platform_name] = {}
                if date not in value_dict[platform_name]:
                    value_dict[platform_name][date] = None
                value_dict[platform_name][date] = value_list
        platform_name_list_1 = sorted(value_dict_1.keys())
        platform_name_list_2 = sorted(value_dict_2.keys())
        if platform_name_list_1 == platform_name_list_2:
            print "两个表内的平台名称完全一致。"
            for platform_name in platform_name_list_1:
                date_list_1 = sorted(value_dict_1[platform_name].keys())
                date_list_2 = sorted(value_dict_2[platform_name].keys())
                if date_list_1 == date_list_2:
                    for date in date_list_1:
                        value_list_1 = value_dict_1[platform_name][date]
                        value_list_2 = value_dict_2[platform_name][date]
                        if value_list_1 == value_list_2:
                            pass
                        else:
                            for j in range(field_number):
                                if value_list_1[j] != value_list_2[j]:
                                    print i
                                    print platform_name
                                    print date
                                    print field_list[j]
                                    print value_list_1[j]
                                    print value_list_2[j]
                                    exit(1)
                else:
                    date_list_lack_1 = list(set(date_list_1) - set(date_list_2))
                    for date in platform_name_lack_1:
                        print date + "在第一个表中但不在第二个表中。"
                    date_list_lack_2 = list(set(date_list_2) - set(date_list_1))
                    for date in date_list_lack_2:
                        print date + "在第二个表中但不在第一个表中。"
                    exit(1)
            print "两个表内的平台的时间戳也完全一致。"
        else:
            print platform_name_list_1
            print platform_name_list_2
            platform_name_lack_1 = list(set(platform_name_list_1) - set(platform_name_list_2))
            for platform_name in platform_name_lack_1:
                print platform_name + "在第一个表中但不在第二个表中。"
            platform_name_lack_2 = list(set(platform_name_list_2) - set(platform_name_list_1))
            for platform_name in platform_name_lack_2:
                print platform_name + "在第二个表中但不在第一个表中。"
            exit(1)
        
    closeCursors(cur_db, cur_dev, cur_ddpt_data, cur_ddpt_test)
    closeConns(conn_db, conn_dev, conn_ddpt_data, conn_ddpt_test)
