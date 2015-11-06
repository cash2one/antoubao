#!/usr/bin/python
#encoding=utf-8

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
import sys
def calculateDist(_list_total, _list_target):
    list_total_sorted = sorted(_list_total)
    index_list= []
    for value in _list_target:
        if value not in list_total_sorted:
            print "排名列表出错..."
            exit(-1)
        index_list.append(list_total_sorted.index(value) + 1)
    index_list.sort()
    list_total_number = len(list_total_sorted)
    index_list = [float(x)/list_total_number for x in index_list]
    list_target_number = len(index_list)
    list_target_sum = sum(index_list)
    ave = list_target_sum / list_target_number
    stdev = 0
    for value in index_list:
        stdev += (value - ave) ** 2
    stdev = (stdev / list_target_number) ** 0.5
    max_rank = min(index_list)
    min_rank = max(index_list)
    return ave, stdev, max_rank, min_rank

def calculateDistFromList(_index_list):
    index_list_sorted = sorted(_index_list)
    index_list_number = len(index_list_sorted)
    max_rank = min(index_list_sorted)
    min_rank = max(index_list_sorted)
    ave = sum(index_list_sorted) / index_list_number
    stdev = 0
    for value in index_list_sorted:
        stdev += (value - ave) ** 2
    stdev = (stdev / index_list_number) ** 0.5
    return ave, stdev, max_rank, min_rank

