# /usr/bin/python
# encoding=utf8
# 将project_info中的脏数据去掉，方便后续处理

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from atbtools.paymentTools import *
from math import floor
import time

if __name__ == '__main__':
    # 获取连接    
    srcdb_info = "project_info"
    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db1, cur_db2 = getCursors(conn_db, 2)
    initializeCursors(cur_db1, cur_db2)

    #获得所有字段
    stringSQL = "SELECT `id`, `investor`, `site_id` FROM "+ srcdb_info
    stringSQL = stringSQL + " WHERE `site_id` = 'licaifan'"
    print "正在从数据库传输数据回本地..."
    bids_number = cur_db1.execute(stringSQL)
    print "共有" + str(bids_number) + "个标需要处理."
    bidsPercentList = [floor(float(x) * bids_number / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)] 
    rows = cur_db1.fetchall()
    counter = 0
    site_id_repeat_set=set()
    site_id_error_set=set()
    print "cleaning: 0%"
    fp = open("repeatplatform_id.txt","w")
    for _id, investor, site_id in rows:
        counter += 1
        if counter in bidsPercentList:
            print "cleaning: " + str((1 + bidsPercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
        _id = int(_id)
        investor = str(investor)
        if len(investor) == 0:
            continue
        else:
            investor_set = set()
            investor_dict = {}
            investor_list = investor.split("|")
            investor_number = (len(investor_list) + 1) / 3
            for i in range(investor_number):
                investor_str = investor_list[i * 3:(i + 1) * 3]
                try: 
                    investor_dict[tuple(investor_str)] += 1
                except:
                    investor_dict[tuple(investor_str)] = 1
                investor_set.add("|".join(investor_str))
            investor_set_number = len(investor_set)
            repeat_time = investor_number / investor_set_number
            if repeat_time != 1:
                print str(_id) + "__" + str(site_id) + ": investor有重复，重复次数为" + str(repeat_time) + "."
                if site_id not in site_id_repeat_set:
                    if repeat_time > 2:
                        fp.write(str(site_id) + "\n")
                    site_id_repeat_set.add(site_id)
                #重新写回数据
                
            repeat_time_reminder = investor_number % investor_set_number
            if repeat_time_reminder != 0:
                if site_id not in site_id_error_set:
                    #print str(site_id) + ": 存在自身重复的投资人，会导致投资人个数被少估计."
                    site_id_error_set.add(site_id)
    print "存在重复的网站有" + str(len(site_id_repeat_set)) + "个."
    fp.close()
    closeCursors(cur_db1, cur_db2)
    closeConns(conn_db)  
