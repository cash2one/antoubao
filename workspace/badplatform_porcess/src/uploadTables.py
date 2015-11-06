# /usr/bin/python
# encoding=utf8
# 上传view_mobile和view_cache表格

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
import time

if __name__ == '__main__':
    # 获取连接
    conn_dev = getConn(DEVHOST, USERNAME, PASSWORD, DB, PORT)
    cur_dev = getCursors(conn_dev)
    conn_server = getConn(SERVERHOST, USERNAME, PASSWORD, DB, PORT)
    cur_server = getCursors(conn_server)
    initializeCursors(cur_dev, cur_server)
    #开始上传    
    srcdb = ["view_mobile","view_cache"]
    for _srcdb in srcdb:
        stringSQL = "SELECT COUNT(*) FROM information_schema.TABLES WHERE table_name = '" + _srcdb + "' AND TABLE_SCHEMA = '" + DB + "'"
        ret = cur_server.execute(stringSQL)
        if ret == 1:
            print "开始上传..."
            cur_server.execute("TRUNCATE " + _srcdb)
            conn_server.commit()
        else:
            print _srcdb + "并不存在，需要手工创建."
            exit(1)
        _field_list = getAllColumnsFromTable(cur_server, _srcdb, del_list = ["id"]) 
        fields_list = getAllColumnsFromTable(cur_dev, _srcdb, del_list = ["id"], merge_list = _field_list) 
        fields_number = len(fields_list)
        stringSQL = "SELECT `" +"`,`".join(fields_list) + "` FROM "+ _srcdb
        cur_dev.execute(stringSQL)
        for line in cur_dev.fetchall():
            fields_new_list = [] #处理null的问题，如果为None则不插入该指标，即采用mysql默认的null
            values_list = []
            for i in range(fields_number):
                if None != line[i]:
                    fields_new_list.append(fields_list[i])
                    values_list.append(str(line[i])) 
            stringSQL = "INSERT INTO " + _srcdb + "(`" + "`,`".join(fields_new_list) + "`) VALUES('" + "','".join(values_list) + "')"
            cur_server.execute(stringSQL)
            conn_server.commit()
    #收尾工作
    closeCursors(cur_dev, cur_server)
    closeConns(conn_dev, conn_server) 
    