def computeATBDeviation(_last_weeks = 8, _strategy = "", _summary = "", _top_N = 20, _insertSQL = False):
    V = "V_view" #ddpt_data
    V_origin = "V_view" #ddpt_data
    Y = "total_status" #db
    Strategy_list = "99_Strategy_list" #ddpt_test
    
    conn_ddpt_test = getConn(DDPT_TESTHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_ddpt_test = getCursors(conn_ddpt_test)
    conn_ddpt_data = getConn(DDPT_DATAHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_ddpt_data = getCursors(conn_ddpt_data)
    conn_db = getConn(DBHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_ddpt_test, cur_ddpt_data, cur_db)
    
    date_now = time.time()
    date_list = getDifferentFieldlist(V, cur_ddpt_data, "date")[::-1]
    this_date = date_list[0]
    last_date = date_list[1]
    last_weeks_list = date_list[: _last_weeks]
    
    #统计安投宝偏差
    bad_platform_name_list = []
    status_dict = {}
    stringSQL = "SELECT A.platform_name, A.status FROM " + Y + " AS A,(SELECT `platform_name`, MAX(`date`) AS `date` FROM " + Y + " GROUP BY `platform_name`) AS B WHERE A.platform_name = B.platform_name AND A.date = B.date AND A.status < '0.89'"
    cur_db.execute(stringSQL)
    rows = cur_db.fetchall()
    for platform_name, status in rows:
        status_dict[platform_name] = status
        bad_platform_name_list.append(platform_name)
        
    this_date_level_dict = {}.fromkeys(LEVEL_LIST, 0)
    last_weeks_level_dict = {}
    for level in LEVEL_LIST:
        last_weeks_level_dict[level] = [0] * _last_weeks
    level_ratio_dict = {}
    level_ratio_str_dict = {}
    
    stringSQL = "SELECT `platform_name`, `date`, `level` FROM " + V + " WHERE `date` >= '" + str(last_weeks_list[-1]) + "'"
    cur_ddpt_data.execute(stringSQL)
    rows = cur_ddpt_data.fetchall()
    for row in rows:
        platform_name = row[0]
        date = row[1]
        date_index = last_weeks_list.index(date)
        level = row[2]
        last_weeks_level_dict[level][date_index] += 1
        if platform_name in bad_platform_name_list and date == this_date:
            this_date_level_dict[level] += 1
    deviation = 0.0
    deviation_dict = {"A++":0.45, "A+":0.3, "A":0.15, "B++":0.04, "B+":0.03, "B":0.02, "C":0.01}
    standard_dict = {"A++":0, "A+":0, "A":0.01, "B++":0.05, "B+":0.15, "B":0.4, "C":0.8}
    for level in LEVEL_LIST:
        level_ratio_dict[level] = this_date_level_dict[level] / (float(sum(last_weeks_level_dict[level])) / _last_weeks)
#         level_ratio_str_dict[level] = "0" if this_date_level_dict[level] == 0 else str(this_date_level_dict[level]) + "/" + "%.3f" % (float(sum(last_weeks_level_dict[level])) / _last_weeks) + " = " + "%.5f" % level_ratio_dict[level]
        level_ratio_str_dict[level] = str(this_date_level_dict[level]) + "/" + "%.3f" % (float(sum(last_weeks_level_dict[level])) / _last_weeks) + " = " + "%.5f" % level_ratio_dict[level]
        deviation += deviation_dict[level] * (level_ratio_dict[level] - standard_dict[level])
        
    #统计排名变化超过5个的平台的个数
    rank_score_dict_new = {}
    score_dict_new = {}
    level_dict_new = {}
    platform_name_list_new = []
    rank_score_dict_origin = {}
    score_dict_origin = {}
    level_dict_origin = {}
    platform_name_list_origin = []
    count = 0
    for table_name in [V, V_origin]:
        count += 1
        stringSQL = "SELECT `platform_name`, `level`, `rank_score`, `score` FROM " + table_name + " WHERE `date` = '" + str(this_date) + "'"
        _cur = cur_ddpt_data
        if count == 1:
            _rank_score_dict = rank_score_dict_new
            _score_dict = score_dict_new
            _level_dict = level_dict_new
            _list = platform_name_list_new
        else:
            _rank_score_dict = rank_score_dict_origin
            _score_dict = score_dict_origin
            _level_dict = level_dict_origin
            _list = platform_name_list_origin
        _cur.execute(stringSQL)
        rows = _cur.fetchall()
        for row in rows:
            platform_name = row[0]
            level = row[1]
            rank_score = int(row[2])
            score = float(row[3])
            _rank_score_dict[platform_name] = rank_score
            _score_dict[platform_name] = score
            _level_dict[platform_name] = level
            _list.append(platform_name)
    
    rank_change_number_good = 0
    rank_change_number_bad = 0
    level_change_number_good = 0
    level_change_number_bad = 0
    output_str = "平台名称 排名变化 得分变化 等级变化 原排名 现排名 原得分 现得分 原等级 现等级 状态\n"
    output_dict_list = []
    platform_name_list = list(set(platform_name_list_new) & set(platform_name_list_origin))
    platform_name_length_max = 0 
    for platform_name in platform_name_list:
        for letter in "abcdefghijklmnopqrstuvwxyz0123456789":
            if letter in platform_name:
                break
        else:
            platform_name_length_max = max(platform_name_length_max, len(platform_name))
        rank_score_origin = rank_score_dict_origin[platform_name]
        rank_score_new = rank_score_dict_new[platform_name]
        rank_change = rank_score_origin - rank_score_new
        score_origin = score_dict_origin[platform_name]
        score_new = score_dict_new[platform_name]
        score_change = score_new - score_origin
        level_origin = level_dict_origin[platform_name]
        level_new= level_dict_new[platform_name]
        level_change = LEVEL_LIST.index(level_origin) - LEVEL_LIST.index(level_new)
        if abs(rank_change) > 5:
            if platform_name in bad_platform_name_list:
                rank_change_number_bad += 1
            else:
                rank_change_number_good += 1
        if level_new != level_origin:
            if platform_name in bad_platform_name_list:
                level_change_number_bad += 1
            else:
                level_change_number_good += 1
        output_dict_list.append((platform_name, rank_change, score_change, level_change, rank_score_origin, rank_score_new, score_origin, score_new, level_origin, level_new))
    output_dict_list.sort(key=lambda x:(-abs(x[1]),-abs(x[2]), -x[3], x[4]))
    for (platform_name, rank_change, score_change, level_change, rank_score_origin, rank_score_new, score_origin, score_new, level_origin, level_new) in output_dict_list:
        if platform_name in status_dict:
            status = status_dict[platform_name]
        else:
            status = 1
        _str = "\t".join([("%-" + str(platform_name_length_max + 3) + "s") % platform_name, str(rank_change), "%.4f" % score_change, str(level_change), str(rank_score_origin), str(rank_score_new), "%.4f" % score_origin, "%.4f" % score_new, level_origin, level_new, str(status)]) + "\n"
        output_str += _str

    #统计排名变化和得分变化绝对值前20的平台
    rank_score_dict_this = {}
    score_dict_this = {}
    level_dict_this = {}
    platform_name_list_this = []
    rank_score_dict_last = {}
    score_dict_last = {}
    level_dict_last = {}
    platform_name_list_last = []
    for date in [this_date, last_date]:
        stringSQL = "SELECT `platform_name`, `score`, `rank_score`, `level` FROM " + V + " WHERE `date` = '" + str(date) + "'"
        if date == this_date:
            _rank_score_dict = rank_score_dict_this
            _score_dict = score_dict_this
            _level_dict = level_dict_this
            _list = platform_name_list_this
        else:
            _rank_score_dict = rank_score_dict_last
            _score_dict = score_dict_last
            _level_dict = level_dict_last
            _list = platform_name_list_last
        _cur = cur_ddpt_data
        _cur.execute(stringSQL)
        rows = _cur.fetchall()
        for row in rows:
            platform_name = row[0]
            score = float(row[1])
            rank_score = int(row[2])
            level = row[3]
            _list.append(platform_name)
            _score_dict[platform_name] = score
            _level_dict[platform_name] = level
            _rank_score_dict[platform_name] = rank_score
    platform_name_list = list(set(platform_name_list_this) & set(platform_name_list_last))
    change_list = []
    for platform_name in platform_name_list:
        rank_score_last = rank_score_dict_last[platform_name]
        rank_score_this = rank_score_dict_this[platform_name]
        rank_change = rank_score_last - rank_score_this
        score_last = score_dict_last[platform_name]
        score_this = score_dict_this[platform_name]
        score_change = score_this - score_last
        level_last = level_dict_last[platform_name]
        level_this= level_dict_this[platform_name]
        level_change = LEVEL_LIST.index(level_last) - LEVEL_LIST.index(level_this)
        change_list.append((platform_name, rank_change, score_change, level_change, rank_score_last, rank_score_this, score_last, score_this, level_last, level_this))
    change_list.sort(key=lambda x:(-abs(x[1]),-abs(x[2]), -x[3], x[4]))
    rank_score_change_list = change_list[:_top_N]
    change_list.sort(key=lambda x:(-abs(x[2]),-abs(x[1]), -x[3], x[4]))
    score_change_list = change_list[:_top_N]
    change_list.sort(key=lambda x:(-abs(x[3]),-abs(x[1]), -x[2], x[4]))
    level_change_list = change_list[:_top_N]
    
    rank_score_change_str = "平台名称 排名变化 得分变化 等级变化 上周排名 本周排名 上周得分 本周得分 上周等级 本周等级 状态\n"
    score_change_str = "平台名称 排名变化 得分变化 等级变化 上周排名 本周排名 上周得分 本周得分 上周等级 本周等级 状态\n"
    level_change_str = "平台名称 排名变化 得分变化 等级变化 上周排名 本周排名 上周得分 本周得分 上周等级 本周等级 状态\n"
    count = 0
    for _list in [rank_score_change_list, score_change_list, level_change_list]:
        count += 1
        for (platform_name, rank_change, score_change, level_change, rank_score_last, rank_score_this, score_last, score_this, level_last, level_this) in _list:
            if platform_name in status_dict:
                status = status_dict[platform_name]
            else:
                status = 1
            _str = "\t".join([("%-" + str(platform_name_length_max + 3) + "s") % platform_name, str(rank_change), "%.4f" % score_change, str(level_change), str(rank_score_last), str(rank_score_this), "%.4f" % score_last, "%.4f" % score_this, level_last, level_this, str(status)]) + "\n"
            if count == 1:
                rank_score_change_str += _str
            elif count == 2:
                score_change_str += _str
            else:
                level_change_str += _str
    
    #统计每个等级下坏站的分布(均值和方差)
    #获得当前所有的坏站在数据库中的历史时间
    platform_name_dict_bad = {}
    stringSQL = "SELECT `platform_name`, `old_date` FROM " + V + " WHERE `date` = '" + str(this_date) + "' AND `status` < '0.89'"
    cur_ddpt_data.execute(stringSQL)
    rows = cur_ddpt_data.fetchall()
    for platform_name, old_date in rows:
        if old_date == None:
            old_date = this_date
        platform_name_dict_bad[platform_name] = old_date
    #获得历史上每个时间不同等级的个数
    level_rank_list_dict = {}
    stringSQL = "SELECT `date`, `level`, `rank_score` FROM " + V + " WHERE `old_date` IS NULL"
    cur_ddpt_data.execute(stringSQL)
    rows = cur_ddpt_data.fetchall()
    for date, level, rank_score in rows:
        if date not in level_rank_list_dict:
            level_rank_list_dict[date] = {}
        if level not in level_rank_list_dict[date]:
            level_rank_list_dict[date][level] = []
        level_rank_list_dict[date][level].append(rank_score)
    for date in level_rank_list_dict:
        for level in level_rank_list_dict[date]:
            level_rank_list_dict[date][level].sort()
    #获得每个坏站在历史时刻的所在等级的排名百分比 
    level_dict_bad = {}
    for level in LEVEL_LIST:
        level_dict_bad[level] = []
    for platform_name in platform_name_dict_bad:
        old_date = platform_name_dict_bad[platform_name]
        stringSQL = "SELECT `level`, `rank_score` FROM " + V + " WHERE `platform_name` = '" + platform_name + "' AND `date` = '" + str(old_date) + "'"
        cur_ddpt_data.execute(stringSQL)
        rows = cur_ddpt_data.fetchall()
        for level, rank_score in rows:
            rank_relative = float(level_rank_list_dict[old_date][level].index(rank_score) + 1) / len(level_rank_list_dict[old_date][level])
            level_dict_bad[level] .append(rank_relative)
    level_dict_str_dict = {}.fromkeys(LEVEL_LIST, "")
    for level in LEVEL_LIST:
        if len(level_dict_bad[level]) == 0:
            level_dict_str_dict[level] += "None None"
        else:
            ave, stdev, max_rank, min_rank = calculateDistFromList(level_dict_bad[level])
            level_dict_str_dict[level] += "%.2f" % (ave * 100) + "% " + "%.2f" % (stdev * 100)+ "% " + "%.2f" % (max_rank * 100)+ "% " + "%.2f" % (min_rank * 100)+ "%"
            
    #统计经过不同策略之后各个等级的百分比(分补充和不补充)
    level_dict_V_supply = {}
    level_dict_V_not_supply = {}
    level_ratio_supply = {}
    level_ratio_not_supply = {}
    field_level_list = ["level", "level_initial", "level_after_punishment", "level_after_smooth", "level_after_degrade", "level_lock"]
    field_list_number = len(field_level_list)
    
    for field in field_level_list:
        level_dict_V_supply[field] = {}
        level_dict_V_not_supply[field] = {}
        level_ratio_supply[field] = ""
        level_ratio_not_supply[field] = ""
        for level in LEVEL_LIST:
            level_dict_V_supply[field][level] = 0
            level_dict_V_not_supply[field][level] = 0
    stringSQL = "SELECT `" + "`, `".join(field_level_list) + "` FROM " + V + " WHERE `date` = '" + str(this_date) + "'"
    platform_number_supply = cur_ddpt_data.execute(stringSQL)
    for rets in cur_ddpt_data.fetchall():
        for i in range(field_list_number):
            level_dict_V_supply[field_level_list[i]][rets[i]] += 1
    for field in field_level_list:
        count = 0
        for level in LEVEL_LIST:
            level_ratio_supply[field] += level + ": " + str(level_dict_V_supply[field][level]) + ", " + "%.2f" % (100 * float(level_dict_V_supply[field][level]) / platform_number_supply) + "%; "      
            count += float(level_dict_V_supply[field][level]) / platform_number_supply
        assert (count - 1) < 0.01
        
    stringSQL = "SELECT `" + "`, `".join(field_level_list) + "` FROM " + V + " WHERE `date` = '" + str(this_date) + "' AND `old_date` IS NULL"
    platform_number_not_supply = cur_ddpt_data.execute(stringSQL)
    for rets in cur_ddpt_data.fetchall():
        for i in range(field_list_number):
            level_dict_V_not_supply[field_level_list[i]][rets[i]] += 1
    for field in field_level_list:
        count = 0
        for level in LEVEL_LIST:
            level_ratio_not_supply[field] += level + ": " + str(level_dict_V_not_supply[field][level]) + ", " + "%.2f" % (100 * float(level_dict_V_not_supply[field][level]) / platform_number_not_supply) + "%; "      
            count += float(level_dict_V_not_supply[field][level]) / platform_number_not_supply
        assert (count - 1) < 0.01
    
    #插入数据
    if _insertSQL:
        field_list = LEVEL_LIST + ["execute_date", "database_date", "summary", "deviation", "strategy", "rank_change_good", "rank_change_bad", "level_change_good", "level_change_bad", "output_file"]
        value_list = [str(level_ratio_str_dict[level]) for level in LEVEL_LIST] + [str(date_now), str(this_date), str(_summary), "%.6f" % deviation, str(_strategy), str(rank_change_number_good), str(rank_change_number_bad), str(level_change_number_good), str(level_change_number_bad), output_str]
        for level in LEVEL_LIST:
            field_list += [level + "_dist"]
            value_list += [level_dict_str_dict[level]]
        field_list += ["rank_change_top20", "score_change_top20", "level_change_top20"]
        value_list += [rank_score_change_str, score_change_str, level_change_str]
        for field in field_level_list:
            field_list += [field + "_supply_ratio"]
            field_list += [field + "_not_supply_ratio"]
            value_list += [level_ratio_supply[field]]
            value_list += [level_ratio_not_supply[field]]
        stringSQL = "INSERT INTO " + Strategy_list + "(`" + "`,`".join(field_list) + "`) VALUES('" + "','".join(value_list) + "')"
        cur_ddpt_test.execute(stringSQL)
        conn_ddpt_test.commit()
    closeCursors(cur_ddpt_test, cur_ddpt_data, cur_db)
    closeConns(conn_ddpt_test, conn_ddpt_data, conn_db)
    
    return level_ratio_dict, deviation
  
if __name__ == '__main__':
    summary = "origin"
    if (len(sys.argv) != 1):
        summary = str(sys.argv[1])
    computeATBDeviation(_last_weeks = 8, _strategy = "", _summary = summary, _top_N = 20, _insertSQL = True)
    