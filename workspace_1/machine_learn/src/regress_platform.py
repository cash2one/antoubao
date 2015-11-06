#!/usr/bin/python
# -*- coding: utf-8 -*-
#从H表找到得分前30的好站（时间为真实时间），从view_mobile表中得到status<1的坏站（时间为Y表中反查出的出事时间的前两周），然后从E2表中得到响应时间所有这些站的数据，最后进行神经网络回归计算

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from elm import ELMRegressor
from random_hidden_layer import SimpleRandomHiddenLayer

from header import *
from computeTools import *
import time
from mysqlTools import *
import random

#同numpy中array的下标寻找，但增加了0下标筛选的功能
def selectByIndexlist(X,index_list):
    if len(index_list) != 0:
        return  X[np.array(index_list)]
    else:
        return np.array([])

#通过数据集字典进行训练集和测试集的划分，注意按照两个等级分别提取训练集合测试集        
def train_test_split(status_dict, x_key = "fields", y_key = "status", threshold = 1.0, test_size = 0.5):
    min_test_number = 0 #最少测试集的个数
    X = []
    y = []
    name_list = []
    status_dict_number = len(status_dict)
    for key in status_dict:
        X.append(status_dict[key][x_key])
        y.append(status_dict[key][y_key])
        name_list.append(key)
    X = StandardScaler().fit_transform(np.array(X)) #归一化
    y = np.array(y)
    good_index_list = []
    bad_index_list = []
    for i in range(status_dict_number):
        if y[i] < threshold:
            bad_index_list.append(i)
        else:
            good_index_list.append(i)
    good_test_number = max(int(len(good_index_list) * test_size),min_test_number)
    bad_test_number = max(int(len(bad_index_list) * test_size),min_test_number)
    if good_test_number == 0:
        good_test_index_list = []
    else:
        good_test_index_list = random.sample(good_index_list,good_test_number)
    if bad_test_number == 0:
        bad_test_index_list = []
    else:
        bad_test_index_list = random.sample(bad_index_list,bad_test_number)
    test_index_list = good_test_index_list + bad_test_index_list
    train_index_list = list(set(range(status_dict_number)) - set(test_index_list))
    print train_index_list
    print test_index_list
    X_test = selectByIndexlist(X,test_index_list)
    X_train = selectByIndexlist(X,train_index_list)
    print len(X_train)
    y_test = selectByIndexlist(y,test_index_list)
    y_train = selectByIndexlist(y,train_index_list)
    name_test = selectByIndexlist(np.array(name_list),test_index_list).tolist()
    name_train = selectByIndexlist(np.array(name_list),train_index_list).tolist()
    return X, y, X_train, y_train, name_train, X_test, y_test, name_test 
#返回ELM模式
def make_regressor(func, nh):
    srhl = SimpleRandomHiddenLayer(n_hidden=nh,
                                        activation_func=func,
                                        random_state=0)
    return ELMRegressor(srhl, regressor=LogisticRegression())

