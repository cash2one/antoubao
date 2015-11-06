# /usr/bin/python
# encoding=utf8

import sys
from atbtools.header import * 
from atbtools.mysqlTools import *


def getRowNumber():
    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    stringSQL = "SELECT count(*) FROM " + table_name
    cur_db.execute(stringSQL)
    row_number = cur_db.fetchone()[0]
    closeCursors(cur_db)
    closeConns(conn_db)  
    print row_number
    return row_number
    
if __name__ == '__main__':
        #判断是增量还是全量
    if (len(sys.argv) == 1):
        print "'countRowNumber'程序必须指定对应的表格名称."
        exit(1)
    else:
        table_name = str(sys.argv[1])
    getRowNumber()
