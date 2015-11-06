# /usr/bin/python
# encoding=utf8
# 从project_info中读取数据来更新E1

from atbtools.header import * 
from atbtools.mysqlTools import *

if __name__ == '__main__':
    # 获取连接    
    TABLE_01 = "Table_01_investor_history"
    TABLE_02 = "Table_02_investor_current"
    TABLE_03 = "Table_03_borrower_history"
    TABLE_04 = "Table_04_borrower_current"
    TABLE_05 = "Table_05_pending_bill"
    TABLE_06 = "Table_06_parameter_quantitative"

    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    
    #重建Table01
    print "DELETE FROM '" + TABLE_01
    cur_db.execute("DELETE FROM " + TABLE_01)
    conn_db.commit()
    #重建Table02
    print "DELETE FROM '" + TABLE_02
    cur_db.execute("DELETE FROM " + TABLE_02)
    conn_db.commit()
    #重建Table_03
    print "DELETE FROM '" + TABLE_03
    cur_db.execute("DELETE FROM " + TABLE_03)
    conn_db.commit()
    #重建Table_04
    print "DELETE FROM '" + TABLE_04
    cur_db.execute("DELETE FROM " + TABLE_04)
    conn_db.commit()
    #重建Table_05
    print "DELETE FROM '" + TABLE_05
    cur_db.execute("DELETE FROM " + TABLE_05)
    conn_db.commit()
    #重建Table_06
    print "DELETE FROM '" + TABLE_06
    cur_db.execute("DELETE FROM " + TABLE_06)
    conn_db.commit()
                 
    closeCursors(cur_db)
    closeConns(conn_db)  