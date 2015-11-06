# /usr/bin/python
# coding=utf8

#1.从y表中获得所有坏站
#2.对每一个E1中的时刻，判断waiting-list并进行相应的操作

"""
2.1 坏站：
当周weekly_outstanding_loan=0或者为None，记为-2（-2不进一步操作），否则记为-1
然后上溯-1，填充所有指标进行填充（上溯4周，上溯不成功指标记为0）；

2.2 source=0:
当周weekly_lending=0删除；
本周其他指标为0的个数>2删除；
然后上溯填充所有指标（上溯4周，上溯不成功指标记为0）；
填充后，必须满足所有指标均不为零，否则删除。

2.3 source=1:
上溯填充所有指标进行填充（上溯12周上溯不成功指标记为0）；
填充后，必须满足所有指标均不为零，否则删除。

2.4 记录score和level的时候，也可以上溯（=1上溯12周，=0上溯4周，上溯不成功记为null，null）,-1的坏站不上溯，没有的话默认为null，C。-2的坏站直接记为null, null

2.5 填充close_time字段
"""

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
    (cur1_db, cur2_db)  = getCursors(conn_db,2)
    initializeCursors(cur_dev, cur1_db, cur2_db)
    
    SRCDB_Y = "total_status"
    SRCDB_T = "T_rank"
    SRCDB_E1 = "platform_quantitative_data_E1"
    SRCDB_INDEX_WAITING = "index_waiting_list"
    SRCDB_INDEX_TARGET = "index_platform_list"
    
    _field_list = ["weekly_outstanding_loan", "ave_annualized_return", "weekly_lending", "weekly_total_investor", "weekly_loan_period", "turnover_period"]
    _fields_number = len(_field_list)
    _fields_list_add = ["weekly_ave_bid_close_time"]
    _fields_number_add = len(_fields_list_add)
    value_format = "%.4f"
    
    #1.获得指数指标的时间节点
    date_list_E1 = getDifferentFieldlist(SRCDB_E1, cur1_db, "date")
    date_number =len(date_list_E1)
    date_list_waiting = getDifferentFieldlist(SRCDB_INDEX_WAITING, cur_dev, "date")
    
