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
    srcdb_F = "platform_qualitative_F"
    srcdb_Y = "total_status"

    conn_db = getConn(DBHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    
    # 获取所有的坏站id：从Y表里取得坏站name，通过F表得到id，再去project_info表中比照
    platform_name_Y_list = []
    stringSQL = "SELECT A.platform_name FROM " + srcdb_Y + " AS A,(SELECT `platform_name`, MAX(`date`) AS `date` FROM " + srcdb_Y + " GROUP BY `platform_name`) AS B WHERE A.platform_name = B.platform_name AND A.date = B.date AND A.`status` < '0.89'"
    _number = cur_db.execute(stringSQL)
    if _number != 0:
        for field_temp in cur_db.fetchall():
            platform_name_Y_list.append(field_temp[0].strip())
    platform_id_F_list = []
    platform_name_F_dict = {}
    stringSQL = "SELECT platform_id, platform_name FROM " + srcdb_F
    cur_db.execute(stringSQL)
    for platform_id, platform_name in cur_db.fetchall():
        platform_id = str(platform_id)
        platform_name = platform_name.strip()
        if platform_name in platform_name_Y_list:
            platform_id_F_list.append(platform_id)
            platform_name_F_dict[platform_id] = platform_name
    
#     platform_id_info_list = getDifferentFieldlist("project_info", cur_db, "site_id")
    platform_id_info_list = getSiteIdFromProjectInfos(cur_db)
    platform_id_list = list(set(platform_id_info_list) & set(platform_id_F_list))
    platform_id_list.sort()
    platform_id_number = len(platform_id_list)
    
    #写入文本
    fp1 = open("badplatform_id.txt","w")
    print "数据库中有" + str(platform_id_number) + "个坏站."
    #fp2 = open("collect_luoli.txt","w")
    #fp2.write("数据库中有" + str(platform_id_number) + "个坏站: \n")
    for platform_id in platform_id_list:
        fp1.write(platform_id + "\n")
        #fp2.write(platform_id + ": " + platform_name_F_dict[platform_id] + "\n")
#     for platform_id in platform_id_F_list:
#         if platform_id not in platform_id_list:
#             fp2.write(platform_id + "(" + platform_name_F_dict[platform_id] + ")在F表中，但在project中却没有该平台.\n")
    fp1.close()
#     fp2.close()
    closeCursors(cur_db)
    closeConns(conn_db)  
