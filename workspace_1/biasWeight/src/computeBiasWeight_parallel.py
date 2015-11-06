# /usr/bin/python
# coding=utf8
#1.从y表中获得所有坏站（0、0.3、0.6）的name和坏站时间，同时筛选出在坏站前2至5共4周有数据的坏站集合X
#2.以X这些坏站的出事时间的中位数来作为好站的时间T
#3.计算不同时间段的不同等级的score
#4.筛选出在T至T-3共4周内有数据且周平均水平在A以及A以上的好站Y
#5.根据好站和坏站的比例从Y中来筛选四周平均score较前的好站Z
#6.X和Z作为我们的最终的贝叶斯方法的训练集
#7.获得计算分值的40个属性并赋予相应的初始权重
#8.得到每个平台在相应时间的所有属性的实际值（四周加权平均）
#9.构造每个级别的区间矩阵
#10.遍历所有的weight贝叶斯计算
#11.记录数据、画图

from atbtools.header import *
from atbtools.computeTools import *
from atbtools.mysqlTools import *
import time
import copy
import math
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import sys
from multiprocessing import Process, Manager

def computeQIndex(_weight_value_order_list1,range_temp):
    _Q_sum = 0
    for j in range_temp:
        _weight_value_order_list_temp = copy.deepcopy(_weight_value_order_list1)
        for k in range(weight_index_number):
            _weight_value_order_list_temp[weight_index[k]] = iteration_weight_list[(j / iteration_weight_number ** (weight_index_number -k - 1)) % iteration_weight_number]
        score={}
        for platform in platform_dict:
            score[platform] = getVectorInnerProduct(value_dict[platform], _weight_value_order_list_temp)
        grade_hold_number={}.fromkeys(status_list_final, 0)
        platform_score_list = sortDictByValue(score)[0] #按照得分从大到小排列
        for k in range(0,platform_number):                
            status_old = platform_dict[platform_score_list[k]]["status"]
            if status_block_dict[status_old]["min"] <= k <= status_block_dict[status_old]["max"]:
                grade_hold_number[status_old] += 1
        Q_index = getVirtualIndex(grade_hold_number, status_number_dict)
        for k in range(weight_index_number):
            new_weight_index[k] += _weight_value_order_list_temp[weight_index[k]] * Q_index
        _Q_sum += Q_index
    Q_sum_list[p] += _Q_sum

