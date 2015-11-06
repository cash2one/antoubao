#!/usr/bin/python
# -*- coding: utf-8 -*-
#从H表找到得分前30的好站（时间为真实时间），从Y表和E2表中得到所有的坏站id，然后从Y表得到status和出事时间的前两周），然后从E2表中得到响应时间所有这些站的数据，最后进行神经网络回归计算
#得到回归模型后，对view_mobile表中score不为零的站进行预测（数据来源为E2）

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from elm import ELMRegressor
from random_hidden_layer import SimpleRandomHiddenLayer

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from atbtools.learnTools import *
import time

if __name__ == '__main__':
    _start_time = time.time()
    font = {'family' : 'serif',  
        'color'  : 'darkred',  
        'weight' : 'normal',  
        'size'   : 20,  
        } 
    #数据表格指定
    srcdb_H = "platform_score_H" # 好站来源，H表得分前30的好站
    srcdb_Y = "platform_problem_record_Y" #坏站来源，查询站点的status
    srcdb_E2 = "platform_quantitative_data_E2" #字段属性来源
    srcdb_E3 = "platform_quantitative_data_E3" 
    srcdb_view_mobile = "view_mobile" # 预测集来源
    dstdb_model = "platform_status_regression_model" #汇总
    dstdb_predict = "platform_status_regression_predict" #汇总
    #制定测试集的个数百分比
    test_ratio = 0.5
    #定义隐藏节点个数
    n_hidden_list = [1] #range(1,201)
    #定义回归器函数类型
    activation_func_list = ["sigmoid"] #["sigmoid", "tanh", "tribas", "hardlim", "rbf"]
    #定义随机数选择策略，0为默认随机数，1为真正的随机数
    random_state = 1
    #多次计算验证模型
    model_times = 1 #100
    #指定需要的好站个数
    platform_good_number = 30
    #获取连接
    conn_dev = getConn(DEVHOST, USERNAME, PASSWORD, DB, PORT)
    cur_dev1 = getCursors(conn_dev)
    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db1 = getCursors(conn_db)
    initializeCursors(cur_dev1, cur_db1)
    ###1.获得相关的属性值列表
    #从E2表里获取所有特征值，如果某个特征值属性为零，就用其他站的平均值代替，注意好站坏站要分开处理
    #定义不相关的属性
    field_del_list = ["id", "platform_id", "platform_name","date","black", "weekly_ave_investment_per_bid", "top5_ratio_investment", "top10_ratio_investment"]
    #获得E3里面的属性列表
    field_E3_list = getAllColumnsFromTable(cur_dev1, srcdb_E3, del_list = field_del_list, merge_list = None)
    #E2里面的属性（只找E3里面有的）
    field_list = getAllColumnsFromTable(cur_dev1, srcdb_E3, del_list = field_del_list, merge_list = field_E3_list)
    #定义定量属性
    field_quantitative_list = ["weekly_total_investor", "weekly_lending", "weekly_total_borrower", "weekly_loan_period", "ave_annualized_return", "cash_flow_in", "weekly_outstanding_loan", "investor_HHI", "borrower_HHI", "weekly_ave_lending_per_bid", "weekly_ave_bid_close_time", "weekly_new_investor", "provision_of_risk", "weekly_ave_investment_old", "top5_ratio_loan", "top10_ratio_loan", "weekly_ave_lending_per_borrower", "weekly_ave_investment", "weekly_ratio_new_old", "borrower_growth", "investor_growth", "latest4week_lending", "outstanding_loan", "turnover_registered", "not_returned_yet", "money_growth", "turnover_period", "short_term_debt_ratio", "market_share_growth"]
    field_quantitative_list = list(set(field_list) & set(field_quantitative_list))
    field_quantitative_index_list = [field_list.index(_field) for _field in field_quantitative_list]
    #定义关键属性，如果关键属性值为零，则该平台舍去
    zero_field_del_list = ["weekly_lending", "registered_cap"] 
    zero_field_index_del_list = [field_list.index(_field) for _field in zero_field_del_list]
    
    ###2.确定计算回归的数据时间
    date_list_view_mobile = getDifferentFieldlist(srcdb_view_mobile, cur_dev1, "date")
    date_list_H = getDifferentFieldlist(srcdb_H, cur_dev1, "date")
    date_list_E2 = getDifferentFieldlist(srcdb_E2, cur_dev1, "date")
    date_list = list(set(date_list_view_mobile) & set(date_list_H) & set(date_list_E2))
    regression_date = max(date_list)
    print "The regression timestamp is " + str(regression_date) + "."
    
    ###3. 获得好站和坏站数据作为训练集合测试集
    ##3.1 获得坏站平台字典
    #3.1.1. 获得所有E2表内的platform_id
    platform_id_E2_list = getDifferentFieldlist(srcdb_E2, cur_dev1, "platform_id")
    #3.1.2. 从Y表中获得这些平台的name、status以及坏站时间（前两周）
    platform_model_bad_dict = {}
    stringSQL = "SELECT platform_id, platform_name, min(date), status FROM " + srcdb_Y + " GROUP BY platform_id"
    cur_db1.execute(stringSQL)
    for platform_id, platform_name, _date, status in cur_db1.fetchall():
        if platform_id in platform_id_E2_list:
            platform_id = str(platform_id)
            platform_model_bad_dict[platform_id] = {}
            platform_model_bad_dict[platform_id]["platform_id"] = platform_id
            platform_model_bad_dict[platform_id]["platform_name"] = str(platform_name)
            platform_model_bad_dict[platform_id]["date"] = getTimestampZero(int(_date), 0, 0) - SECONDSPERWEEK
            platform_model_bad_dict[platform_id]["status"] = float(status)
    platform_bad_number = len(platform_model_bad_dict)
    
    ##3.2 获得好站平台字典
    #从H表得打到得分前30的好站platform_id
    platform_model_good_dict = {}
    blank_repeat_platform_list = []
    platform_good_number = 30
    level_id_list = ["A++", "A+", "A", "B++", "B+", "B", "C++", "C+", "C"]
    stringSQL = "SELECT DISTINCT platform_id, platform_name FROM " + srcdb_H + " WHERE `date` = '" + str(regression_date) + "' AND `platform_id` not in ('" + "','".join(level_id_list) + "')" + " ORDER BY score DESC"
    print stringSQL
    cur_dev1.execute(stringSQL)
    count = 0
    for platform_id, platform_name in cur_dev1.fetchall():
        platform_id = str(platform_id)
        if platform_id in platform_model_bad_dict:
            print "###################################################################"
            print platform_name + " is both good and bad platform, something must be wrong! "
            blank_repeat_platform_list.append(platform_id)
            print "###################################################################"
            continue
        platform_model_good_dict[platform_id] = {}
        platform_model_good_dict[platform_id]["platform_id"] = platform_id
        platform_model_good_dict[platform_id]["platform_name"] = str(platform_name)
        platform_model_good_dict[platform_id]["date"] = int(regression_date)
        platform_model_good_dict[platform_id]["status"] = 1.0
        count +=1
        if count == platform_good_number:
            break
    for platform_id in blank_repeat_platform_list:
        del platform_model_bad_dict[platform_id]
        platform_bad_number -= 1
    print 
    print "Firstly, there are " + str(platform_good_number) + " good and " + str(platform_bad_number) + " bad platforms."
        
    for platform_model_good in platform_model_good_dict:
        print platform_model_good_dict[platform_model_good]["date"]
        
        
        
    ##3.3 获得好站和坏站的属性值数据
    #3.3.1 从E2表中拿到所需要的属性值(包括关键值为零的清洗)
    platform_model_bad_dict = getFieldValueFromTableByIdByDate(cur_dev1, srcdb_E2, "fields", field_list, platform_model_bad_dict, zero_field_index_del_list)
    platform_bad_number = len(platform_model_bad_dict)
    platform_model_good_dict = getFieldValueFromTableByIdByDate(cur_dev1, srcdb_E2, "fields", field_list, platform_model_good_dict, zero_field_index_del_list)
    platform_good_number = len(platform_model_good_dict)
    platform_model_bad_dict = cleanZeroValueByAverage(field_quantitative_index_list, "fields", platform_model_bad_dict)
    platform_model_good_dict = cleanZeroValueByAverage(field_quantitative_index_list, "fields",platform_model_good_dict)
    platform_model_dict=dict(platform_model_bad_dict, **platform_model_good_dict)
    platform_model_number = len(platform_model_dict)
    print 
    print "In the end, there are " + str(platform_good_number) + " good and " + str(platform_bad_number) + " bad platforms for modeling."
    #3.3.2 从H表查询每个站的score
    platform_model_dict = addNewFieldFromTableByIdByDate(cur_dev1,srcdb_H,"score",platform_model_dict,None_default = 0)
    #3.3.2.2 附加：改写好站坏站的status分布
    change_dict = {0.0:0.0, 0.3:0.0, 0.5:0.0, 0.7:0.0, 0.6:0.0, 0.9:1.0, 1.0:1.0}
    #platform_model_dict = changeStatus(platform_model_dict, "status", change_dict)
    #3.3.3 写入训练集和测试集的基本属性
    cur_dev1.execute("TRUNCATE " + dstdb_model)
    conn_dev.commit()
    key_initial_list = ["platform_id", "platform_name","date","status","score"]
    insertTableByDict(cur_dev1, conn_dev, dstdb_model, key_initial_list, platform_model_dict, "insert", "fields", field_list)
    print 
    print "There are " + str(platform_model_number - int(platform_model_number * test_ratio)) + " training sets and " + str(int(platform_model_number * test_ratio)) + " testing sets."
    print 
    exit(0)
