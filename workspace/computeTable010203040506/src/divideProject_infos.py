# /usr/bin/python
# encoding=utf8

import sys
from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *


if __name__ == '__main__':
    #确定分库个数
    if (len(sys.argv) <= 1):
        print "'divideProject_infos'程序必须指定对应的分库个数."
        exit(1)
    else:
        division_number = int(sys.argv[1])
    conn_db = getConn(DBHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    
    project_info_name_list = []
    project_info_number_list = []
    for i in range(division_number):
        project_info_name_list.append([])
        project_info_number_list.append([])
    
    #获取所有project_info的总标数
    project_info_number_dict = {}
    for project_info_initial in "abcdefghijklmnopqrstuvwxyz0":
        srcdb_info = "project_info" + "_" + project_info_initial
        stringSQL = "SELECT COUNT(*) FROM " + srcdb_info
        cur_db.execute(stringSQL)
        count = int(cur_db.fetchone()[0])
        if count != 0:
            project_info_number_dict[project_info_initial] = count
    
    #将project_info分组，使得每组的总标数尽量均匀
    project_info_name_list, project_info_number_list = divideNumberForEven(project_info_number_dict, division_number)
    for i in range(division_number):
        file_name = "project_info_list_" + str(i+1) + ".txt"
        fp = open(file_name, "w")
        for project_info_name in project_info_name_list[i]:
            fp.write("project_info" + "_" + project_info_name + "\n")
        fp.close() 
        print "第" + str(i+1) + "个库中有" + str(sum(project_info_number_list[i])) + "个标."
        
    closeCursors(cur_db)
    closeConns(conn_db)