if __name__ == '__main__':
    startTime = time.time()
    conn_dev = getConn(DEVHOST, USERNAME, PASSWORD, DB, PORT)
    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_dev = getCursors(conn_dev)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_dev, cur_db)
    SRCDB_T = "platform_score_T"   
    SRCDB_Y = "total_status.py"   
    SRCDB_E3 = "platform_quantitative_data_E3"  
    
    #0.从y表中获得所有坏站（status < 1）的name和坏站时间，同时筛选出在坏站前2至5共4周有数据的坏站集合X    bad_status_list = [0, 0.3, 0.6]
    stringSQL = "SELECT DISTINCT platform_name , min(date), min(status) FROM " + SRCDB_Y
    stringSQL = stringSQL + " WHERE `status` < '1' GROUP BY platform_name"
    bad_platform_dict_number = cur_db.execute(stringSQL)
    rets = cur_db.fetchall()
    bad_platform_list=[]
    for platform_name, _date, status in rets:
        bad_platform_list.append(str(platform_name))
    print "Y表内一共有" + str(bad_platform_dict_number) + "个坏站."
    print 
    
    #1.从y表中获得所有坏站["<0.3", "=0.3", "=0.6", "=0.7"]的name和坏站时间，同时筛选出在坏站前2至5共4周有数据的坏站集合X
    bad_status_list = ["<0.3", "=0.3", "=0.6", "=0.7"]
    status_order_dict = {"<0.3":0, "=0.3":1, "=0.6":2, "=0.7":3, "=1":4} #value越大，排名越靠前
    status_number_dict = {}
    status_platform_dict = {}
    bad_platform_dict = {}
    bad_platform_list_all = []
    stringSQL = "SELECT DISTINCT platform_name , min(date) FROM " + SRCDB_Y
    stringSQL = stringSQL + " WHERE (status_str_replace) GROUP BY platform_name "
    status_str = ""
    for i in range(len(bad_status_list)):
        status = bad_status_list[i]
        status_number_dict[status] = {}
        status_number_dict[status]["number"] = 0
        status_number_dict[status]["order"] = status_order_dict[status]
        status_platform_dict[status] = []
        if status.startswith("<"):
            _status = float(status[1:])
            status_str = "`status`" + " < '" + str(_status - 0.001) + "'"
        elif status.startswith("="):
            _status = float(status[1:])
            status_str = "`status`" + " > '" + str(_status - 0.001) + "' AND `status`" + " < '" + str(_status + 0.099) + "'"
        elif status.startswith(">"):
            _status = float(status[1:])
            status_str = "`status`" + " > '" + str(_status + 0.001) + "'"
        _stringSQL = stringSQL.replace("status_str_replace", status_str)
        ret = cur_db.execute(_stringSQL)
        if ret != 0:
            for platform_name, _date in cur_db.fetchall():
                platform_name = str(platform_name)
                if platform_name in bad_platform_list_all: #有些坏站可能有多个坏点，只取status最小的时间点
                    continue
                date_end = getDateTimestamp(int(_date)) - (SHIFTWEEKS_BIAS - 1) * SECONDSPERWEEK #本身就是前一周的数据
                date_start =  date_end - (LASTWEEKS_BIAS - 1) * SECONDSPERWEEK
                _stringSQL = "SELECT * FROM " + SRCDB_E3 + " WHERE `date` <= " + str(date_end) + " AND `date`  >= " + str(date_start) + " AND `platform_name` = '" + platform_name + "'"
                ret = cur_dev.execute(_stringSQL)
                if ret != 0:
                    status_number_dict[status]["number"] += 1
                    status_platform_dict[status].append(platform_name)
                    bad_platform_list_all.append(platform_name)
                    bad_platform_dict[platform_name] = {}
                    bad_platform_dict[platform_name]["status"] = status
                    bad_platform_dict[platform_name]["date"] = date_end
    bad_platform_number = len(bad_platform_dict)
    #2.计算不同时间段的不同等级的score
    #2.0.选择在3月份第2周(1426348800)到4月份第1周(1428163200)这四周有数据的好站。
    date_start = 1426348800
    date_end= 1428163200
    date_list = range(date_start, date_end + 1, SECONDSPERWEEK)
    date_number = len(date_list)
    #2.1 获得所有等级1平台在计算节点4周内的等级平均分大于限定levela的平台(自A++到C依次为6、5、4、3、2、1、0分)
    level_dict = {"levelaplusplus":"A++", "levelaplus":"A+", "levela":"A", "levelbplusplus":"B++", "levelbplus":"B+", "levelb":"B", "levelc":"C"}
    level_order = ["levelaplusplus", "levelaplus", "levela", "levelbplusplus", "levelbplus", "levelb", "levelc"]
    level_score = {"levelaplusplus": 7, "levelaplus":6, "levela":5, "levelbplusplus":4, "levelbplus":3, "levelb":2, "levelc":1}     
    level_number = len(level_dict)
    #2.2 获得所有等级为1的平台信息以及评级打分信息
    good_platform_initial_dict = {}
    lever_score_dict = {}
    stringSQL = "SELECT platform_name, date, score FROM " + SRCDB_T + " WHERE `date` <= " + str(date_end) + " AND `date`  >= " + str(date_start) + " AND `status` = 1 "
    cur_dev.execute(stringSQL)
    rets = cur_dev.fetchall()    
    for platform_name, date, score in rets:
        if platform_name in bad_platform_list:
            continue
        if platform_name in level_dict:
            if platform_name not in lever_score_dict:
                lever_score_dict[platform_name] = {}
                for date_temp in date_list:
                    lever_score_dict[platform_name][date_temp] = {}
                    lever_score_dict[platform_name][date_temp]["score"] = MINPLATFORMSCORE
            lever_score_dict[platform_name][date]["score"] = score
        else:
            if platform_name not in good_platform_initial_dict:
                good_platform_initial_dict[platform_name] = {}                
                good_platform_initial_dict[platform_name]["score"] = []
                for date_temp in date_list:
                    good_platform_initial_dict[platform_name][date_temp] = {}
                    good_platform_initial_dict[platform_name][date_temp]["score"] = MINPLATFORMSCORE
                    good_platform_initial_dict[platform_name][date_temp]["level"] = 0  # level化简为分数
            good_platform_initial_dict[platform_name][date]["score"] = score
            good_platform_initial_dict[platform_name]["score"].append(score)
    good_platform_initial_number = len(good_platform_initial_dict)
    #2.3 获得一个时间节点上不同分级的分段区间
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
            elif i == level_number - 1:
                score_dict[date][level]["max"] = lever_score_dict[level_order[i - 1]][date]["score"]
            else:
                score_dict[date][level]["min"] = lever_score_dict[level][date]["score"]
                score_dict[date][level]["max"] = lever_score_dict[level_order[i - 1]][date]["score"]
     
    #3.筛选出在T至T-3共4周内有数据且周平均水平在A以及A以上的好站Y
    good_platform_dict = {}
    for platform_name in good_platform_initial_dict:
        score_str = []
        _number = 0
        _sum = 0
        for i in range(0, date_number):
            date = date_list[i]
            score = good_platform_initial_dict[platform_name][date]["score"]
            for level in level_order:
                if score_dict[date][level]["min"] <= score < score_dict[date][level]["max"]:
                    good_platform_initial_dict[platform_name][date]["level"] = level_score[level]
                    score_str.append(level_score[level])
                    _number += 1
                    _sum += level_score[level]
                    break
        level_future4weeks_ave = float(_sum) / _number        
        if level_future4weeks_ave >= level_score[LIMITEDLEVELFORBIAS]:
            _stringSQL = "SELECT * FROM " + SRCDB_E3 + " WHERE `date` <= " + str(date_end) + " AND `date`  >= " + str(date_start) + " AND `platform_name` = '" + platform_name + "'"
            ret = cur_dev.execute(_stringSQL)
            if ret != 0:
                good_platform_dict[platform_name] = {}
                good_platform_dict[platform_name]["status"] = "=1"
                good_platform_dict[platform_name]["date"] = date_end
                _sum = sum(good_platform_initial_dict[platform_name]["score"])
                _number = len(good_platform_initial_dict[platform_name]["score"])
                good_platform_dict[platform_name]["score_ave"] = _sum / _number
    good_platform_number = len(good_platform_dict)
    status_number_dict["=1"] = {}
    status_number_dict["=1"]["number"] = good_platform_number
    status_number_dict["=1"]["order"] = status_order_dict["=1"]
    status_list = bad_status_list + ["=1"]
    print "起初一共有" + str(bad_platform_number) + "个坏站和" + str(good_platform_number) + "个平均等级在A以上的好站." 
    print "在坏站提前" + str(SHIFTWEEKS_BIAS) + "周和好站固定四周的条件下, 各个status有数据的坏站个数为："
    for status in status_list:
        print status + ": " + str(status_number_dict[status]["number"])
    print
    #4.删除等级个数过小的
    status_list_final = []    
    for status in bad_status_list:
        if status_number_dict[status]["number"] < MINPLATFORMSNUMBER_BIAS:
            print "'" + status + "'的个数小于临界值'" + str(MINPLATFORMSNUMBER_BIAS) + "'，删除."
            for platform_name in status_platform_dict[status]:
                print platform_name
                del bad_platform_dict[platform_name]
            del status_number_dict[status]
        else:
            status_list_final.append(status)
    status_list_final.append("=1")
    bad_platform_number = len(bad_platform_dict)
    #5.根据好站和坏站的比例来筛选得分较前的好站Z, X和Z作为我们的最终的贝叶斯方法的训练集
    if good_platform_number <= bad_platform_number * RATEGOODBAD:
        good_platform_final_dict = good_platform_dict
    else:
        good_platform_number = bad_platform_number * RATEGOODBAD
        (platform_final_list,score_final_list) = sortDictByKeyValue(good_platform_dict,"score_ave")
        good_platform_final_dict = {}
        for platform_name in platform_final_list[0:good_platform_number]:
            platform_name = str(platform_name)
            good_platform_final_dict[platform_name] = {}
            good_platform_final_dict[platform_name]["status"] = 1
            good_platform_final_dict[platform_name]["date"] = date_end
            
    platform_dict=dict(bad_platform_dict, **good_platform_final_dict)
    print "再考虑到好站个数尽量大于坏站个数的" + str(RATEGOODBAD) + "倍, 各个status有数据的坏站个数为: "
    for status in status_list_final:
        print status + ": " + str(status_number_dict[status]["number"])
    platform_number = len(platform_dict)
    print "一共有" + str(platform_number) + "个站."
    print
 
    #7.获得计算分值的40个属性并赋予相应的初始权重
    del_list = ["id", "platform_id", "platform_name", "provision_of_risk_num", "date", "ave_annualized_return", "weekly_ave_investment_per_bid", "top5_ratio_investment", "top10_ratio_investment"]
    merge_list = ["registered_cap","weekly_lending"] #####
    index_list = getAllColumnsFromTable(cur_dev, SRCDB_E3, del_list, merge_list) #####
    weight_dict = {}.fromkeys(index_list, get1DZeroArray(0))
    weight_number = len(weight_dict)
    print "一共有" + str(weight_number) + "指标."
    #获得所有指标的已知默认权重