#     #获得所有日期的评级区间
#     date_list_T = getDifferentFieldlist(SRCDB_T, cur_dev, "date")
#     date_number_T = len(date_list_T)
#     level_name_list = ["levelaplusplus", "levelaplus", "levela", "levelbplusplus", "levelbplus", "levelb", "levelc"]
#     level_order_list = ["A++", "A+", "A", "B++", "B+", "B", "C"]
#     level_number = len(level_order_list)
#     level_dict = {"levelaplusplus":"A++", "levelaplus":"A+", "levela":"A", "levelbplusplus":"B++", "levelbplus":"B+", "levelb":"B", "levelc":"C"}
#     lever_score_dict = {}
#     stringSQL = "SELECT platform_name, date, score FROM " + SRCDB_T
#     cur_dev.execute(stringSQL)
#     rets = cur_dev.fetchall()    
#     for platform_name, date, score in rets:
# #         if platform_name in level_name_list:
# #             platform_name = level_dict[platform_name]
#         if platform_name in level_order_list:
#             if platform_name not in lever_score_dict:
#                 lever_score_dict[platform_name] = {}
#                 for date_temp in date_list_T:
#                     lever_score_dict[platform_name][date_temp] = {}
#                     lever_score_dict[platform_name][date_temp]["score"] = MINPLATFORMSCORE
#             lever_score_dict[platform_name][date]["score"] = float(score)
#     score_dict = {}
#     for date in date_list_T:
#         score_dict[date] = {}
#         for i in range(level_number):
#             level = level_order_list[i]
#             score_dict[date][level] = {}
#             score_dict[date][level]["min"] = MINPLATFORMSCORE + 1
#             score_dict[date][level]["max"] = MAXPLATFORMSCORE
#             if i == 0:
#                 score_dict[date][level]["min"] = lever_score_dict[level][date]["score"]
#             elif i == level_number - 1:
#                 score_dict[date][level]["max"] = lever_score_dict[level_order_list[i - 1]][date]["score"]
#             else:
#                 score_dict[date][level]["min"] = lever_score_dict[level][date]["score"]
#                 score_dict[date][level]["max"] = lever_score_dict[level_order_list[i - 1]][date]["score"]
#     
    #判断是增量还是全量
    isreset = 0
    if (len(sys.argv) == 2):
        if (sys.argv[1] == "reset"):
            print "Reset '" + SRCDB_INDEX_TARGET + "'"
            print
            start = 0
            cur_dev.execute("DELETE FROM " + SRCDB_INDEX_TARGET)
            conn_dev.commit()
            isreset = 1
    if isreset == 0:
        print "Update '" + SRCDB_INDEX_TARGET + "'"
        print
        start = date_number - 1
        stringSQL = "DELETE FROM " + SRCDB_INDEX_TARGET + " WHERE `date` = '" + str(date_list_E1[-1]) + "'"
        cur_dev.execute(stringSQL)
        conn_dev.commit()
        
    #2.对每一个E1中的时刻，判断waiting-list并进行相应的操作
    for _date in date_list_E1[start : date_number]:
        date_waiting = getValueNoMoreThanValue(_date, date_list_waiting)
        if None == date_waiting:
            continue
        
        #2.1.从y表中获得历史坏站
        bad_platform_list_history = []
        stringSQL = "SELECT DISTINCT `platform_name` FROM " + SRCDB_Y + " WHERE `date` <= '" + str(_date) + "' AND `status` < '1' ORDER BY `platform_name` ASC" 
        _number = cur1_db.execute(stringSQL)
        if _number != 0:
            for field_temp in cur1_db.fetchall():
                bad_platform_list_history.append(field_temp[0])
        bad_platform_number_history = len(bad_platform_list_history)
        if 0 != bad_platform_number_history:
            print "截至" + str(_date) + "这个时间节点，已经有" + str(bad_platform_number_history) + "个坏站."
        else:
            print "截至" + str(_date) + "这个时间节点，还没出现坏站."
        
        #2.2.从Y表获得当周的坏站
        bad_platform_dict_havingdata = {}
        bad_platform_dict_nothavingdata = {}
        stringSQL = "SELECT `platform_name`, MIN(status) FROM " + SRCDB_Y + " WHERE `date` <= '" + str(_date) + "' AND `date` > '" + str(_date - SECONDSPERWEEK) + "' AND `status` < 1 GROUP BY platform_name"
        cur1_db.execute(stringSQL)
        for platform_name, status in cur1_db.fetchall():
            platform_name = str(platform_name)
            stringSQL = "SELECT `weekly_outstanding_loan` FROM " + SRCDB_E1 + " WHERE `date` = '" + str(_date) + "' AND `platform_name`  = '" + str(platform_name) + "'" 
            ret = cur1_db.execute(stringSQL)
            if ret == 0:
                bad_platform_dict_nothavingdata[platform_name] = {}
                bad_platform_dict_nothavingdata[platform_name]["status"] = str(status)
                bad_platform_dict_nothavingdata[platform_name]["platform_id"] = hashlib.md5(platform_name).hexdigest()[0:10]
            else:
                if float(cur1_db.fetchone()[0]) == 0:
                    bad_platform_dict_nothavingdata[platform_name] = {}
                    bad_platform_dict_nothavingdata[platform_name]["status"] = str(status)
                    bad_platform_dict_nothavingdata[platform_name]["platform_id"] = hashlib.md5(platform_name).hexdigest()[0:10]
                else:
                    bad_platform_dict_havingdata[platform_name] = {}
                    bad_platform_dict_havingdata[platform_name]["fields"] = getString(getNoneZeroListByPeriod(cur1_db, SRCDB_E1, _field_list, platform_name, _date, INDEXTOLERANCE, 0))
                    bad_platform_dict_havingdata[platform_name]["status"] = str(status)
                    bad_platform_dict_havingdata[platform_name]["platform_id"] = hashlib.md5(platform_name).hexdigest()[0:10]
                    bad_platform_dict_havingdata[platform_name]["value"] = value_format % getValue(cur2_db,SRCDB_E1,["weekly_lending", "weekly_total_investor"],platform_name,_date,INDEXTOLERANCE)

        #2.3.将坏站写入数据库
        bad_platform_havingdata_number = len(bad_platform_dict_havingdata)
        bad_platform_havingdata_list = bad_platform_dict_havingdata.keys()
        bad_platform_nothavingdata_number = len(bad_platform_dict_nothavingdata)
        bad_platform_nothavingdata_list = bad_platform_dict_nothavingdata.keys()
        bad_platform_list = bad_platform_havingdata_list + bad_platform_nothavingdata_list
        bad_platform_number = len(bad_platform_list)
        if bad_platform_number != 0:
            print "本周一共有" + str(bad_platform_number) + "个坏站."
            if bad_platform_havingdata_number != 0:
                print "其中有" + str(bad_platform_havingdata_number) + "个坏站有数据，分别是："
                for platform_name in bad_platform_dict_havingdata:
                    print platform_name
                    fields_list = _field_list + ["date", "platform_name", "platform_id", "status", "rank_value", "source",  "value_new"]
                    value_list = bad_platform_dict_havingdata[platform_name]["fields"] + [str(_date), platform_name, bad_platform_dict_havingdata[platform_name]["platform_id"], str(bad_platform_dict_havingdata[platform_name]["status"]), "10000", "-1", bad_platform_dict_havingdata[platform_name]["value"]]
                    stringSQL = "INSERT INTO " + SRCDB_INDEX_TARGET + "(`" + "`,`".join(fields_list) + "`) VALUES('" + "','".join(value_list) + "')"
                    cur_dev.execute(stringSQL)
                    conn_dev.commit()
                print
                 
            if bad_platform_nothavingdata_number != 0:
                print "其中有" + str(bad_platform_nothavingdata_number) + "个坏站没有数据，分别是："
                for platform_name in bad_platform_dict_nothavingdata:
                    print platform_name
                    fields_list = ["date", "platform_name", "platform_id", "status", "rank_value", "source"]
                    value_list = [str(_date), platform_name, bad_platform_dict_nothavingdata[platform_name]["platform_id"], str(bad_platform_dict_nothavingdata[platform_name]["status"]), "20000", "-2"]
                    stringSQL = "INSERT INTO " + SRCDB_INDEX_TARGET + "(`" + "`,`".join(fields_list) + "`) VALUES('" + "','".join(value_list) + "')"
                    cur_dev.execute(stringSQL)
                    conn_dev.commit()
                print
                    
        #2.4.从SRCDB_INDEX_WAITING表中获得所有的站，并根据来源设置不同的时间阈值，同时判断是否有效并插入E1数据
        stringSQL = "SELECT platform_name, value, source FROM " + SRCDB_INDEX_WAITING + " WHERE `date` = '" + str(date_waiting) + "' ORDER BY `rank` ASC"
        waiting_list_number = cur_dev.execute(stringSQL)
        print "对应的waiting_list时间节点为" + str(date_waiting) + ", 在waiting list 中有" + str(waiting_list_number) + "个站." 
        rank = 0
        bad_platform_list_new = []
        bad_platform_number = 0
        notvalid_best_platform_list = []
        notvalid_best_platform_number = 0
        notvalid_normal_platform_list = []
        notvalid_normal_platform_number = 0
        platform_name_list_good = []
        good_platform_weeks_dict = {}
        for platform_name, _value, source in cur_dev.fetchall():
            platform_name = str(platform_name)
            _value = float(_value)
            source = int(source)
            status = 1
            if platform_name in bad_platform_list_history:
                bad_platform_number += 1
                bad_platform_list_new.append(platform_name)
                continue
            else:
                if source == 1:
                    last_weeks = 12
                    value_list = getNoneZeroListByPeriod(cur1_db, SRCDB_E1, _field_list, platform_name, _date, last_weeks, 0)
                    if checkZeroNumber(value_list)[0] != 0:
                        notvalid_best_platform_number += 1
                        notvalid_best_platform_list.append(platform_name)
                        continue
                else:
                    value_list = getFieldsListFromTableByNameByDate(cur1_db, SRCDB_E1, platform_name, _date, _field_list)
                    if value_list == None:
                        continue
                    value_list = getFloat(value_list)
                    isValid = checkValid(_field_list, value_list, ["weekly_lending"], 2)
                    if isValid == 0:
                        notvalid_normal_platform_number += 1
                        notvalid_normal_platform_list.append(platform_name)
                        continue
                    else:
                        last_weeks = 4
                        value_list = getNoneZeroListByPeriod(cur1_db, SRCDB_E1, _field_list, platform_name, _date, last_weeks, 0)
                        if checkZeroNumber(value_list)[0] != 0:
                            notvalid_normal_platform_number += 1
                            notvalid_normal_platform_list.append(platform_name)
                            continue
            rank += 1
            platform_name_list_good.append(platform_name)
            good_platform_weeks_dict[platform_name] = last_weeks
            platform_id = hashlib.md5(platform_name).hexdigest()[0:10]
            value_new = getValue(cur2_db,SRCDB_E1,["weekly_lending", "weekly_total_investor"],platform_name,_date,last_weeks)
            fields_list = _field_list + ["date", "platform_name", "platform_id", "status", "rank_value", "source",  "value", "value_new"]
            value_list = getString(value_list) + [str(_date), platform_name, platform_id, str(status), str(rank), str(source), value_format % _value, value_format % value_new]
            stringSQL = "INSERT INTO " + SRCDB_INDEX_TARGET + "(`" + "`,`".join(fields_list) + "`) VALUES('" + "','".join(value_list) + "')"
            cur_dev.execute(stringSQL)
            conn_dev.commit()
            if rank == RANKALL:
                break
        print "截止前" + str(RANKALL + bad_platform_number) + "名，有" + str(bad_platform_number) + "个waiting_list的站截止至这周变为坏站."
        if bad_platform_number != 0:
            for platform_name in bad_platform_list_new:
                print platform_name
            print
        print "有" + str(notvalid_best_platform_number) + "个已有优选站(50)没有满足有效数据(12周)的定义."
        if notvalid_best_platform_number != 0:
            for platform_name in notvalid_best_platform_list:
                print platform_name
            print
        print "有" + str(notvalid_normal_platform_number) + "个已有平常站没有满足有效数据(4周)的定义."
        if notvalid_normal_platform_number != 0:
            for platform_name in notvalid_normal_platform_list:
                print platform_name
            print
        
        #3.获得所有站的score和评级level并进行排名
        #3.1.先处理好站
        platform_score_dict = {}
        for platform_name in platform_name_list_good:
#             date_temp, score = getValueByPeriod(cur_dev, SRCDB_T, "score", platform_name, _date, good_platform_weeks_dict[platform_name])
#             if score != None:
#                 for level in level_order_list:
#                     if score_dict[date_temp][level]["min"] <= score < score_dict[date_temp][level]["max"]:
#                         _level = level
#                         break
#                 platform_score_dict[platform_name] = {}
#                 platform_score_dict[platform_name]["score"] = score
#                 platform_score_dict[platform_name]["level"] = _level
            date_temp, score, level = getValueListByPeriod(cur_dev, SRCDB_T, ["score", "level"], platform_name, _date, good_platform_weeks_dict[platform_name])
            platform_score_dict[platform_name] = {}
            platform_score_dict[platform_name]["score"] = score
            platform_score_dict[platform_name]["level"] = level
        good_platform_sorted_list = sortDictByKeyValue(platform_score_dict, "score")[0]
        rank_score = 0
        for platform_name in good_platform_sorted_list:
            rank_score += 1
            stringSQL = "UPDATE " + SRCDB_INDEX_TARGET + " SET `score` = '" + str(platform_score_dict[platform_name]["score"]) + "', `rank_score` = '" + str(rank_score) + "', `level` ='" + str(platform_score_dict[platform_name]["level"]) + "' WHERE `platform_name` = '" + platform_name + "' AND `date` = '" + str(_date) + "'"    
            cur_dev.execute(stringSQL)
            conn_dev.commit()
                    
        #3.2.再处理坏站
        for platform_name in bad_platform_havingdata_list:
