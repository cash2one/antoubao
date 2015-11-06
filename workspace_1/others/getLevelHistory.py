# /usr/bin/python
# coding=utf8

from mysqlTools import *
import time
from header import *
from math import floor
# FROM meliae import scanner,loader

if __name__ == '__main__':
    startTime = time.time()
    # 初始条件设置
    level_dict = {"levelaplusplus":"A++", "levelaplus":"A+", "levela":"A", "levelbplusplus":"B++", "levelbplus":"B+", "levelb":"B", "levelc":"C"}
    level_order = ["levelaplusplus", "levelaplus", "levela", "levelbplusplus", "levelbplus", "levelb", "levelc"]
    level_score = {"A++":7, "A+":6, "A":5, "B++":4, "B+":3, "B":2, "C":1}     

    level_number = len(level_dict)
    SRCDB = "platform_score_T"
    DSTDB = "platform_score_T"
    
    conn = getConn(DEVHOST, USERNAME, PASSWORD, DB, PORT)
    cur = getCursors(conn)
    initializeCursors(cur)
    
    # 获得时间列表，最近的时间点在前
    date_list = []
    stringSQL = "SELECT DISTINCT date FROM " + SRCDB + " ORDER BY date DESC"
    cur.execute(stringSQL)
    rets = cur.fetchall()
    for ret in rets:
        date_list.append(ret[0])
    start_date = date_list[-1]   
    date_number = len(date_list)
    
    # 获得所有平台和level的score信息并组装
    platform_score_dict = {}
    lever_score_dict = {}       
    stringSQL = "SELECT platform_name, date, score FROM " + SRCDB
    cur.execute(stringSQL)
    DB_info = cur.fetchall()
    DB_info_number = len(DB_info)
    for platform_name, date, score in DB_info:
        if platform_name in level_dict:
            if platform_name not in lever_score_dict:
                lever_score_dict[platform_name] = {}
                for date_temp in date_list:
                    lever_score_dict[platform_name][date_temp] = {}
                    lever_score_dict[platform_name][date_temp]["score"] = MINPLATFORMSCORE
            lever_score_dict[platform_name][date]["score"] = score
        else:
            if platform_name not in platform_score_dict:
                platform_score_dict[platform_name] = {}                
                for date_temp in date_list:
                    platform_score_dict[platform_name][date_temp] = {}
                    platform_score_dict[platform_name][date_temp]["score"] = MINPLATFORMSCORE
                    platform_score_dict[platform_name][date_temp]["level"] = "-"
            platform_score_dict[platform_name][date]["score"] = score
    
    platform_number = len(platform_score_dict)
    
    # 获得一个时间节点上不同分级的分段区间
    score_dict = {}
    for date in date_list:
        score_dict[date] = {}
        for i in range(0, level_number):
            level = level_order[i]
            score_dict[date][level] = {}
            score_dict[date][level]["min"] = MINPLATFORMSCORE + 1
            score_dict[date][level]["max"] = MAXPLATFORMSCORE
            if i == 0:
                score_dict[date][level]["min"] = lever_score_dict[level][date]["score"]
            else:
                if i == level_number - 1:
                    score_dict[date][level]["max"] = lever_score_dict[level_order[i - 1]][date]["score"]
                else:
                    score_dict[date][level]["min"] = lever_score_dict[level][date]["score"]
                    score_dict[date][level]["max"] = lever_score_dict[level_order[i - 1]][date]["score"]
    # 获得每个平台的最大时间
    date_max_list = {}
    for platform_name in platform_score_dict:
        date_max_list[platform_name] = start_date
        for date in date_list: 
            if platform_score_dict[platform_name][date]["score"] != MINPLATFORMSCORE:
                date_max_list[platform_name] = max(date_max_list[platform_name], date)
    # 判断平台在不同时间节点上的评级并记录到T表内
    PercentList = [floor(float(x) * platform_number / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)] 
    counter = 0
    for platform_name in platform_score_dict:
        counter += 1
        if counter in PercentList:
            print "updating: " + str((1 + PercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
        score_str = ["-"] * date_number
        for i in range(0, date_number):
            date = date_list[i]
            score = platform_score_dict[platform_name][date]["score"]
            for level in level_order:
                if score_dict[date][level]["min"] <= score < score_dict[date][level]["max"]:
                    platform_score_dict[platform_name][date]["level"] = level_dict[level]
                    score_str[i] = level_dict[level]
                    break
        change_str = ["-"] * (date_number - 1)
        for i in range(0, date_number - 1):
            if score_str[i] != "-" and score_str[i + 1] != "-":
                change_str[i] = str(level_score[score_str[i]] - level_score[score_str[i + 1]])
        score_str = "#".join(score_str)
        change_str = "#".join(change_str)         
        stringSQL = "UPDATE " + DSTDB + " SET `level_history` = '" + score_str + "', `level_change` = '" + change_str + "' WHERE `platform_name` = '" + platform_name + "' AND `date` = " + str(date_max_list[platform_name]) + ""
        cur.execute(stringSQL)
        conn.commit() 

    # 收尾工作        
    closeCursors(cur)
    closeConns(conn)  
    endTime = time.time()
    print "The whole reset program costs " + str(endTime - startTime) + " seconds."
    
