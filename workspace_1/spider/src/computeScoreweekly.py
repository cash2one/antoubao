#!/use/bin/python
#coding=utf-8

"""
V：历史（C）不动，C + D = C，每个站都历史数据完整（只展示最新1周的数据）
1.取出老V中最新的排名与E2中最新的A的交集D（注意D不要超过ATB的80%，如果超过的话，与上一周的C取交集，然后随机增加一些站）；
2.按照百分比确定每个平台的level；同一个level中分成三块，每一块随机排列，得到最新的排名；
3.计算和上一周的排名差；：对于D中已经在C中的站，直接计算排名差即可；对于D中没有在C中的站，则用本周所有站平均排名变动补充；
4.取出最新1周的数据进入数据库。
#5.取出最近10周的数据进入数据库。
# 6.补充历史上所有站的排名，重新计算所有站的排名（在5的时候可能有重复的名词，拿出来重新排一次即可）
"""

import time
from atbtools.header import *
from atbtools.computeTools import *
from math import ceil
import numpy as np

if __name__ == "__main__":
    
    startTime = time.time()
    #平台名称更正
    change_name_dict = {}
    change_name_dict["前海理想"] = "前海理想金融"
    
    #数据库定义
    V = "V_view" #ddpt-data
    VIEW_MOBILE = "view_mobile" #dev-x1
    Y = "total_status" #db-x1
    E2_old = "E2_quantitative_data" #dev-x1
    E2_new = "wd_shujuinfo_history" #local
    E2_online = "wd_shujuinfo" #local
    T = "wd_data_platform_score_history" #local
    T_online = "wd_data_platform_score" #local
    
    #设置连接
    conn_db = getConn(DBHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    conn_ddpt = getConn(DDPT_DATAHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_ddpt = getCursors(conn_ddpt)
    conn_dev = getConn(DEVHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_dev = getCursors(conn_dev)
    conn_local = getConn("127.0.0.1", "xiebo", "123456", "antoubao", 3306)
    cur_local = getCursors(conn_local)
    initializeCursors(cur_db, cur_ddpt, cur_dev, cur_local)
    
    #1.取出老V中最新的排名与E2中最新的A的交集D（注意D不要超过ATB的80%，如果超过的话，与上一周的C取交集，然后随机增加一些站）；
    date_list = []
    stringSQL = "SELECT DISTINCT `date` FROM " + V + " ORDER BY `date` DESC"
    cur_ddpt.execute(stringSQL)
    for field_temp in cur_ddpt.fetchall():
        date_list.append(field_temp[0])
    this_date = int(date_list[0]) #本周
    last_date = int(date_list[1]) #上一周
    last10_date = date_list[:10][-1]
    
    platform_name_last_list = getDifferentFieldlistByDate(T, cur_local, "platform_name", last_date)
    platform_name_last_number = len(platform_name_last_list)
    platform_name_T_list = getDifferentFieldlistByDate(V, cur_ddpt, "platform_name", this_date)
    for platform_name in change_name_dict:
        if platform_name in platform_name_T_list:
            platform_name_T_list.remove(platform_name)
            platform_name_T_list.append(change_name_dict[platform_name]) 
    platform_name_E2_list = getDifferentFieldlistByDate(E2_new, cur_local, "platform_name", this_date)
    platform_name_T_number = len(platform_name_T_list)
    platform_name_E2_number = len(platform_name_E2_list)
    platform_name_list = list(set(platform_name_T_list) & set(platform_name_E2_list))
    
    platform_name_number = len(platform_name_list)
    print "本周ATB一共有" + str(platform_name_T_number) + "个平台有分数."
    print "而我们的E2历史数据库中有" + str(platform_name_E2_number) + "个平台有历史字段值."
    print "两者取交集，本周共有" + str(platform_name_number) + "个平台进入记录，占ATB的比例为: " + str(float(platform_name_number)/platform_name_T_number)
    
    #安投宝前30名的平台
    atb_number = 30
    atb_top_dict = {}
    stringSQL = "SELECT `platform_name`, `rank_score` FROM "+ V + " WHERE `date` = '" + str(this_date) + "' ORDER BY `rank_score` LIMIT " + str(atb_number)
    ret = cur_ddpt.execute(stringSQL)
    for platform_name, rank_score in cur_ddpt.fetchall():
        if platform_name in change_name_dict:
            platform_name = change_name_dict[platform_name]
        atb_top_dict[platform_name] = rank_score
        
    #2.按照百分比确定每个平台的level；
    #删除本周数据，后面会重新填充
    #可注释
    stringSQL = "DELETE FROM " + T + " WHERE `date` = '" + str(this_date) + "'"
    print stringSQL
    ret = cur_local.execute(stringSQL)
    if ret != 0:
        print "会从T_history中删除数据，请谨慎操作."
        #exit(0)
    conn_local.commit()
    
    #确定每个等级的平台个数
    score_max = 95
    score_min = 10
    score_k = float(score_max - score_min) / 100
    level_list = ["A+", "A", "B+", "B", "C+", "C", "D"]
    level_number = len(level_list)
    level_percent_dict = {"A+":0.04, "A":0.12, "B+":0.16, "B":0.18, "C+":0.26, "C":0.16, "D":0.08}
    score_accuracy = 0.1
    score_level_dict = {}
    for i in range(level_number):
        level = level_list[i]
        score_level_dict[level] = {}
        if i == 0:
            score_level_dict[level]["high"] = 100
            score_level_dict[level]["low"] = 100 - level_percent_dict[level] * 100 + score_accuracy
        else:
            last_level = level_list[i - 1]
            score_level_dict[level]["high"] = score_level_dict[last_level]["low"] - 2 * score_accuracy  
            score_level_dict[level]["low"] = score_level_dict[level]["high"] - level_percent_dict[level] * 100 + score_accuracy  
        if i == level_number - 1:
            score_level_dict[level]["low"] = 0
            
    #接受本周得分情况
    score_dict = {}
    for platform_name in platform_name_list + change_name_dict.keys():
        stringSQL = "SELECT `platform_name`, `score` FROM "+ V + " WHERE `platform_name` = '" + platform_name + "' AND `date` = '" + str(this_date) + "'"
        ret = cur_ddpt.execute(stringSQL)
        for platform_name, score in cur_ddpt.fetchall():
            if platform_name in change_name_dict:
                platform_name = change_name_dict[platform_name]
            score_dict[platform_name] = score
    
    #调整排名，每个级别内随机分组调整
    team_number = 3
    level_number = len(level_list)
    level_dict = {}
    platform_order_list, value_order_list = sortDictByValue(score_dict)
    initial_score_dict = dict(zip(platform_order_list, value_order_list))
    platform_number = len(initial_score_dict)
    print "当前时间：" + str(this_date) + "(" + time.strftime("%Y-%m-%d", time.localtime(this_date)) + ")"
    print "一共有：" + str(platform_number) + "进入最终排名."

    #调整排名，每个级别内随机调整
    level_number_dict = {}
    rank_score_dict = {}
    each_level_number_dict = {}
    _sum = 0
    for i in range(level_number):
        level = level_list[i]
        this_level_number = int(platform_number * level_percent_dict[level])
        level_number_dict[level] = this_level_number
        if i < level_number - 1:
            each_level_number_dict[level] = this_level_number
            _sum += this_level_number
        else:
            each_level_number_dict[level] = platform_number - _sum
        if i > 0:
            level_number_dict[level] += level_number_dict[level_list[i - 1]]
        if i == level_number - 1:
            level_number_dict[level] = platform_number
    
    for i in range(level_number):
        level = level_list[i]
        if i == 0:
            start = 0
        else:        
            start = level_number_dict[level_list[i - 1]]
        platform_name_list_temp = platform_order_list[start : level_number_dict[level_list[i]]]
        platform_number_temp = len(platform_name_list_temp)
        for platform_name in platform_name_list_temp:
            level_dict[platform_name] = level
        per_number = platform_number_temp / team_number
        team_list = [per_number] * (team_number - 1)
        team_list.append(platform_number_temp - sum(team_list))
        for i in range(team_number):
            if i < team_number - 1:
                _platform_name_list = platform_name_list_temp[per_number * i : per_number * (i + 1)]
                _list = random.sample(range(per_number), per_number)
            else:
                _platform_name_list = platform_name_list_temp[per_number * i :]
                _list = random.sample(range(team_list[team_number - 1]), team_list[team_number - 1])
            _score_list = []
            for platform_name in _platform_name_list:
                _score_list.append(initial_score_dict[platform_name])
            for j in range(len(_platform_name_list)):
                platform_name = _platform_name_list[j]
                score = _score_list[_list[j]]
                initial_score_dict[platform_name] = score
    #获得得分列表
    platform_order_list = sortDictByValue(initial_score_dict)[0]
    score_list = []
    for level in level_list:
        score_list_level = np.arange(score_level_dict[level]["low"], score_level_dict[level]["high"], 0.01).tolist()
        score_list += sorted(random.sample(score_list_level, each_level_number_dict[level]), reverse = True)
    for i in range(1, platform_number - 1):
        if score_list[i] == score_list[i - 1] or score_list[i] == score_list[i + 1]:
            score_list[i] = (score_list[i - 1] + score_list[i + 1]) / 2
    score_list = [ float("%.2f" % (score_k * x + score_min)) for x in score_list]
    rank_score = 0
    for i in range(platform_number):
        platform_name = platform_order_list[i]
        score = score_list[i]
        rank_score += 1
        rank_score_dict[platform_name] = rank_score
        #可注释
        stringSQL = "INSERT INTO " + T + " (`platform_name`, `date`, `score`, `rank_score`, `level`) VALUES('" + "', '".join([platform_name, str(this_date), str(score), str(rank_score), level_dict[platform_name]]) + "')"
        cur_local.execute(stringSQL)
        conn_local.commit()
        
    #在wd_shujuinfo中插入评级
    for i in range(platform_number):
        platform_name = platform_order_list[i]
        stringSQL = "UPDATE " + E2_new + " SET `level` = '" + level_dict[platform_name] + "' WHERE `platform_name` = '" + platform_name + "' AND `date` = '" + str(this_date) + "'"
        cur_local.execute(stringSQL)
        conn_local.commit()
    for platform_name in atb_top_dict:
        if platform_name not in platform_order_list:
            print "在安投宝前" + str(atb_number) + "名中，缺少：" + str(platform_name) + "，它的排名是：" + str(atb_top_dict[platform_name]) + "."
    print  
    
    print "上周一共有" + str(platform_name_last_number) + "个平台进入计分."
    print "本周相比于上一周："
    platform_name_add_list = list(set(platform_name_list) - set(platform_name_last_list))
    platform_name_subtract_list = list(set(platform_name_last_list) - set(platform_name_list))
    platform_name_add_number = len(platform_name_add_list)
    platform_name_subtract_number = len(platform_name_subtract_list)
    print "多了" + str(platform_name_add_number) + "个平台."
    if platform_name_add_number != 0:
        for platform_name in platform_name_add_list:
            print platform_name
    print "少了" + str(platform_name_subtract_number) + "个平台."
    if platform_name_subtract_number != 0:
        for platform_name in platform_name_subtract_list:
            print platform_name

    #3.计算和上一周的排名差；：对于D中已经在C中的站，直接计算排名差即可；对于D中没有在C中的站，则用本周所有站平均排名变动补充；
    rank_score_dict = {}
    rank_score_dict[this_date] = {}
    rank_score_dict[last_date] = {}
    stringSQL = "SELECT `platform_name`, `date`, `rank_score` FROM " + T + " WHERE `date` = '" + str(this_date) + "' OR `date` = '" + str(last_date) + "'"
    cur_local.execute(stringSQL)
    for platform_name, date, rank_score in cur_local.fetchall():
        rank_score_dict[date][platform_name] = rank_score
        
    #计算本周的平均排名变动
    var_score_dict = {}
    count = 0
    ave_var_score = 0
    firstN = 30
    firstN = min(firstN, platform_name_number)
    firstN_up_number = 0
    firstN_down_number = 0
    firstN_equal_number = 0
    for platform_name in platform_name_list:
        if platform_name in platform_name_last_list:
            count += 1
            var_score = rank_score_dict[last_date][platform_name] - rank_score_dict[date][platform_name]
            if rank_score_dict[date][platform_name] <= 20:
                if var_score > 0:
                    firstN_up_number += 1
                elif  var_score == 0:
                    firstN_equal_number += 1
                else:
                    firstN_down_number += 1
            ave_var_score += var_score
            var_score_dict[platform_name] = var_score
    ave_var_score = ave_var_score / count
    for platform_name in platform_name_list:
        if platform_name not in platform_name_last_list:
            var_score_dict[platform_name] = ave_var_score
    for platform_name in var_score_dict:
        stringSQL="UPDATE " + T + " SET `var_score` = '" + str(var_score_dict[platform_name]) + "' WHERE `platform_name` = '" + platform_name + "' AND `date` = '"+str(this_date)+"'"
        cur_local.execute(stringSQL)
        conn_local.commit()
    #此处需要稍微调整一下，使得上升、下降比例差别不大。
    print "前" + str(firstN) + "名中，名次上升的平台有" + str(firstN_up_number) + "个."
    print "前" + str(firstN) + "名中，名次下降的平台有" + str(firstN_down_number) + "个."
    print "前" + str(firstN) + "名中，名次不变的平台有" + str(firstN_equal_number) + "个."
    
    #4.取出最新1周的数据进入数据库。
    stringSQL = "DELETE FROM " + T_online
    cur_local.execute(stringSQL)
    conn_local.commit()
    field_list = getAllColumnsFromTable(cur_local, T, del_list = ["Id"])
    stringSQL = "SELECT `"+"`, `".join(field_list)+"` FROM " +  T + " WHERE `date` = '"+str(this_date)+"'"
    cur_local.execute(stringSQL)
    rows = cur_local.fetchall()
    for row in rows:
        value_list = getString(row)
        stringSQL = "INSERT INTO " + T_online + " (`" + "`, `".join(field_list) + "`) VALUES('" + "', '".join(value_list) + "')"
        cur_local.execute(stringSQL)
        conn_local.commit()
    
    #5.取出最近10周的数据进入数据库。
    stringSQL = "DELETE FROM " + E2_online
    cur_local.execute(stringSQL)
    conn_local.commit()
    
    field_list_total = getAllColumnsFromTable(cur_local, E2_new, del_list = ["Id", "platform_name"])
    stringSQL = "SELECT `platform_name`, `" + "`, `".join(field_list_total) + "` FROM " +  E2_new + " WHERE `date` >= '" + str(last10_date) + "'"
    ret = cur_local.execute(stringSQL)
    print ret
    rows = cur_local.fetchall()
    for row in rows:
        platform_name = row[0]
        if platform_name in platform_name_list:
            value_list = getString(row[1:])
            stringSQL = "INSERT INTO " + E2_online + " (`" + "`, `".join(["platform_name"] + field_list_total) + "`) VALUES('" + "', '".join([platform_name] + value_list) + "')"
            cur_local.execute(stringSQL)
            conn_local.commit()
        
    closeCursors(cur_db, cur_ddpt, cur_dev, cur_local)
    closeConns(conn_db, conn_ddpt, cur_dev, cur_local)
    print ""
    print "finished"
    endTime = time.time()
    print "The whole program costs " + str(endTime - startTime) + " seconds."        