# /usr/bin/python
# encoding=utf8

import sys
from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *

if __name__ == '__main__':

    conn_db = getConn(DBHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    
    for site_id in ["anxin", "zfxindai", "zgcfbank", "zhaocaibank", "zibenzaixian", "zj-bank", "zjsdai", "zzydb"]:
        print site_id
        changeProjectInfo(cur_db, conn_db, site_id, "project_info_0")
        
    closeCursors(cur_db)
    closeConns(conn_db)