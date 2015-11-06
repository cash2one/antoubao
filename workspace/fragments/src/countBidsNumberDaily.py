#!/usr/bin/python
#coding=utf-8

import time
from atbtools.header import *
from atbtools.mysqlTools import *
from atbtools.computeTools import *


if __name__ == '__main__':
    _start_time = time.time()
    
    #获取连接
    conn_ddpt_data=MySQLdb.connect(host=DDPT_DATAHOST_OUT, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT) 
    cur_ddpt_data=getCursors(conn_ddpt_data)
    conn_db=MySQLdb.connect(host=DBHOST_OUT, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT) 
    cur_db=getCursors(conn_db)
    initializeCursors(cur_ddpt_data, cur_db)
    
    SRCDB_V = "V_view"
    SRCDB_P = "project_info_clean_whole"
    
    #获得V表中的时间戳
    date_list_V = getDifferentFieldlist(SRCDB_V, cur_ddpt_data, "date")
    
    #获得每个时间戳内V表中B++以上的站（注意可以包括补充数据的站）
    platform_BPP_dict = {}
    stringSQL = "SELECT `date` , `platform_name` FROM " + SRCDB_V + " WHERE `level` in ('A++', 'A+', 'A', 'B++') AND `status` > 0.89 GROUP BY `date`, `platform_name`"
    cur_ddpt_data.execute(stringSQL)
    for date, platform_name in cur_ddpt_data.fetchall():
        if date not in platform_BPP_dict:
            platform_BPP_dict[date] = []
        platform_BPP_dict[date].append(platform_name)
    
    summary_BPP_dict = {}
    summary_NBPP_dict = {}
    for date in date_list_V:
        summary_BPP_dict[date] = {}
        summary_NBPP_dict[date] = {}
        stringSQL = "SELECT `platform_name`, count(*) FROM " + SRCDB_P + " WHERE `date` = '" + str(date) + "' AND `loan_period` <= '120' AND `loan_period` >= '0' GROUP BY `platform_name`"
        cur_db.execute(stringSQL)
        for platform_name, count in cur_db.fetchall():
#             if platform_name == "前海理想金融":
#                 platform_name = "前海理想"
#             if platform_name == "凤凰金融（江西）":
#                 platform_name = "江西凤凰"
#             if platform_name == "汇盈金服(汇盈贷)":
#                 platform_name = "汇盈金服"
            if platform_name in platform_BPP_dict[date]:
                summary_BPP_dict[date][platform_name] = count
            else:
                summary_NBPP_dict[date][platform_name] = count
        BPP_sum_number = len(summary_BPP_dict[date])
        NBPP_sum_number = len(summary_NBPP_dict[date])
        platform_name_list_BPP = sortListByDicts(summary_BPP_dict[date].keys(), [-1], summary_BPP_dict[date])
        platform_name_list_NBPP = sortListByDicts(summary_NBPP_dict[date].keys(), [-1], summary_NBPP_dict[date])
        _str = str(date) + "(Y: " + str(BPP_sum_number) + "  N: " + str(NBPP_sum_number) + ")"
        print _str
        for platform_name in platform_name_list_BPP:
            _str = "%-15s" % (platform_name + "(Y)") + "    " + str(summary_BPP_dict[date][platform_name])
            print _str
        for platform_name in platform_name_list_NBPP:
            _str = "%-15s" % (platform_name + "(N)") + "    " + str(summary_NBPP_dict[date][platform_name])
            print _str
        print 
    closeCursors(cur_db, cur_ddpt_data)
    closeConns(conn_db, conn_ddpt_data)
    _end_time = time.time()
    print "The whole program costs " + str(_end_time - _start_time) + " seconds." 