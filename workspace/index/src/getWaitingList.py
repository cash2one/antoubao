# /usr/bin/python
# coding=utf8

#按照12周的周期，统计出来waiting_list并按照value排序，且前50名标记为表明单（source = 0）
#1.获得指数指标的时间节点
#2.在E1表中寻找所有非坏站并依据value进行排序

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
import time
import hashlib
import sys

if __name__ == '__main__':
    _start_time = time.time()
    #获得连接        
    conn_dev = getConn(DEVHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    conn_db = getConn(DBHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_dev = getCursors(conn_dev)
    cur_db  = getCursors(conn_db)
    initializeCursors(cur_dev, cur_db)
    
    SRCDB_Y = "total_status"   
    SRCDB_E1 = "platform_quantitative_data_E1"
    SRCDB_INDEX_WAITING = "index_waiting_list"
    
    value_format = "%.4f"
    
    #1.获得指数指标的时间节点
    date_list_E1 = getDifferentFieldlist(SRCDB_E1, cur_db, "date")
    date_list_E1.sort(reverse = True) #从大到小排列
    date_list_E1 = date_list_E1[:date_list_E1.index(int(STARTDATE)) + 1] #之前的数据抛弃
    max_date_E1 = date_list_E1[0]
    min_date_E1 = date_list_E1[-1]
    max_date_E1_fake = INDEXNODE + ((max_date_E1 - INDEXNODE)/INDEXPERIOD/SECONDSPERWEEK) * INDEXPERIOD * SECONDSPERWEEK
    min_date_E1_fake = INDEXNODE + ((min_date_E1 - INDEXNODE)/INDEXPERIOD/SECONDSPERWEEK) * INDEXPERIOD * SECONDSPERWEEK
    date_list_fake = range(max_date_E1_fake, min_date_E1_fake - 1, 0 - INDEXPERIOD * SECONDSPERWEEK) #从大到小排列
    date_list = []
    for _date in date_list_fake:
        for i in range(INDEXTOLERANCE):
            _date_fake = _date - i * SECONDSPERWEEK
            if _date_fake in date_list_E1:
                date_list.append(_date_fake)
                break
        else:
            break
    date_number = len(date_list)
    date_list.sort() #从小到大排列
    
    #判断是增量还是全量
    isreset = 0
    if (len(sys.argv) == 2):
        if (sys.argv[1] == "reset"):
            print "Reset '" + SRCDB_INDEX_WAITING + "'"
            start = 0
            cur_dev.execute("DELETE FROM " + SRCDB_INDEX_WAITING)
            conn_dev.commit()
            isreset = 1
    if isreset == 0:
        print "Update '" + SRCDB_INDEX_WAITING + "'"
        start = date_number - 1
        stringSQL = "DELETE FROM " + SRCDB_INDEX_WAITING + " WHERE `date` = '" + str(date_list[-1]) + "'"
        cur_dev.execute(stringSQL)
        conn_dev.commit()
    start = 0
    #2.在E1表中寻找所有非坏站并依据value进行排序
    for i in range(start, date_number):
        _date = date_list[i]
        print _date
        #1.从y表中获得当前时间以前的所有坏站<0.89
        bad_platform_list = []
        stringSQL = "SELECT A.platform_name FROM " + SRCDB_Y + " AS A,(SELECT `platform_name`, MAX(`date`) AS `date` FROM " + SRCDB_Y + " WHERE `date` <= '" + str(_date) + "' GROUP BY `platform_name`) AS B WHERE A.platform_name = B.platform_name AND A.date = B.date AND A.status < '0.89'"
        #stringSQL = "SELECT DISTINCT `platform_name` FROM " + SRCDB_Y + " WHERE `date` <= '" + str(_date) + "' AND `status` < '0.89' ORDER BY `platform_name` ASC" 
        _number = cur_db.execute(stringSQL)
        if _number != 0:
            for field_temp in cur_db.fetchall():
                bad_platform_list.append(field_temp[0])
        bad_platform_number = len(bad_platform_list)
        if 0 != bad_platform_number:
            print "截至" + str(_date) + "这个时间节点，已经有" + str(bad_platform_number) + "个坏站."
        else:
            print "截至" + str(_date) + "这个时间节点，还没有坏站."
            
        #操作非坏站
        platform_list = getDifferentFieldlistEarly(SRCDB_E1, cur_db, "platform_name", _date)
        good_platform_list = list(set(platform_list) - set(bad_platform_list))
        good_platform_dict = {}
        good_platform_list_del = ["陆金所", "金银猫", "e租宝"]
        for good_platform in good_platform_list:
            if good_platform not in good_platform_list_del:
                good_platform_dict[good_platform] = getValue(cur_db,SRCDB_E1,["weekly_lending", "weekly_total_investor"],good_platform,_date,12)
        good_platform_list_sorted = sortDictByValue(good_platform_dict)[0]
        
        #写入数据库
        rank = 0
        field_list = ["date", "value", "platform_id", "platform_name", "rank", "source"]
        for platform_name in good_platform_list_sorted:
            platform_id = hashlib.md5(platform_name).hexdigest()[0:10]
            rank += 1
            source = 1
            if rank > GOODRANK:
                source = 0
            value_list = [str(_date), value_format % good_platform_dict[platform_name], platform_id, platform_name, str(rank), str(source)]
            stringSQL = "INSERT INTO " + SRCDB_INDEX_WAITING + "(`" + "`,`".join(field_list) + "`) VALUES('" + "','".join(value_list) + "')"
            cur_dev.execute(stringSQL)
            conn_dev.commit()
        print "共有" + str(len(good_platform_list_sorted)) + "个站进入waiting list."    
        print ""
    
    closeCursors(cur_dev, cur_db)
    closeConns(conn_dev, conn_db)
    _end_time = time.time()
    print "The whole program costs " + str(_end_time - _start_time) + " seconds."  
    