#             score = getFieldFromTableByNameByDate(cur_dev,SRCDB_T,platform_name,_date,"score")
#             if score != None:
#                 for level in level_order_list:
#                     if score_dict[_date][level]["min"] <= score < score_dict[_date][level]["max"]:
#                         _level = level
#                         break
#             else:
#                 _level = "C" 
            result = getFieldsFromTableByNameByDate(cur_dev,SRCDB_T,platform_name,_date,["score","level"])
            if result != None:
                score, _level = result
            else:
                score, _level = None, "C"
            stringSQL = "UPDATE " + SRCDB_INDEX_TARGET + " SET `score` = '" + str(score) + "', `level` ='" + str(_level) + "' WHERE `platform_name` = '" + platform_name + "' AND `date` = '" + str(_date) + "'"    
            stringSQL = stringSQL.replace("'None'", "NULL")
            cur_dev.execute(stringSQL)
            conn_dev.commit()
                
        #4为所有的站添加   'weekly_ave_bid_close_time'指标值
        platform_name_list_havingdata = platform_name_list_good + bad_platform_havingdata_list
        for platform_name in platform_name_list_havingdata:
            key_value_list = []
            if platform_name in platform_name_list_good:
                last_weeks = good_platform_weeks_dict[platform_name]
            else:
                last_weeks = 4
            for field in _fields_list_add:
                value = getValueByPeriod(cur1_db, SRCDB_E1, field, platform_name, _date, last_weeks)[1]
                key_value_list.append("`" + field + "` = '" + str(value) + "'")
            stringSQL = "UPDATE " + SRCDB_INDEX_TARGET + " SET " + ",".join(key_value_list) + " WHERE `platform_name` = '" + platform_name + "' AND `date` = '" + str(_date) + "'"    
            stringSQL = stringSQL.replace("'None'", "NULL")
            cur_dev.execute(stringSQL)
            conn_dev.commit()
            
    closeCursors(cur_dev, cur1_db, cur2_db)
    closeConns(conn_dev, conn_db)
    _end_time = time.time()
    print "The whole program costs " + str(_end_time - _start_time) + " seconds."  
    