#     ###4. 获得要预测的平台的数据字典
#     ##4.1 获得view_mobile中score不为零的数据以及从E2中返回的属性值
#     platform_predict_dict = {}
#     stringSQL = "SELECT platform_id, platform_name, score, status FROM " + srcdb_view_mobile
#     cur_dev1.execute(stringSQL)
#     for platform_id, platform_name, score, status in cur_dev1.fetchall():
#         if float(score) != 0 and None != status:
#             if platform_id not in platform_predict_dict:
#                 platform_id = str(platform_id)
#                 platform_predict_dict[platform_id] = {}
#                 platform_predict_dict[platform_id]["platform_id"] = platform_id
#                 platform_predict_dict[platform_id]["platform_name"] = str(platform_name)
#                 platform_predict_dict[platform_id]["score"] = float(score)
#                 platform_predict_dict[platform_id]["status"] = float(status)
#                 platform_predict_dict[platform_id]["date"] = int(regression_date)
#     platform_predict_dict = getFieldValueFromTableByIdByDate(cur_dev1, srcdb_E2, "fields", field_list, platform_predict_dict)
#     ##4.2 对预测集进行预处理        
#     X_predict, y_predict, X_predict_train, y_predict_train, name_predict_train, X_predict_test, y_predict_test, name_predict_test = train_test_split(platform_predict_dict, x_key ="fields", y_key = "status", threshold = 1.0, test_size = 1)
#     print 
#     print "There are " + str(len(X_predict_test)) + " platforms to predict."
#    
#     ##4.2 写入预测集的基本属性
#     cur_dev1.execute("TRUNCATE " + dstdb_predict)
#     conn_dev.commit()
#     key_initial_list = ["platform_id", "platform_name","date","status","score"]
#     insertTableByDict(cur_dev1, conn_dev, dstdb_predict, key_initial_list, platform_predict_dict, "insert", "fields", field_list)

    #获得训练集和测试集表格的已有属性
    field_in_dstdb_model_list = getAllColumnsFromTable(cur_dev1, dstdb_model)
    field_in_dstdb_predict_list = getAllColumnsFromTable(cur_dev1, dstdb_predict)
    
    ###5. 构建回归模型并进行预测
    print "Doing regression analysis..."
    prediction_method_number = len(activation_func_list) * len(n_hidden_list)
    regressor_list = [0] * prediction_method_number
    prediction_method_list = []
    correct_proportion_dict = {}
    counter = 0
    for activation_func in activation_func_list:
        correct_proportion_dict[activation_func]={}
        for n_hidden in n_hidden_list:
            counter += 1
            print str(counter) + "/" + str(prediction_method_number) + ": Activation_func is '" + str(activation_func) + "' and n_hidden is '"+ str(n_hidden) +"'."
            ###5.1 构建回归模型
            #根据隐藏节点个数和激活函数名称（ELM）获得回归器
            prediction_method = "status_" + str(activation_func) + "_" + str(n_hidden)
            prediction_method_shortname = str(activation_func) + "_" + str(n_hidden)
            correct_proportion_dict[activation_func][n_hidden] = []
            for i in range(model_times):
                #3.3.4 通过数据集字典进行训练集和测试集的划分，注意按照两个等级分别提取训练集合测试集        
                X_modle, y_model, X_model_train, y_model_train, name_model_train, X_model_test, y_model_test, name_model_test = train_test_split(platform_model_dict, x_key ="fields", y_key = "status", threshold = 0.5, test_size = test_ratio)
                #返回ELM模式，func表示回归器函数类型，nh表示隐藏节点个数，rs表示随机数的选取方法，如果是零的化返回内置随机数（每次运行结果一致）, dorc表示希望结果是分类的还是连续的，以c开头表示连续，以d开头表示分类
                regressor = make_regressor(activation_func, n_hidden, rs = random_state, dorc = "continuous")
                #训练数据
                regressor.fit(X_model_train, y_model_train)
                regressor_list[counter - 1] = regressor
                #预测得分
                prediction_train = regressor.predict(X_model_train)
                for i in range(len(prediction_train)):
                    platform_id = name_model_train[i]
                    platform_model_dict[str(platform_id)][prediction_method] = prediction_train[i] 
                if len(X_model_test) == 0:
                    prediction_test=[]
                else:
                    prediction_test = regressor.predict(X_model_test)
                    for i in range(len(prediction_test)):
                        platform_id = name_model_test[i]
                        platform_model_dict[str(platform_id)][prediction_method] = prediction_test[i] 
                #附加：通过给定的区间节点，将连续的预测值变为离散的预测值
                platform_model_dict = changePredictionFromCToD(platform_model_dict, prediction_method, [0.5], [0.0, 1.0])
