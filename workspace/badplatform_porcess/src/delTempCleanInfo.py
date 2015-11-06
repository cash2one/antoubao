# /usr/bin/python
# encoding=utf8
# 删除一个临时表

from atbtools.header import * 
from atbtools.mysqlTools import *

if __name__ == '__main__':
    # 获取连接    
    dstdb = "project_info_clean_temp"
    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    #删除整个表
    stringSQL = "DROP TABLE IF EXISTS " + dstdb  
    cur_db.execute(stringSQL)
    conn_db.commit()
    #收尾工作
    closeCursors(cur_db)
    closeConns(conn_db) 
    