# /usr/bin/python
# encoding=utf8
# 通过project_info和table06的比较，筛选出从未出现的站就行全量跑

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from atbtools.paymentTools import *
from math import floor

if __name__ == '__main__':
    # 获取连接    
    srcdb_info = "project_info_clean"
    srcdb_table06 = "Table_06_parameter_quantitative"
    srcdb_F = "platform_qualitative_F"

    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    #记录下不在table06的新站
    fp_old = open("old_platform_id.txt","w") #做增量
    fp_new = open("new_platform_id.txt","w") #做全量
    platform_name_06_list = getDifferentFieldlist(srcdb_table06, cur_db, "platform_name")
    platform_id_info_list = getDifferentFieldlist(srcdb_info, cur_db, "site_id")
    old_number = 0
    new_number = 0
    print "要做全量的新站有："
    for platform_id in platform_id_info_list:
        #通过F表查询platform_name
        stringSQL = "SELECT platform_name FROM " + srcdb_F + " WHERE `platform_id` = '" + str(platform_id) + "'"
        ret = cur_db.execute(stringSQL)
        if ret != 0:
            platform_name = cur_db.fetchone()[0].strip()
        if platform_name not in platform_name_06_list:
            fp_new.write(str(platform_id) + "\n")
            print str(platform_id)
            new_number += 1
        else:
            fp_old.write(str(platform_id) + "\n")
            old_number += 1
    fp_old.close()    
    fp_new.close()
    print "共有" + str(new_number) + "个新站需要做全量."
    print "共有" + str(old_number) + "个老站可以做增量."
    closeCursors(cur_db)
    closeConns(conn_db)  