if __name__ == '__main__':
    _start_time = time.time()
    # 指定查询时间
    end_date = getQueryTime()[1]
    srcdb_T = "view_mobile" # T表status<1的坏站
    srcdb_H = "platform_score_H" # H表得分前30的好站
    srcdb_E2 = "platform_quantitative_data_E2" #字段来源
    srcdb_Y = "platform_problem_record_Y" #查询站点的status
    dstdb = "platform_status_regression" #汇总
    dstdb_whole = "platform_status_regression_whole" #汇总
    #制定测试集的个数百分比
    test_ratio = 0
    #定义隐藏节点个数
    n_hidden = 10
    #定义回归器函数类型
    activation_func = "tanh"
    #获取连接
    conn_dev = getConn(DEVHOST, USERNAME, PASSWORD, DB, PORT)
    cur_dev1 = getCursors(conn_dev)
    initializeCursors(cur_dev1)
    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db1 = getCursors(conn_db)
    initializeCursors(cur_db1)
    
    #确定标记时间
    date_list_T = getDifferentFieldlist(srcdb_T, cur_dev1, "date")
    date_list_H = getDifferentFieldlist(srcdb_H, cur_dev1, "date")
    date_list_E2 = getDifferentFieldlist(srcdb_E2, cur_dev1, "date")
    date_list = list(set(date_list_T) & set(date_list_H) & set(date_list_E2))
    regression_date = max(date_list)
    print "The regression timestamp is " + str(regression_date) + "."
    
    #获得全部数据集
    platform_status_dict = {}
    #从T表得到status<1的坏站platform_id
    stringSQL = "SELECT platform_id, platform_name, status FROM " + srcdb_T + " WHERE `status` < 1 AND `date` = '" + str(regression_date) + "'" 
    print stringSQL
    cur_dev1.execute(stringSQL)
    for platform_id, platform_name, status in cur_dev1.fetchall():
        platform_status_dict[str(platform_id)] = {}
        print platform_name
        platform_status_dict[str(platform_id)]["status_true"] = float(status)
        platform_status_dict[str(platform_id)]["platform_name"] = platform_name

    #从db_Y表获得坏站的“坏时间”
    blank_bad_platform_list = []
    for platform_id in platform_status_dict:
        platform_name = platform_status_dict[platform_id]["platform_name"]
        stringSQL = "SELECT min(date) FROM " + srcdb_Y + " WHERE `platform_id` = '" + str(platform_id) + "'" 
        row_number = cur_db1.execute(stringSQL)
        if row_number == 0:
            print "DELETE: there is no 'bad time' for bad platform " + platform_name
            blank_bad_platform_list.append(platform_id)
        else:
            platform_status_dict[platform_id]["badtime"] = getTimestampZero(int(cur_db1.fetchone()[0]), 0, 0) - SECONDSPERWEEK
    for platform_id in blank_bad_platform_list:
        del platform_status_dict[platform_id]
    platform_bad_number = len(platform_status_dict)
    
    #从H表得打到得分前30的好站platform_id
    blank_repeat_platform_list = []
    platform_good_number = 30
    level_id_list = ["A++", "A+", "A", "B++", "B+", "B", "C++", "C+", "C"]
    stringSQL = "SELECT DISTINCT platform_id, platform_name FROM " + srcdb_H + " WHERE `date` = '" + str(regression_date) + "' AND `platform_id` not in ('" + "','".join(level_id_list) + "')" + " ORDER BY score DESC"
    cur_dev1.execute(stringSQL)
    count = 0
    for platform_id, platform_name in cur_dev1.fetchall():
        if platform_id in platform_status_dict:
            print "###################################################################"
            print platform_name + " is both good and bad platform, something must be wrong! "
            blank_repeat_platform_list.append(platform_id)
            print "###################################################################"
            continue
        platform_status_dict[str(platform_id)] = {}
        platform_status_dict[str(platform_id)]["status_true"] = 1.0
        platform_status_dict[str(platform_id)]["platform_name"] = platform_name
        platform_status_dict[str(platform_id)]["badtime"] = int(regression_date)
        count +=1
        if count == platform_good_number:
            break
    for platform_id in blank_repeat_platform_list:
        del platform_status_dict[platform_id]
        platform_bad_number -= 1
    print "Firstly, there are " + str(platform_good_number) + " good and " + str(platform_bad_number) + " bad platforms."
    if len(platform_status_dict) != platform_good_number + platform_bad_number:
        print "There are " + str(platform_status_dict) + "platforms only." 
        exit(0)
    #获取所有特征值
    blank_platform_list = []
    field_del_list = ["id", "platform_id", "platform_name","date","black"]
    field_list =[]
    stringSQL = "SHOW FULL COLUMNS FROM " + srcdb_E2
    cur_dev1.execute(stringSQL)
    for field_temp in cur_dev1.fetchall():
        if  field_temp[0] in field_del_list:
            continue
        field_list.append(field_temp[0])
    for platform_id in platform_status_dict:
        platform_status_dict[str(platform_id)]["fields"] = []
        stringSQL = "SELECT "+','.join(field_list)+" FROM " + srcdb_E2+ " WHERE `date` = '" + str(platform_status_dict[platform_id]["badtime"]) + "' AND `platform_id` = '" + platform_id + "'"
        have_data = cur_dev1.execute(stringSQL)
        if have_data == 0:
            if platform_status_dict[str(platform_id)]["status_true"] < 1:
                print "Bad " + str(platform_status_dict[platform_id]["platform_name"]) + " delete: There is no data on timestamp " + str(platform_status_dict[platform_id]["badtime"])
                platform_bad_number -= 1
            else:
                platform_good_number -= 1
                print "Good " + str(platform_status_dict[platform_id]["platform_name"]) + " delete: There is no data on timestamp " + str(platform_status_dict[platform_id]["badtime"])
            blank_platform_list.append(platform_id)
            continue
        field_values = cur_dev1.fetchone()
        platform_status_dict[str(platform_id)]["fields"]=list(field_values)
    #去掉没有数据的站
    for platform_id in blank_platform_list:
        del platform_status_dict[platform_id]
    print "In the end, there are " + str(platform_good_number) + " good and " + str(platform_bad_number) + " bad platforms."
    
    #通过数据集字典进行训练集和测试集的划分，注意按照两个等级分别提取训练集合测试集        
    X, y, X_train, y_train, name_train, X_test, y_test, name_test = train_test_split(platform_status_dict, x_key ="fields", y_key = "status_true", threshold = 1.0, test_size = test_ratio)
    print "There are " + str(len(X_train)) + " training sets and " + str(len(X_test)) + " testing sets."
    print "#####训练数据汇总#####"
    print "good platform:"
    for platform_id in platform_status_dict:
        platform_temp = platform_status_dict[platform_id]
        if platform_id in name_train:
            print platform_temp["platform_name"] + ": " + str(platform_temp["status_true"])
    print "#####################"
    print "Doing regression analysis..."
    #根据隐藏节点个数和激活函数名称（ELM）获得回归器
    regressor = make_regressor(activation_func, n_hidden)
    #训练数据
    regressor.fit(X_train, y_train)
    #预测得分
    prediction_train = regressor.predict(X_train)
    for i in range(len(prediction_train)):
        platform_id = name_train[i]
        platform_status_dict[str(platform_id)]["status_predict"] = prediction_train[i] 
    if len(X_test) == 0:
        prediction_test=[]
    else:
        prediction_test = regressor.predict(X_test)
        for i in range(len(prediction_test)):
            platform_id = name_test[i]
            platform_status_dict[str(platform_id)]["status_predict"] = prediction_test[i] 
    #虚拟判定系数pseudo-R2
    #r2 = r2_score(y_test, prediction_test)
    #清除原表
    cur_dev1.execute("TRUNCATE " + dstdb)
    conn_dev.commit()
    #写入数据库
    key_list = ["platform_id", "platform_name","date"] + field_list + ["status_true", "status_predict", "score"]
    for platform_id in platform_status_dict:
        platform_temp = platform_status_dict[platform_id]
        value_list = [platform_id, platform_temp["platform_name"], str(platform_temp["badtime"])]
        for field_temp in platform_temp["fields"]:
            value_list.append(str(field_temp))
        stringSQL = "SELECT score FROM " + srcdb_H + " WHERE `date` = '" + str(regression_date) + "' AND `platform_id` ='" + str(platform_id) + "'"
        row_number = cur_dev1.execute(stringSQL)
        score = 0 if row_number == 0 else float(cur_dev1.fetchone()[0])
        value_list = value_list + [str(platform_temp["status_true"]), str(platform_temp["status_predict"]), str(score)]
        stringSQL = "INSERT INTO " + dstdb + "(`" + "`,`".join(key_list) + "`) VALUES('" + "','".join(value_list) + "')"
        cur_dev1.execute(stringSQL)
        conn_dev.commit() 
    
    print "Model training completed."   
