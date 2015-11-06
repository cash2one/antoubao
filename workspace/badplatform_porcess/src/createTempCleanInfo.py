# /usr/bin/python
# encoding=utf8
# 新建一个临时project_info_clean空表（只有表结构）

from atbtools.header import * 
from atbtools.mysqlTools import *

if __name__ == '__main__':
    # 获取连接    
    srcdb = "project_info_clean"
    dstdb = "project_info_clean_temp"
    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    #创建形如srcdb的新表，只包含结构
    stringSQL = "SHOW TABLES LIKE '%" + dstdb+ "%'"
    ret = cur_db.execute(stringSQL)
    if ret == 0:
        stringSQL = "CREATE TABLE IF NOT EXISTS " + dstdb + " LIKE " + srcdb  
        cur_db.execute(stringSQL)
        conn_db.commit()
    else:
        cur_db.execute("DELETE FROM " + dstdb)
        conn_db.commit()
    #收尾工作
    closeCursors(cur_db)
    closeConns(conn_db) 
    