# /usr/bin/python
# encoding=utf8
# 通过project_info和table06的比较，筛选出从未出现的站就行全量跑

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from math import floor
import sys

if __name__ == '__main__':
    #判断是增量还是全量
    if (len(sys.argv) <= 2):
        print "'dividePlatform'程序必须指定对应的表格名称和分库个数."
        exit(1)
    else:
        table_name = str(sys.argv[1])
        platform_division = int(sys.argv[2])
#     table_name = "project_info_clean"
#     platform_division = 4
    # 获取连接    
    conn_db = getConn(DBHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    
    platform_name_number_dict = {}
    stringSQL = "SELECT `site_id`, COUNT(*) FROM "  +  table_name + " WHERE `error` = '' GROUP BY `site_id`"
    cur_db.execute(stringSQL)
    for site_id, count in cur_db.fetchall():
        platform_name_number_dict[site_id] = int(count)
    print "共有" + str(len(platform_name_number_dict)) + "个平台."
    
    #将平台名称分组，使得每组的总标数尽量均匀
    platform_name_list, platform_number_list = divideNumberForEven(platform_name_number_dict, platform_division)
    for i in range(platform_division):
        file_name = "platform_id_" + str(i+1) + ".txt"
        fp = open(file_name, "w")
        for platform_name in platform_name_list[i]:
            fp.write(platform_name + "\n")
        fp.close() 
        print "第" + str(i+1) + "个库中有" + str(sum(platform_number_list[i])) + "个标."
        
    closeCursors(cur_db)
    closeConns(conn_db)  
