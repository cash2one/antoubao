# /usr/bin/python
# coding=utf8

#1.获得指数指标的时间节点
#2.在E1表中寻找所有非坏站并依据value进行排序

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
import time
import sys

if __name__ == '__main__':
    _start_time = time.time()
    #获得连接        
    conn_dev = getConn(DEVHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_dev = getCursors(conn_dev)
    initializeCursors(cur_dev)
    
    SRCDB_INDEX_TARGET = "index_platform_list"
    SRCDB_INDEX = "index_weekly_report"
    
    #1.获得指数指标的时间节点
    date_list = getDifferentFieldlist(SRCDB_INDEX_TARGET, cur_dev, "date")
    date_number =len(date_list)
    alpha_list = [0] * date_number
    #判断是增量还是全量
    isreset = 0
    if (len(sys.argv) == 2):
        if (sys.argv[1] == "reset"):
            print "Reset '" + SRCDB_INDEX + "'"
            start = 0
            cur_dev.execute("DELETE FROM " + SRCDB_INDEX)
            conn_dev.commit()
            isreset = 1
    if isreset == 0:
        print "Update '" + SRCDB_INDEX + "'"
        start = date_number - 1
        stringSQL = "DELETE FROM " + SRCDB_INDEX + " WHERE `date` = '" + str(date_list[-1]) + "'"
        cur_dev.execute(stringSQL)
        conn_dev.commit()
    value_format = "%.4f"
    
    #获得所有指标
    field_index_list = getAllColumnsFromTable(cur_dev, SRCDB_INDEX, del_list = ["Id", "date"])
    _field_list_additive = ["weekly_outstanding_loan", "weekly_lending", "weekly_total_investor", "turnover_period"]
    _field_list_nonadditive = ["ave_annualized_return", "weekly_loan_period", "weekly_ave_bid_close_time"]
    _field_list = _field_list_additive + _field_list_nonadditive
    field_number = len(_field_list)
    field_index_dict = {}
    for field in _field_list:
        field_index_dict[field] = _field_list.index(field)
        
    #2.计算指数指标
    level_list = ["ALL", "aboveA", "belowA", "B++", "B+", "B", "C"]
    level_dict = {"ALL":["A++", "A+", "A", "B++", "B+", "B", "C"], "aboveA":["A", "A+", "A++"], "belowA":["C", "B", "B+", "B++"], "B++":["B++"], "B+":["B+"], "B":["B"], "C":["C"]}
    total_value_list = ["top300_value", "top10_value", "top10_score", "top20_value", "top20_score", "bad_sum"]
    field_name_dict = {"top300_value":"300", "top10_value":"value10", "top20_value":"value20", "top10_score":"security10", "top20_score":"security20", "bad_sum":"bad"}
    for j in range(start, date_number):
        _date = date_list[j]
        print _date
        #构造数据字典
        total_value_dict = {}
        #可以直接相加的参数
        total_value_dict["additive"] = {}
        for total_value in total_value_list:
            total_value_dict["additive"][total_value] = {}.fromkeys(_field_list_additive, 0)
        #不可以直接相加的参数，需要加权
        total_value_dict["nonadditive"] = {}
        for total_value in total_value_list:
            total_value_dict["nonadditive"][total_value] = {}.fromkeys(_field_list_nonadditive, 0)
        #构造评级字典
        total_level_dict = {}
        total_level_dict["additive"] = {}
        for total_level in level_dict:
            total_level_dict["additive"][total_level] = {}.fromkeys(_field_list_additive, 0)
        total_level_dict["nonadditive"] = {}
        for total_level in level_dict:
            total_level_dict["nonadditive"][total_level] = {}.fromkeys(_field_list_nonadditive, 0)
        A_level_dict = {} #只有好站才有，不同level下的按照A计算的公式
        A_level_dict_test = {} #和_level_dict公式相比，不用weekly_outstanding_loan相乘
        BB_level_dict = {} #只有好站才有，不同level下的按照B计算的公式
        BW_level_dict = {} #只有坏站才有，不同level下的按照B计算的公式再乘以alpha
        BW_level_dict_test = {} #和BW_level_dict相比，不用weekly_outstanding_loan相乘
        level_number_dict = {} #每个level中站的个数
        for total_level in level_dict:
            A_level_dict[total_level] = 0
            A_level_dict_test[total_level] = 0
            BB_level_dict[total_level] = 0
            BW_level_dict[total_level] = 0
            BW_level_dict_test[total_level] = 0
            level_number_dict[total_level] = 0
        
        bad_number_data = 0
        bad_number_nondata = 0
        good_number = 0
        A_weekly_outstanding_loan = 0
        BW_weekly_outstanding_loan = 0
        BB_weekly_outstanding_loan = 0
        stringSQL = "SELECT `source`, `status`, `level`, `rank_value`, `rank_score`,`" + "`,`".join(_field_list) + "` FROM " + SRCDB_INDEX_TARGET + " WHERE `date` = '" + str(_date) + "'" 
        cur_dev.execute(stringSQL)
        rets = cur_dev.fetchall()
        good_data_number = 0
        for ret in rets:
            value_dict = {}
            source = int(ret[0])
            status = float("%.3f" % float(ret[1]))
            level = ret[2]
            rank_value = int(ret[3])
            rank_score = ret[4]
            value_list = getNoNoneList(ret[5:])
            for i in range(field_number):
                value_dict[_field_list[i]] = float(value_list[i])
            value_dict["ave_annualized_return"] = value_dict["ave_annualized_return"] / 100.0 
            #没有数据的坏站
            if source == -2:
                bad_number_nondata += 1
            #有数据的站
            else:
                #有数据的坏站
                if status < 1:
                    bad_number_data += 1
                    weight = getWeightByStatus(status)
                    #处理加和
                    for field in _field_list_additive:
                        total_value_dict["additive"]["bad_sum"][field] += value_dict[field]
                    #处理加权
                    for field in _field_list_nonadditive:
                        total_value_dict["nonadditive"]["bad_sum"][field] += value_dict[field] * value_dict["weekly_lending"]
                    if level != None:
                        for total_level in level_dict:
                            if level in level_dict[total_level]:
                                BW_level_dict[total_level] += weight * value_dict["weekly_outstanding_loan"] / (1 + value_dict["ave_annualized_return"] * value_dict["weekly_loan_period"] / DAYSPERYEAR)
                                BW_level_dict_test[total_level] += weight / (1 + value_dict["ave_annualized_return"] * value_dict["weekly_loan_period"] / DAYSPERYEAR)
                    BW_weekly_outstanding_loan += weight * value_dict["weekly_outstanding_loan"] / (1 + value_dict["ave_annualized_return"] * value_dict["weekly_loan_period"] / DAYSPERYEAR)
                #有数据的好站
                else:
                    good_number += 1
                    #值相关
                    _dict = {"top10_value":rank_value <= 10,"top20_value":rank_value <= 20,"top10_score":False if rank_score == None else True if rank_score <= 10 else False,"top20_score":False if rank_score == None else True if rank_score <= 20 else False,"top300_value":rank_value <= 300}
                    for _key in _dict:
                        if _dict[_key]:
                            #处理加和
                            for field in _field_list_additive:
#                                 if field == "weekly_lending" and _key == "top10_value":
#                                     print value_dict[field]
                                total_value_dict["additive"][_key][field] += value_dict[field]
                            #处理加权
                            for field in _field_list_nonadditive:
                                total_value_dict["nonadditive"][_key][field] += value_dict[field] * value_dict["weekly_lending"]
                    
                    #评级相关
                    if level != None:
                        for total_level in level_dict:
                            if level in level_dict[total_level]:
                                for field in _field_list_additive:
                                    total_level_dict["additive"][total_level][field] += value_dict[field]
                                #处理加权
                                for field in _field_list_nonadditive:
                                    total_level_dict["nonadditive"][total_level][field] += value_dict[field] * value_dict["weekly_lending"]
                                A_level_dict[total_level] += value_dict["weekly_outstanding_loan"] * (value_dict["ave_annualized_return"] * DAYSPERWEEK / DAYSPERYEAR) / (1 + value_dict["ave_annualized_return"] * value_dict["weekly_loan_period"] / DAYSPERYEAR)
                                A_level_dict_test[total_level] += (value_dict["ave_annualized_return"] * DAYSPERWEEK / DAYSPERYEAR) / (1 + value_dict["ave_annualized_return"] * value_dict["weekly_loan_period"] / DAYSPERYEAR)
                                level_number_dict[total_level] += 1
                                BB_level_dict[total_level] += value_dict["weekly_outstanding_loan"] / (1 + value_dict["ave_annualized_return"] * value_dict["weekly_loan_period"] / DAYSPERYEAR)
                    BB_weekly_outstanding_loan += value_dict["weekly_outstanding_loan"] / (1 + value_dict["ave_annualized_return"] * value_dict["weekly_loan_period"] / DAYSPERYEAR)
                    A_weekly_outstanding_loan += value_dict["weekly_outstanding_loan"] * (value_dict["ave_annualized_return"] * DAYSPERWEEK / DAYSPERYEAR) / (1 + value_dict["ave_annualized_return"] * value_dict["weekly_loan_period"] / DAYSPERYEAR)
        #规律指标
        kv={}
        weekly_lending_300 = total_value_dict["additive"]["top300_value"]["weekly_lending"]
        #可加指标
        for field in _field_list_additive:
            for total_value in total_value_list:
                if total_value in ["top300_value", "bad_sum"]: 
                    k = field + "_" + field_name_dict[total_value]
                    kv[k] = total_value_dict["additive"][total_value][field]
                if total_value in ["top10_value", "top10_score", "top20_value", "top20_score"]:                     
                    k = "weighted_" + field + "_" + field_name_dict[total_value]
                    kv[k] = total_value_dict["additive"][total_value][field] / total_value_dict["additive"]["top300_value"][field]
                insertField(conn_dev, cur_dev, SRCDB_INDEX, k, "DOUBLE DEFAULT NULL")
            for total_level in level_list:
                k = "weighted_" + field + "_" + total_level
                kv[k] = total_level_dict["additive"][total_level][field] / total_value_dict["additive"]["top300_value"][field]
                insertField(conn_dev, cur_dev, SRCDB_INDEX, k, "DOUBLE DEFAULT NULL")
        
        #加权指标    
        for field in _field_list_nonadditive:
            for total_value in total_value_list:
                if total_value in ["top300_value"]:
                    k = field + "_" + field_name_dict[total_value]
                    kv[k] = total_value_dict["nonadditive"][total_value][field] / total_value_dict["additive"]["top300_value"]["weekly_lending"]                   
                if total_value in ["top10_value", "top10_score", "top20_value", "top20_score", "bad_sum"]:                     
                    k = "average_" + field + "_" + field_name_dict[total_value]
                    if total_value_dict["additive"][total_value]["weekly_lending"] == 0:
                        kv[k] = 0
                    else:
                        kv[k] = total_value_dict["nonadditive"][total_value][field] / total_value_dict["additive"][total_value]["weekly_lending"]
                insertField(conn_dev, cur_dev, SRCDB_INDEX, k, "DOUBLE DEFAULT NULL")
            for total_level in level_list:
                k = "average_" + field + "_" + total_level
                kv[k] = total_level_dict["nonadditive"][total_level][field] / total_level_dict["additive"][total_level]["weekly_lending"]
                insertField(conn_dev, cur_dev, SRCDB_INDEX, k, "DOUBLE DEFAULT NULL")
        #特殊A、B指标
        #alpha = total_value_dict["additive"]["bad_sum"]["weekly_outstanding_loan"] / (total_value_dict["additive"]["bad_sum"]["weekly_outstanding_loan"] + bad_number_nondata * 500)
        alpha = BW_weekly_outstanding_loan / (BW_weekly_outstanding_loan + bad_number_nondata * 450)
        if alpha == 0:
            alpha = 0.6
        beta = 0.65 / alpha
#         print alpha
        k = "beta"
        kv[k] = beta
        insertField(conn_dev, cur_dev, SRCDB_INDEX, k, "DOUBLE DEFAULT NULL")
        B_bad = BW_level_dict["ALL"]
        A_300 = A_level_dict["ALL"]
        B_300 = BB_level_dict["ALL"]
        for total_level in level_list:
            BW_level_dict[total_level] *= beta
            BW_level_dict_test[total_level] *= beta
#         print "分子减数"
#         print A_level_dict
#         print "分子被减数"
#         print BW_level_dict
#         print "分母"
#         print getDictFromDict(total_level_dict["additive"], "weekly_outstanding_loan")
        BW_weekly_outstanding_loan *= beta
        for total_level in level_list:
            k = "interest_rate_" + total_level
            #kv[k] = WEEKSPERYEAR * (A_level_dict[total_level] - BW_level_dict[total_level]) / BB_level_dict[total_level]
            kv[k] = WEEKSPERYEAR * (A_level_dict[total_level] - BW_level_dict[total_level]) / total_level_dict["additive"][total_level]["weekly_outstanding_loan"]
#             if total_level in ["C"]:
#                 print total_level
#                 print A_level_dict[total_level]
#                 print BW_level_dict[total_level]
#                 print A_level_dict[total_level] - BW_level_dict[total_level]
#                 print total_level_dict["additive"][total_level]["weekly_outstanding_loan"]
#                 print "interest_rate_C:" + str(kv[k])
            insertField(conn_dev, cur_dev, SRCDB_INDEX, k, "DOUBLE DEFAULT NULL")
            
        #新增interest_rate的非weekly_outstanding_loan加权
        for total_level in level_list:
            k = "interest_rate_" + total_level + "_uw"
            kv[k] = WEEKSPERYEAR * (A_level_dict_test[total_level] - BW_level_dict_test[total_level]) / level_number_dict[total_level]
            insertField(conn_dev, cur_dev, SRCDB_INDEX, k, "DOUBLE DEFAULT NULL")
                
        #其他指标 
        kv["gotten_bad_numbe"] = bad_number_data
        kv["total_bad_number"] = bad_number_data + bad_number_nondata
        kv["scale"] = 0.7 * total_value_dict["additive"]["top300_value"]["weekly_lending"] + 0.3 * total_value_dict["additive"]["top300_value"]["weekly_total_investor"] 
        kv["interest_gross"] = A_weekly_outstanding_loan
        kv["interest_pure"] = A_weekly_outstanding_loan - BW_weekly_outstanding_loan
        #kv["money_loss_ratio_weekly"] = BW_level_dict["ALL"] / BB_level_dict["ALL"]
        kv["money_loss_ratio_weekly"] = BW_level_dict["ALL"] / total_value_dict["additive"]["top300_value"]["weekly_outstanding_loan"]  
        #kv["real_interest_rate_300"] = WEEKSPERYEAR * kv["interest_pure"] / BB_level_dict["ALL"] 
        kv["real_interest_rate_300"] = WEEKSPERYEAR * kv["interest_pure"] / total_value_dict["additive"]["top300_value"]["weekly_outstanding_loan"]   
        
        #临时指标，方便后面和历史有关的指标计算
        kv["temp_B_bad"] = BW_level_dict["ALL"]
        #kv["temp_B_300"] = BB_level_dict["ALL"]
        kv["temp_B_300"] = total_value_dict["additive"]["top300_value"]["weekly_outstanding_loan"]  
        
        #插入数据
        k_list = []
        v_list = []
        for k, v in kv.items():
            insertField(conn_dev, cur_dev, SRCDB_INDEX, k, "DOUBLE DEFAULT NULL")
            k_list.append(k)
            v_list.append(str(v))
        k_list = k_list + ["date"]
        v_list = v_list + [str(_date)]
        stringSQL = "INSERT INTO " + SRCDB_INDEX + "(`" + "`,`".join(k_list) + "`) VALUES('" + "','".join(v_list) + "')"
        stringSQL = stringSQL.replace("'None'", "NULL")
        cur_dev.execute(stringSQL)
        conn_dev.commit()
     
    closeCursors(cur_dev)
    closeConns(conn_dev)  
    _end_time = time.time()
    print "The whole program costs " + str(_end_time - _start_time) + " seconds."  
    
