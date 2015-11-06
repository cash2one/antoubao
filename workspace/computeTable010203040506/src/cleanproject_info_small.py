# /usr/bin/python
# encoding=utf8
# 将project_info中的脏数据去掉，方便后续处理

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from atbtools.xmlTools import *
from atbtools.paymentTools import *
from math import floor

if __name__ == '__main__':
    _start_time = time.time()
    #清理数据的时间为每周一次，且每次只保留上一周满标的数据
#     clean_date_now = int(time.time())
#     clean_date_lasttime=int(getValue("./clean_date.xml","clean_date_lasttime"))
#     if clean_date_now - clean_date_lasttime < SECONDSPERWEEK:
#         print "上一周的数据已经清理过了，不需要再清理"
#         exit(0)
#     else:
#         clean_date_thistime = getTimestampZero(clean_date_now, 0, 0)
    clean_date_thistime = getTimestampZero(time.time(), 0, 0)
    # 获取连接    
    dstdb_info = "project_info_clean"
    conn_db = getConn(DBHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_db1, cur_db2 = getCursors(conn_db, 2)
    initializeCursors(cur_db1, cur_db2)

    project_info_list = getListByTxt("project_info_list.txt")
    srcdb_info = project_info_list[0]
        
    #获得所有字段
    fields_list = getAllColumnsFromTable(cur_db1, dstdb_info, del_list = ["date", "error", "id"])
    fields_number = len(fields_list)
    for srcdb_info in project_info_list:
        print srcdb_info
        stringSQL = "SELECT `" +"`,`".join(fields_list) + "` FROM "+ srcdb_info
        print "正在从数据库传输数据回本地..."
        bids_number = cur_db1.execute(stringSQL)
        bidsPercentList = [floor(float(x) * bids_number / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)] 
        rows = cur_db1.fetchall()
        counter = 0
        print "cleaning: 0%"
        for row in rows:
            counter += 1
            if counter in bidsPercentList:
                print "cleaning: " + str((1 + bidsPercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
            v={}
            for i in range(fields_number):
                v[fields_list[i]] = row[i]
            v = cleanProjectInfoPerBid(v)
            if v["error"] != "":
                continue
            if v["date"] > clean_date_thistime: #只保留上周之前的标
                continue
            v["release_time"] = v["first_time"]    
            v["end_time"] = v["last_time"]
            fields_list_new = []
            value_str = []
            for _field in fields_list:
                fields_list_new.append(str(_field))
                value_str.append(str(v[_field]))
            fields_list_new.append("date")
            value_str.append(str(v["date"]))
            stringSQL = "INSERT INTO " + dstdb_info + "(`" + "`,`".join(fields_list_new) + "`) VALUES('" + "','".join(value_str) + "')"
#             print stringSQL
            cur_db2.execute(stringSQL)
            conn_db.commit()
    #changeValue("./clean_date.xml","clean_date_lasttime",clean_date_thistime)
    closeCursors(cur_db1, cur_db2)
    closeConns(conn_db)
    _end_time = time.time()
    print "The clean program costs " + str(_end_time - _start_time) + " seconds."  
      
