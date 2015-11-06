# /usr/bin/python
# encoding=utf8
# 从project_info中读取数据来更新E1

from atbtools.header import * 
from atbtools.mysqlTools import *

if __name__ == '__main__':
    # 获取连接    
    project_info_clean = "project_info_clean"

    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    
    #重建project_info_clean
    print "DELETE FROM " + project_info_clean
    stringSQL = "DELETE FROM " + project_info_clean
    cur_db.execute(stringSQL)
    conn_db.commit()
                 
    closeCursors(cur_db)
    closeConns(conn_db)  