# /usr/bin/python
# coding=utf8

#1.获得指数指标的时间节点
#2.在E1表中寻找所有非坏站并依据value进行排序

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
import time
import hashlib
import sys

def checkLack(_cur, _table, _field_list, _platform_name, _date):
    value_list = getFieldsFromTableByNameByDate(_cur, _table, _platform_name, _date, _field_list)
    if value_list == None:
        return "#lack"
    else:
        if checkZeroNumber(value_list)[0] != 0 :
            return "#lack"
        else:
            return ""
    
if __name__ == '__main__':
    _start_time = time.time()
    #获得连接        
    conn_ddpt = getConn(DDPT_TESTHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_ddpt = getCursors(conn_ddpt)
    conn_dev = getConn(DEVHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_dev = getCursors(conn_dev)
    initializeCursors(cur_ddpt, cur_dev)
    
    SRCDB_Y = "2_total_status" #ddpt_test
    SRCDB_E2 = "0_E2_quantitative_data" #ddpt_test
    SRCDB_Z = "01_platform_problem_doubt_Z" #ddpt_test
    SRCDB_VIEW_MOBILE = "view_mobile" #dev
    
    #1.获得指数指标的时间节点
    initial_date = 1439654400
    date_list = getDifferentFieldlist(SRCDB_E2, cur_ddpt, "date")
    this_date = date_list[-1]
    last_date = this_date - SECONDSPERWEEK
    last4weeks_list = [last_date - i * SECONDSPERWEEK for i in range(4)]

    #删除本周数据，后面会重新填充
    stringSQL = "DELETE FROM " + SRCDB_Z + " WHERE `date` = '" + str(this_date) +"'"
    cur_ddpt.execute(stringSQL)
    conn_ddpt.commit()
    
    #获得所有平台的status属性
    status_dict_good = {}
    date_dict_good = {}
    stringSQL = "SELECT A.platform_name, A.`date`, A.status FROM " + SRCDB_Y + " AS A,(SELECT `platform_name`, MAX(`date`) AS `date` FROM " + SRCDB_Y + " GROUP BY `platform_name`) AS B WHERE A.platform_name = B.platform_name AND A.`date` = B.`date`"
    ret = cur_ddpt.execute(stringSQL)
    rows = cur_ddpt.fetchall()
    for row in rows:
        platform_name = row[0]
        date = row[1]
        status = float(row[2])
        if status >= 0.997:
            status_dict_good[platform_name] = status
            date_dict_good[platform_name] = date
    #2.在E2表中寻找所有非坏站并依据value进行排序，在上一周已在白名单内的站本周也直接进入白名单，否则按照排名补充至白名单
    white_platform_number = 70
    score_dict = {}
    lack_dict = {}
    for platform_name in status_dict_good:
        value = getValue(cur_ddpt, SRCDB_E2, ["weekly_lending", "weekly_total_investor"], platform_name, this_date, 6, 0.6, 0.4)
        if value > 0 :
            score_dict[platform_name] = value
            lack_dict[platform_name] = checkLack(cur_ddpt, SRCDB_E2, ["weekly_lending", "weekly_total_investor"], platform_name, this_date)
    good_platform_list_sorted = sortDictByValue(score_dict)[0]
    good_platform_number = len(good_platform_list_sorted)

    platform_list_last = getDifferentFieldlistByDate(SRCDB_Z, cur_ddpt, "platform_name", last_date)
    platform_repeat_list = list(set(good_platform_list_sorted) & set(platform_list_last))
    white_platform_name_list = platform_repeat_list
    platform_repeat_number = len(platform_repeat_list)
    platform_add_number = white_platform_number - platform_repeat_number
    print "截至本周，一共有" + str(good_platform_number) + "个好站有数据，其中有" + str(platform_repeat_number) + "个站和上一周相同，直接进入白名单."
    count = platform_repeat_number
    if count < white_platform_number:
        for i in range(good_platform_number):
            platform_name = good_platform_list_sorted[i]
            if platform_name not in platform_repeat_list:
                white_platform_name_list.append(platform_name)
                count += 1
                if count == white_platform_number:
                    break
    
    #3.重写根据score计算排名
    white_score_dict = {}
    for platform_name in white_platform_name_list:
        white_score_dict[platform_name] = score_dict[platform_name]
    white_platform_name_list_sorted = sortDictByValue(white_score_dict)[0]
    
    #写入数据库
    rank = 0
    status_dict_new = {}
    field_list = ["platform_id", "platform_name", "date", "rank", "score", "status", "lack"]
    for i in range(white_platform_number):
        rank += 1
        platform_name = white_platform_name_list_sorted[i]
        platform_id = hashlib.md5(platform_name).hexdigest()[0:10]
        status_dict_new[platform_name] = 2.5 - 0.01 * rank
        stringSQL = "INSERT INTO " + SRCDB_Z + "(`" + "`,`".join(field_list) + "`) VALUES('" + "','".join([platform_id, platform_name, str(this_date), str(rank), str(white_score_dict[platform_name]), str(status_dict_new[platform_name]), str(lack_dict[platform_name])]) + "')"
        cur_ddpt.execute(stringSQL)
        conn_ddpt.commit()
    
    ATB_top20_dict = {}
    date_list_V = getDifferentFieldlist(SRCDB_E2, cur_ddpt, "date")
    max_date = max(date_list_V)
    #曾经的白名单删除
    stringSQL = "SELECT `id` FROM " + SRCDB_Y + " WHERE `date` < '" + str(max_date) + "' AND `status` > '1' AND `description` = '平台优秀'" 
    cur_ddpt.execute(stringSQL)
    rows = cur_ddpt.fetchall()
    for _id in rows:
        stringSQL = "UPDATE " + SRCDB_Y  + " SET `status` = '1', `description` = '平台正常' WHERE `id` = '" + str(_id[0]) + "'" 
        cur_ddpt.execute(stringSQL)
        conn_ddpt.commit()
    #4.修改原来的total_status表，没有进入白名单的为1，进入白名单的更新status
    stringSQL = "SELECT `platform_name`, `rank_score` FROM " + SRCDB_VIEW_MOBILE + " WHERE `date` = '" + str(max_date) + "' AND `rank_score` <= '20'" 
    cur_dev.execute(stringSQL)
    rows = cur_dev.fetchall()
    for row in rows:
        platform_name = row[0]
        rank_score = row[1]
        ATB_top20_dict[platform_name] = rank_score
    del_number = 0
    for platform_name in status_dict_good:
        if platform_name in white_platform_name_list_sorted:
            status = status_dict_new[platform_name]
            description = "平台优秀"
        else:
            status = 1
            description = "平台正常"
            if platform_name in ATB_top20_dict:
                del_number += 1
                print str(del_number) + ": " + platform_name + "在前20(" + str(ATB_top20_dict[platform_name]) + ")，但是目前会被改为status = 1的平常站;"
                stringSQL = "SELECT MAX(`date`) FROM " + SRCDB_E2  + " WHERE `platform_name` ='" + platform_name + "'"
                cur_ddpt.execute(stringSQL)
                _date = cur_ddpt.fetchone()[0]
                print "    它在E2中的最近时间戳为" + str(_date) + ";"
                if _date < max_date:
                    print "    这样做可能会导致它无法进入后面的补充历史数据阶段。"
                else:
                    print "    因为该时间戳等于目前计算的时间戳，因此这样做是安全的。"
        stringSQL = "UPDATE " + SRCDB_Y  + " SET `status` = '" + str(status) + "', `date` = '" + str(this_date) + "', `description` = '" + description + "' WHERE `platform_name` = '" + platform_name + "' AND `date` = '" + str(date_dict_good[platform_name]) + "' AND `status` > '0.997'" 
        cur_ddpt.execute(stringSQL)
        conn_ddpt.commit()
    closeCursors(cur_ddpt, cur_dev)
    closeConns(conn_ddpt, conn_dev)
    _end_time = time.time()
    print "The whole program costs " + str(_end_time - _start_time) + " seconds."  
    