#                 #写入数据库
#                 if prediction_method not in field_in_dstdb_model_list:
#                     stringSQL = "ALTER TABLE " + dstdb_model + " ADD " + prediction_method + " FLOAT DEFAULT NULL"
#                     cur_dev1.execute(stringSQL) #如果没有该字段则新建字段
#                 insertTableByDict(cur_dev1, conn_dev, dstdb_model, [prediction_method], platform_model_dict, sql_method ="update")
                #验证与已知结果的一致性，用正确个数的比例来比较(只保留测试集而不包括训练集)
                correct_proportion = calculateCorrectProportion(platform_model_dict, "status", prediction_method, name_model_test)
                correct_proportion_dict[activation_func][n_hidden].append(correct_proportion)
#                 ###5.2 对预测集进行预测
#                 prediction_test = regressor.predict(X_predict_test)
#                 for i in range(len(prediction_test)):
#                     platform_id = name_predict_test[i]
#                     platform_predict_dict[str(platform_id)][prediction_method] = prediction_test[i] 
#                 #附加：通过给定的区间节点，将连续的预测值变为离散的预测值
#                 platform_predict_dict = changePredictionFromCToD(platform_predict_dict, prediction_method, [0.5], [0.0, 1.0])
#                 #写入数据库
#                 if prediction_method not in field_in_dstdb_predict_list:
#                     stringSQL = "ALTER TABLE " + dstdb_predict + " ADD " + prediction_method + " FLOAT DEFAULT NULL"
#                     cur_dev1.execute(stringSQL) #如果没有该字段则新建字段
#                 insertTableByDict(cur_dev1, conn_dev, dstdb_predict, [prediction_method], platform_predict_dict, sql_method ="update")
        ###6 绘制model的图像来检验参数n_hidden
        correct_proportion_mean_list = []
        correct_proportion_max_list = []
        correct_proportion_min_list = []
        correct_proportion_dict_temp = correct_proportion_dict[activation_func]
        for n_hidden in n_hidden_list:
            correct_proportion_mean_list.append(np.mean(correct_proportion_dict_temp[n_hidden]))
            correct_proportion_max_list.append(max(correct_proportion_dict_temp[n_hidden]))
            correct_proportion_min_list.append(min(correct_proportion_dict_temp[n_hidden]))
        correct_proportion_mean_array = np.array(correct_proportion_mean_list)
        correct_proportion_lowerr_array = correct_proportion_mean_array - np.array(correct_proportion_min_list)
        correct_proportion_uperr_array = np.array(correct_proportion_max_list) - correct_proportion_mean_array
        _errorbar = plt.errorbar(np.array(n_hidden_list), correct_proportion_mean_array, yerr=np.array([correct_proportion_lowerr_array,correct_proportion_uperr_array]), marker='s',ls='--', ms=8, label = activation_func)
    matplotlib.rcParams["font.size"] = 20 #修改画图的默认值
    plt.xlabel("N_Hidden")
    plt.ylabel("Accuracy_Rate")
    plt.xlim(min(n_hidden_list)-0.5,max(n_hidden_list)+0.5)
    #plt.ylim(min(correct_proportion_min_list)-0.1,max(correct_proportion_max_list)+0.1)
    plt.xticks(range(0,max(n_hidden_list)+1,40))
    #plt.yticks(fontsize = 20)
    _title = "N_Hidden .vs. Accuracy_Rate (" + str(model_times) + " samples)"
    plt.title(_title, fontsize = 20)
    plt.legend(loc='lower right', numpoints = 1, scatterpoints = 1, fontsize = 15)  
    picture_name = "nh_test.jpg"
    plt.savefig(picture_name)          
    #plt.show() #不显示图像
            
    closeCursors(cur_dev1, cur_db1)
    closeConns(conn_dev,conn_db)
    print ""
    print "finished"
    _end_time = time.time()
    print "The whole clean program costs " + str(_end_time - _start_time) + " seconds."  