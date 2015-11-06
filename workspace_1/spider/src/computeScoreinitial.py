#!/use/bin/python
#coding=utf-8

import time
from atbtools.header import *
from atbtools.computeTools import *
from math import ceil
import numpy as np

if __name__ == "__main__":
    
    startTime = time.time()
    #获得连接        
    conn = getConn("127.0.0.1", "xiebo", "123456", "antoubao", 3306)
    cur = getCursors(conn)
    initializeCursors(cur)
    
    E2_new = "wd_shujuinfo"
    T = "wd_data_platform_score"
    T_history = "wd_data_platform_score_history"
    V = "v_view"
    
    field_list = getAllColumnsFromTable(cur, T, del_list = ["Id, level, var_score, rank"])
    field_number = len(field_list)
    date_list = getDifferentFieldlist(V, cur, "date")
    this_date = date_list[-1]
    last_date = date_list[-2]
    
    #安投宝前20名的平台
    atb_number = 30
    atb_top_dict = {}
    stringSQL = "SELECT `platform_name`, `rank_score` FROM "+ V + " WHERE `date` = '" + str(this_date) + "' ORDER BY `rank_score` LIMIT " + str(atb_number)
    ret = cur.execute(stringSQL)
    for platform_name, rank_score in cur.fetchall():
        atb_top_dict[platform_name] = rank_score
    
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
    
    
    #先录入数据
    platform_name_list = getDifferentFieldlistByDate(E2_new, cur, "platform_name", this_date)
    score_dict = {}
    score_dict[this_date] = {}
    score_dict[last_date] = {}
    for platform_name in platform_name_list:
        stringSQL = "SELECT `platform_name`, `date`, `score` FROM "+ V + " WHERE `platform_name` = '" + platform_name + "' AND (`date` = '" + str(this_date) + "' OR `date` = '" + str(last_date) + "')"
        ret = cur.execute(stringSQL)
        for platform_name, date, score in cur.fetchall():
            score_dict[date][platform_name] = score
    
    stringSQL = "TRUNCATE " + T_history
    cur.execute(stringSQL)
    conn.commit()
    
    #调整排名，每个级别内随机分组调整
    team_number = 3
    level_number = len(level_list)
    for date in score_dict:
        level_dict = {}
        platform_order_list, value_order_list = sortDictByValue(score_dict[date])
        initial_score_dict = dict(zip(platform_order_list, value_order_list))
        platform_number = len(initial_score_dict)
        print "当前时间：" + str(date) + "(" + time.strftime("%Y-%m-%d", time.localtime(date)) + ")"
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
            stringSQL = "INSERT INTO " + T_history + " (`platform_name`, `date`, `score`, `rank_score`, `level`) VALUES('" + "', '".join([platform_name, str(date), str(score), str(rank_score), level_dict[platform_name]]) + "')"
            cur.execute(stringSQL)
            conn.commit()
            
        #在wd_shujuinfo中插入评级
        if date == this_date:
            for i in range(platform_number):
                platform_name = platform_order_list[i]
                stringSQL = "UPDATE " + E2_new + " SET `level` = '" + level_dict[platform_name] + "' WHERE `platform_name` = '" + platform_name + "' AND `date` = '" + str(this_date) + "'"
                cur.execute(stringSQL)
                conn.commit()
            for platform_name in atb_top_dict:
                if platform_name not in platform_order_list:
                    print "在安投宝前" + str(atb_number) + "名中，缺少：" + str(platform_name) + "，它的排名是：" + str(atb_top_dict[platform_name]) + "."
        print         
    #计算排名变化
    date_list = getDifferentFieldlist(T_history, cur, "date")
    rank_score_dict = {}
    for date in date_list:
        rank_score_dict[date] = {}
    stringSQL = "SELECT `platform_name`, `date`, `rank_score` FROM " + T_history
    cur.execute(stringSQL)
    for platform_name, date, rank_score in cur.fetchall():
        rank_score_dict[date][platform_name] = rank_score
    for date in date_list[1:]:
        var_score_dict = {}
        last_date = date - SECONDSPERWEEK
        platform_number = len(rank_score_dict[date])
        ave_var_score = 0
        count = 0
        for platform_name in rank_score_dict[date]:
            if platform_name in rank_score_dict[last_date]:
                var_score = rank_score_dict[last_date][platform_name] - rank_score_dict[date][platform_name]
                var_score_dict[platform_name] = var_score
                ave_var_score += var_score
                count += 1
        ave_var_score = ave_var_score / count
        for platform_name in rank_score_dict[date]:
            if platform_name not in rank_score_dict[last_date]:
                var_score_dict[platform_name] = ave_var_score
        for platform_name in rank_score_dict[date]:
            stringSQL="UPDATE " + T_history + " SET `var_score` = '"+str(var_score_dict[platform_name])+"' WHERE `platform_name` = '" + platform_name + "' AND `date` = '"+str(date)+"'"
            cur.execute(stringSQL)
            conn.commit()
    
    #插入最新数据
    stringSQL = "TRUNCATE " + T
    cur.execute(stringSQL)
    conn.commit()
    this_date = date_list[-1]
    field_list = getAllColumnsFromTable(cur, T_history, del_list = ["Id"])
    stringSQL = "SELECT `"+"`, `".join(field_list)+"` FROM " +  T_history + " WHERE `date` = '"+str(this_date)+"'"
    cur.execute(stringSQL)
    rows = cur.fetchall()
    for row in rows:
        value_list = getString(row)
        stringSQL = "INSERT INTO " + T + " (`" + "`, `".join(field_list) + "`) VALUES('" + "', '".join(value_list) + "')"
        cur.execute(stringSQL)
        conn.commit()
    
    closeCursors(cur)
    closeConns(conn)        
    print ""
    print "finished"
    endTime = time.time()
    print "The whole program costs " + str(endTime - startTime) + " seconds."        