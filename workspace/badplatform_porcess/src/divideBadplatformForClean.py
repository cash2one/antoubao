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
    if (len(sys.argv) <= 1):
        print "'divideBadplatformForClean'程序必须指定对应的分库个数."
        exit(1)
    else:
        platform_division = int(sys.argv[1])
    # 获取连接    
    conn_db = getConn(DBHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    
    bad_platform_name_list = getListByTxt("badplatform_id.txt")
    bad_platform_name_list_del = getPlatformIdList("badplatform_id_del.txt")
    bad_platform_name_list_add = getPlatformIdList("badplatform_id_add.txt")
    bad_platform_name_list = list((set(bad_platform_name_list) - set(bad_platform_name_list_del)) | set(bad_platform_name_list_add))

    bad_platform_number = len(bad_platform_name_list)
    
    bad_platform_number_dict = {}
    for project_info_initial in "abcdefghijklmnopqrstuvwxyz0":
        srcdb_info = "project_info" + "_" + project_info_initial
        stringSQL = "SELECT `site_id`, COUNT(*) FROM " + srcdb_info + " GROUP BY `site_id`"
        cur_db.execute(stringSQL)
        for site_id, count in cur_db.fetchall():
            if site_id in bad_platform_name_list:
                bad_platform_number_dict[site_id] = int(count)
    print "清理之前共有" + str(len(bad_platform_number_dict)) + "个平台: "
    print bad_platform_number_dict.keys()
    
    #将平台名称分组，使得每组的总标数尽量均匀
    platform_name_list, platform_number_list = divideNumberForEven(bad_platform_number_dict, platform_division)
    for i in range(platform_division):
        file_name = "badplatform_id_" + str(i+1) + ".txt"
        fp = open(file_name, "w")
        for platform_name in platform_name_list[i]:
            fp.write(platform_name + "\n")
        fp.close() 
        print "第" + str(i+1) + "个库中有" + str(sum(platform_number_list[i])) + "个标."
        
    closeCursors(cur_db)
    closeConns(conn_db)
