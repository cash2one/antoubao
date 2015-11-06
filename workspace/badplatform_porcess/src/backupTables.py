# /usr/bin/python
# encoding=utf8
# 备份view_mobile表格

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
import time

if __name__ == '__main__':
    # 获取连接    
    conn_server = getConn(SERVERHOST, USERNAME, PASSWORD, DB, PORT)
    cur_server = getCursors(conn_server)
    initializeCursors(cur_server)
    #获得备份时间：当天的零点
    srcdb = ["view_mobile","view_cache"]
    backup_time = time.strftime("%Y%m%d", time.localtime(time.time()))
    print "备份时间为：" + str(backup_time)
    for _srcdb in srcdb:
        _dstdb = _srcdb + "_" + str(backup_time)
        #备份表格
        stringSQL = "SHOW TABLES LIKE '%" + _dstdb+ "%'"
        ret = cur_server.execute(stringSQL)
        if ret == 0:
            stringSQL = "CREATE TABLE IF NOT EXISTS " + _dstdb + " SELECT * FROM " + _srcdb   
            cur_server.execute(stringSQL)
            conn_server.commit()
            print _dstdb + "备份完毕."
        else:
            print _dstdb + "已经备份，无需再备份."

    #收尾工作
    closeCursors(cur_server)
    closeConns(conn_server) 
    