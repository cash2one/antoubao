# /usr/bin/python
# encoding=utf8

import sys
from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *


if __name__ == '__main__':
    #判断是增量还是全量
    if (len(sys.argv) <= 2):
        print "'divideId'程序必须指定对应的表格名称和分库个数."
        exit(1)
    else:
        table_name = str(sys.argv[1])
        division_number = int(sys.argv[2])
    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    id_list = getDifferentFieldlist(table_name, cur_db, "id")
    id_number =len(id_list)
    print "共有" + str(id_number) +"个标."
    id_per_number = id_number / division_number
    id_remainder = id_number - id_per_number * division_number
    start_index = []
    end_index = []
    start = 0
    end = 0
    for i in range(division_number):
        start_index.append(id_list[start])
        end = start + (id_per_number - 1)
        if id_remainder > 0:
            end += 1
            id_remainder -= 1
        end_index.append(id_list[end])
        file_name = "id_" + str(i+1) + ".txt"
        fp = open(file_name,"w")
        fp.write(str(id_list[start]) + "\n")
        fp.write(str(id_list[end]) + "\n")
        fp.close() 
        print "第" + str(i+1) + "个库中有" + str(end-start+1) + "个标."
        start = end + 1
        
    closeCursors(cur_db)
    closeConns(conn_db)