#     total_grade_list = {}
#     total_grade_list["Capital_adequacy_ratio"] = 0.117
#     total_grade_list["Activeness_credibility"] = 0.223
#     total_grade_list["Distribution"] = 0.152
#     total_grade_list["Mobility"] = 0.269
#     total_grade_list["Security"] = 0.071
#     total_grade_list["Pellucidity"] = 0.092
#     total_grade_list["Growth"] = 0.076
#     checkGradeIndex(total_grade_list,0)
#     total_grade_number = len(total_grade_list)
#     print "共有 " + str(total_grade_number) + "个总指标"
#     first_grade_list={}
#     first_grade_list["registered_cap"] = ["Capital_adequacy_ratio", 0.15]
#     first_grade_list["vc_cap_usd"] = ["Capital_adequacy_ratio", 0.40]
#     first_grade_list["turnover_registered"] = ["Capital_adequacy_ratio", 0.45]
#     first_grade_list["investor"] = ["Activeness_credibility", 0.35]
#     first_grade_list["turnover"] = ["Activeness_credibility", 0.0875]
#     first_grade_list["turnover_period"] = ["Activeness_credibility", 0.2625]
#     first_grade_list["ave_turnover"] = ["Activeness_credibility", 0.105]
#     first_grade_list["bidding_activeness"] = ["Activeness_credibility", 0.081]
#     first_grade_list["investor_HHI"] = ["Activeness_credibility", 0]
#     first_grade_list["weekly_ratio_new_old"] = ["Activeness_credibility", 0.114]
#     first_grade_list["ave_lending_per_borrower"] = ["Distribution", 0.3]
#     first_grade_list["borrower"] = ["Distribution", 0.3]
#     first_grade_list["borrow_concentration"] = ["Distribution", 0.4]
#     first_grade_list["not_returned_yet"] = ["Mobility", 0.35]
#     first_grade_list["loan_period"] = ["Mobility", 0.05]
#     first_grade_list["outstanding_loan"] = ["Mobility", 0.1]
#     first_grade_list["short_term_debt_ratio"] = ["Mobility", 0.25]
#     first_grade_list["cash_flow_in"] = ["Mobility", 0.15]
#     first_grade_list["provision_of_risk"] = ["Mobility", 0.1] 
#     first_grade_list["compensation"] = ["Security", 0.2]  
#     first_grade_list["technical_index"] = ["Security", 0.25]
#     first_grade_list["third_entrust"] = ["Security", 0.3]  
#     first_grade_list["third_assurance"] = ["Security", 0.15]  
#     first_grade_list["real_name"] = ["Security", 0.05]  
#     first_grade_list["debt_transfer"] = ["Security", 0.05]  
#     first_grade_list["financial_transparency"] = ["Pellucidity", 0.2]  
#     first_grade_list["overdue_transparency"] = ["Pellucidity", 0.25]  
#     first_grade_list["borrower_transparency"] = ["Pellucidity", 0.25]  
#     first_grade_list["PR_transparency"] = ["Pellucidity", 0.2]  
#     first_grade_list["customer_service"] = ["Pellucidity", 0.1]  
#     first_grade_list["money_growth"] = ["Growth", 0.3]  
#     first_grade_list["client_growth"] = ["Growth", 0.4]
#     first_grade_list["market_share_growth"] = ["Growth", 0.3]
#     checkGradeIndex(first_grade_list,1)
#     first_grade_number = len(first_grade_list)
#     print "共有" + str(first_grade_number) + "个一极指标"
#     second_grade_list={}
#     second_grade_list["registered_cap"] = ["registered_cap", 1, 23]
#     second_grade_list["vc_cap_usd"] = ["vc_cap_usd", 1, 24]
#     second_grade_list["turnover_registered"] = ["turnover_registered", 1, 25]
#     second_grade_list["weekly_new_investor"] = ["investor", 0.3, 4]
#     second_grade_list["weekly_total_investor"] = ["investor", 0.7, 2]
#     second_grade_list["weekly_lending"] = ["turnover", 1, 1]
#     second_grade_list["turnover_period"] = ["turnover_period", 1, 12]
#     second_grade_list["weekly_ave_investment"] = ["ave_turnover", 0.7, 6]
#     second_grade_list["weekly_ave_investment_old"] = ["ave_turnover", 0.3, 7]
#     second_grade_list["weekly_ave_bid_close_time"] = ["bidding_activeness", 1, 8]
#     second_grade_list["weekly_ratio_new_old"] = ["weekly_ratio_new_old", 1, 11]
#     second_grade_list["investor_HHI"] = ["investor_HHI", 1, 15]
#     second_grade_list["weekly_ave_lending_per_borrower"] = ["ave_lending_per_borrower", 0.8, 9]
#     second_grade_list["weekly_ave_lending_per_bid"] = ["ave_lending_per_borrower", 0.2, 10]
#     second_grade_list["weekly_total_borrower"] = ["borrower", 1, 3]
#     second_grade_list["top10_ratio_loan"] = ["borrow_concentration", 0.45, 13]
#     second_grade_list["top5_ratio_loan"] = ["borrow_concentration", 0.45, 14]
#     second_grade_list["borrower_HHI"] = ["borrow_concentration", 0.1, 16]
#     second_grade_list["not_returned_yet"] = ["not_returned_yet", 1, 18]
#     second_grade_list["weekly_loan_period"] = ["loan_period", 1, 5]
#     second_grade_list["outstanding_loan"] = ["outstanding_loan", 1, 17]
#     second_grade_list["short_term_debt_ratio"] = ["short_term_debt_ratio", 1, 40] #新加指标的位置
#     second_grade_list["cash_flow_in"] = ["cash_flow_in", 1, 39]
#     second_grade_list["provision_of_risk"] = ["provision_of_risk", 1, 26]
#     second_grade_list["compensation"] = ["compensation", 1, 27]
#     second_grade_list["technical_security"] = ["technical_index", 1, 29]
#     second_grade_list["third_entrust"] = ["third_entrust", 1, 28]
#     second_grade_list["third_assurance"] = ["third_assurance", 1, 30]
#     second_grade_list["real_name"] = ["real_name", 1, 36]
#     second_grade_list["debt_transfer"] = ["debt_transfer", 1, 37]
#     second_grade_list["financial_transparency"] = ["financial_transparency", 1, 31]
#     second_grade_list["overdue_transparency"] = ["overdue_transparency", 1, 32]
#     second_grade_list["borrower_transparency"] = ["borrower_transparency", 1, 33]
#     second_grade_list["PR_transparency1"] = ["PR_transparency", 0.9, 34]
#     second_grade_list["PR_transparency2"] = ["PR_transparency", 0.1, 35]
#     second_grade_list["customer_service"] = ["customer_service", 1, 38]
#     second_grade_list["money_growth"] = ["money_growth", 1, 19]
#     second_grade_list["borrower_growth"] = ["client_growth", 0.5, 20]
#     second_grade_list["investor_growth"] = ["client_growth", 0.5, 21]
#     second_grade_list["market_share_growth"] = ["market_share_growth", 1, 22]
#     checkGradeIndex(second_grade_list,1)
#     second_grade_number = len(second_grade_list)
#     print "共有" + str(second_grade_number) + "个二极指标"
#     if second_grade_number != weight_number:
#         print "二级指标个数与已知指标个数不符，请重新检查指标权重设置."
#         exit(1)
#     print 

    total_grade_list = {}
    total_grade_list["Capital_adequacy_ratio"] = 0.4
    total_grade_list["Activeness_credibility"] = 0.6
    checkGradeIndex(total_grade_list,0)
    total_grade_number = len(total_grade_list)
    print "共有 " + str(total_grade_number) + "个总指标"
    first_grade_list={}
    first_grade_list["registered_cap"] = ["Capital_adequacy_ratio", 1]
    first_grade_list["turnover"] = ["Activeness_credibility", 1]
    checkGradeIndex(first_grade_list,1)
    first_grade_number = len(first_grade_list)
    print "共有" + str(first_grade_number) + "个一极指标"
    second_grade_list={}
    second_grade_list["registered_cap"] = ["registered_cap", 1, 23]
    second_grade_list["weekly_lending"] = ["turnover", 1, 1]
    checkGradeIndex(second_grade_list,1)
    second_grade_number = len(second_grade_list)
    print "共有" + str(second_grade_number) + "个二极指标"
    if second_grade_number != weight_number:
        print "二级指标个数与已知指标个数不符，请重新检查指标权重设置."
        exit(1)
    print 
    weight_dict = assembledGrade(total_grade_list,first_grade_list,second_grade_list,weight_dict)
     
    # 按照权重大小将weight_dict的key和value排序
    weight_key_order_list = list(reversed(sortDictByValue(second_grade_list,2)[0])) #按初始权重从大到小排列
    weight_value_order_list = [weight_dict[x] for x in weight_key_order_list]
    print "指标按照优先级从大到小排列顺序以及对应的初始权重为: "
    for i in range(second_grade_number):
        print weight_key_order_list[i] + ": " + str(weight_value_order_list[i])
    print  
    #8. 得到每个平台在相应时间的所有属性的实际值（四周加权平均）
    value_dict={}
    for platform_name in platform_dict:
        value_dict[platform_name]=[]
        date_end = platform_dict[platform_name]["date"]
        date_start = date_end - (LASTWEEKS_BIAS - 1) * SECONDSPERWEEK
        stringSQL = "SELECT " + ','.join(weight_key_order_list) + " FROM " + SRCDB_E3 + " WHERE `date` <= " + str(date_end) + " AND `date`  >= " + str(date_start) + " AND `platform_name` = '" + platform_name + "'" + " ORDER BY date DESC"
        ret_number = cur_dev.execute(stringSQL)
        rets = cur_dev.fetchall()
        for i in range(0,weight_number):
            index = []
            for j in range(0,ret_number):
                index.append(rets[j][i])
            ave_index = getWeightedMean(index)  #计算四周内的加权平均  
            value_dict[platform_name].append(ave_index)
 
    #9.构造每个级别的区间矩阵
    status_block_dict={}
    status_sum = 0
    for status in sortDictByKeyValue(status_number_dict, "order")[0]:
        status_block_dict[status]={}
        status_block_dict[status]["min"] = status_sum - RANKFLOATING
        status_block_dict[status]["max"] = status_sum + status_number_dict[status]["number"] -1 + RANKFLOATING
        status_sum += status_number_dict[status]["number"]
    status_number_dict = {status:status_number_dict[status]["number"] for status in status_number_dict}
    print "在允许排名浮动为'"+ str(RANKFLOATING) +"'的情况下，每个等级的排名区间为(排名从0开始)" 
    for status in status_list_final:
        print status + ": min = " + str(status_block_dict[status]["min"]) + ", max = " + str(status_block_dict[status]["max"])
    print
    # 赋予每个属性初始权重，作为下面计算的初始值。
    iteration_weight_list = [x * 0.05 for x in range(1, 10 * 2 / weight_number + 1, 1)]
    iteration_weight_number = len(iteration_weight_list)
    print "每个指标的迭代空间为: "
    print iteration_weight_list
    print 
    # 求最优权重策略1：每四个一组按照出现指数Q来确定贝叶斯权重
    block_number = weight_number / BLOCKCONTAINS
    block_reminder = weight_number % BLOCKCONTAINS
    parallel_number = BLOCKCONTAINS
    weight_value_order_list1 = copy.deepcopy(weight_value_order_list)
    #分组循环
    for i in range(block_number + 1):
        print "正在进行第" + str(i+1) + "/" + str(block_number) + "组计算。"
        sys.stdout.flush()
        if i == block_number:
            weight_index = range(BLOCKCONTAINS * i,weight_number)
        else:
            weight_index = range(BLOCKCONTAINS * i,BLOCKCONTAINS * (i + 1))
        weight_index_number = len(weight_index)
        if weight_index_number == 0:
            continue
        #组内循环
        iteration_number = iteration_weight_number ** weight_index_number
        Q_sum = 0
        #开始并行
        parallel_per_number = iteration_number / parallel_number
        parallel_reminder = iteration_number % parallel_number
        start = 0
        end = 0
        pool_list = [0] * parallel_number
        Q_sum_list = Manager().list([0] * parallel_number)
        new_weight_index = Manager().list([0] * parallel_number)
        for p in range(parallel_number):
            end = start + parallel_per_number
            if parallel_reminder > 0:
                end += 1
                parallel_reminder -= 1
            range_temp = range(start,end)
            start = end
            if len(range_temp) == 0:
                continue
            pool_list[p] = Process(target=computeQIndex,args = (weight_value_order_list1, range_temp))
            pool_list[p].start()
        for p in range(parallel_number):
            try:
                pool_list[p].join()
            except:
                continue
        Q_sum = sum(Q_sum_list)
        for k in range(weight_index_number):
            if Q_sum == 0:
                weight_value_order_list1[weight_index[k]] = 0
            else:
                weight_value_order_list1[weight_index[k]] = new_weight_index[k] / Q_sum
        file_name = "weight_" + str(i+1) + "_" + str(block_number) + ".txt"
        fp = open(file_name, 'w')
        for weight_final in weight_value_order_list1:
            fp.write("%.6f" % weight_final + " \n")
        fp.close()
    weight_value_order_list1 = getNormalization(weight_value_order_list1)
    print weight_value_order_list1
    file_name = "weight_" + str(RANKFLOATING) + "_parallel.txt"
    fp = open(file_name, 'w')
    for weight_final in weight_value_order_list1:
        fp.write("%.6f" % weight_final + " \n")
    fp.close()
     
    plt.plot(np.array(range(weight_number)), weight_value_order_list, 'o', ms=8, label = "Origin")
    plt.plot(np.array(range(weight_number)), weight_value_order_list1, 's', ms=8, label = "Bayes")
    matplotlib.rcParams["font.size"] = 20 #修改画图的默认值
    plt.xlabel("Index")
    plt.ylabel("Weight")
    plt.xlim(-0.5,weight_number+0.5)
    #plt.ylim(min(correct_proportion_min_list)-0.1,max(correct_proportion_max_list)+0.1)
    plt.xticks(range(0,weight_number+1,5))
    #plt.yticks(fontsize = 20)
    _title = "Index .vs. Weight (floating = " + str(RANKFLOATING) + " )"
    plt.title(_title, fontsize = 20)
    plt.legend(loc='lower right', numpoints = 1, scatterpoints = 1, fontsize = 15)  
    picture_name = "weight_" + str(RANKFLOATING) + "_parallel.jpg"
    plt.savefig(picture_name)    
    
    print ""
    print "finished"
    endTime = time.time()
    print "The whole program costs " + str(endTime - startTime) + " seconds."
    
    closeCursors(cur_dev, cur_db)
    closeConns(conn_dev, conn_db)  
