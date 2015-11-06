# /usr/bin/python
# encoding=utf8
# 更新view_cache中坏站是否出现的report参数

import sys
from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from atbtools.paymentTools import *
from math import floor
import time
import hashlib

if __name__ == '__main__':
    
    #从文件中取得更新的platform_name
    platform_name_insert_list = getPlatformIdList("insertReportId.txt")
    platform_name_delete_list = getPlatformIdList("deleteReportId.txt")
    print "要添加报告的平台为："
    for platform_name_insert in platform_name_insert_list:
        print str(platform_name_insert),
    print 
    print "要删除报告的平台为："
    for platform_name_delete in platform_name_delete_list:
        print str(platform_name_delete),
    print
    print 
    platform_name_report_dict={}.fromkeys(platform_name_insert_list, 1)
    platform_name_report_dict.update({}.fromkeys(platform_name_delete_list, 0))
    #获取链接
    srcdb = "view_cache"
    conn_server = getConn(SERVERHOST, USERNAME, PASSWORD, DB, PORT)
    cur_server = getCursors(conn_server)
    initializeCursors(cur_server)
    
    for platform_name in platform_name_report_dict:
        platform_id = hashlib.md5(platform_name).hexdigest()[0:10]
        stringSQL = "SELECT * FROM " + srcdb + " WHERE `platform_id` = '" + platform_id + "'"   
        ret = cur_server.execute(stringSQL)
        if ret == 0:
            print "'" + str(platform_name) + "'不在我们的数据库中，请仔细检查."
            exit(0)
        else:
            stringSQL = "UPDATE " + srcdb + " SET `report` = '" + str(platform_name_report_dict[platform_name]) + "' WHERE `platform_id` = '" + platform_id + "'"   
            ret = cur_server.execute(stringSQL)
            conn_server.commit()
            if ret == 1:
                if platform_name in platform_name_delete:
                    print "'" + str(platform_name) + "'已经从线上删除."
                else:
                    print "'" + str(platform_name) + "'已经添加到线上."
            else:
                print "'" + str(platform_name) + "'状态不需要更新."
        
    closeCursors(cur_server)
    closeConns(conn_server)  
