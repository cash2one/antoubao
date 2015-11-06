# /usr/bin/python
# encoding=utf8
# 从project_info中读取数据来更新E1

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.paymentTools import *
from atbtools.computeTools import *
from math import floor
import time

if __name__ == '__main__':
    # 获取连接    
    dstdb_E1 = "platform_quantitative_data_E1"
    srcdb_F = "platform_qualitative_F"
    srcdb_Y = "total_status"

    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    
    date_list = getDifferentFieldlist(dstdb_E1, cur_db, 'date')
    date_now = max(date_list)
    # 获取所有的坏站id：从Y表里取得坏站name，通过F表得到id，再去project_info表中比照
    platform_name_Y_list = []
    stringSQL = "SELECT A.platform_name FROM " + srcdb_Y + " AS A,(SELECT `platform_name`, MAX(`date`) AS `date` FROM " + srcdb_Y + " GROUP BY `platform_name`) AS B WHERE A.platform_name = B.platform_name AND A.date = B.date AND A.`status` < '0.89'"
    _number = cur_db.execute(stringSQL)
    if _number != 0:
        for field_temp in cur_db.fetchall():
            platform_name_Y_list.append(field_temp[0].strip())
    platform_name_E1_list = getDifferentFieldlist(dstdb_E1, cur_db, "platform_name")
    platform_name_E1_list = [x.strip() for x in platform_name_E1_list] #这里去掉行尾的回车
    platform_name_list = list(set(platform_name_Y_list) & set(platform_name_E1_list))
    platform_name_number = len(platform_name_list)
    platform_name_E1_list_now = getDifferentFieldlistByDate(dstdb_E1, cur_db, "platform_name", date_now)
    platform_name_E1_list_now = [x.strip() for x in platform_name_E1_list_now] #这里去掉行尾的回车
    platform_name_list_now = list(set(platform_name_Y_list) & set(platform_name_E1_list_now))
    platform_name_number_now = len(platform_name_list_now)
    
    #写入文本
    fp1 = open("bad_platform_name.txt","w")
    fp1.write("数据库E1中一共有" + str(platform_name_number) + "个坏站: \n")
    for platform_name in platform_name_list:
        fp1.write(platform_name + "\n")
    fp1.write("其中本周一共有" + str(platform_name_number_now) + "个坏站: \n")
    for platform_name in platform_name_list_now:
        fp1.write(platform_name + "\n")
    fp1.close()
    closeCursors(cur_db)
    closeConns(conn_db)  