#     #重新预测全站得分
#     print "Doing prediction analysis...."  
#     #清除原表
#     cur_dev1.execute("TRUNCATE " + dstdb_whole)
#     conn_dev.commit()
#     #从E2抓取全站数据
#     X_test = []
#     platform_whole_id_list = []
#     platform_whole_name_list = []
#     key_list = ["platform_id", "platform_name"] + field_list
#     stringSQL = "SELECT "+','.join(key_list)+" FROM " + srcdb_E2+ " WHERE `date` = '" + str(regression_date) + "' AND `platform_id` not in ('" + "','".join(level_id_list) + "')" 
#     platform_id_number = cur_dev1.execute(stringSQL)
#     print "There are " + str(platform_id_number) + " platforms on timestamp " + str(regression_date)
#     print "Doing regression analysis..."
#     key_number = len(key_list)
#     for field_values in cur_dev1.fetchall():
#         field_values = list(field_values)
#         platform_whole_id_list.append(field_values[0])
#         platform_whole_name_list.append(field_values[1])
#         for i in range(2,key_number):
#             if None == field_values[i]:
#                 field_values[i] = 0
#         X_test.append(field_values[2:])
#     prediction_test = regressor.predict(StandardScaler().fit_transform(np.array(X_test)))
#     #从Y表找到每个平台的status，找不到的记为1
#     platform_number = len(platform_whole_id_list)
#     y = [1.0] * platform_number
#     for i in range(platform_number):
#         platform_id = platform_whole_id_list[i]
#         stringSQL = "SELECT `status` FROM " + srcdb_T + " WHERE `platform_id` = '" + str(platform_id) + "' AND `date` = '" +str(regression_date) + "'"
#         have_data = cur_dev1.execute(stringSQL)
#         if have_data != 0:
#             y[i] = cur_dev1.fetchone()[0]
#     #写入数据库
#     key_list = ["platform_id", "platform_name","date"] + field_list + ["status_true", "status_predict" ,"score"]
#     for i in range(len(X_test)):
#         value_list = [platform_whole_id_list[i], platform_whole_name_list[i], str(regression_date)]
#         for field_temp in X_test[i]:
#             value_list.append(str(field_temp))
#         stringSQL = "SELECT score FROM " + srcdb_H + " WHERE `date` = '" + str(regression_date) + "' AND `platform_id` ='" + str(platform_whole_id_list[i]) + "'"
#         row_number = cur_dev1.execute(stringSQL)
#         score = 0 if row_number == 0 else float(cur_dev1.fetchone()[0])
#         value_list = value_list + [str(y[i]), str(prediction_test[i]), str(score)]
#         stringSQL = "INSERT INTO " + dstdb_whole + "(`" + "`,`".join(key_list) + "`) VALUES('" + "','".join(value_list) + "')"
#         cur_dev1.execute(stringSQL)
#         conn_dev.commit()
#     print X_test[280]
#     test_norm = StandardScaler().fit_transform(np.array(X_test))[280]
#     print test_norm.tolist()
#     prediction_test = regressor.predict(test_norm)
#     print prediction_test
    closeCursors(cur_dev1, cur_db1)
    closeConns(conn_dev,conn_db)
    print ""
    print "finished"
    _end_time = time.time()
    print "The whole clean program costs " + str(_end_time - _start_time) + " seconds."  