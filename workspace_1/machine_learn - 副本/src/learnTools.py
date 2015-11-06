#!/usr/bin/python
# -*- coding: utf-8 -*-
#从H表找到得分前30的好站（时间为真实时间），从Y表和E2表中得到所有的坏站id，然后从Y表得到status和出事时间的前两周），然后从E2表中得到响应时间所有这些站的数据，最后进行神经网络回归计算
#得到回归模型后，对H表中score不为零的站进行预测（数据来源为E2）

import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from elm import ELMRegressor
from random_hidden_layer import SimpleRandomHiddenLayer,RBFRandomHiddenLayer
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
    #print "经过调整，有" + str(len(good_index_list)) + "个status在" + str(threshold) + "以上的好站以及剩下的" + str(len(bad_index_list)) + "个坏站."
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
    X_test = selectByIndexlist(X,test_index_list)
    X_train = selectByIndexlist(X,train_index_list)
    y_test = selectByIndexlist(y,test_index_list)
    y_train = selectByIndexlist(y,train_index_list)
    name_test = selectByIndexlist(np.array(name_list),test_index_list).tolist()
    name_train = selectByIndexlist(np.array(name_list),train_index_list).tolist()
    return X, y, X_train, y_train, name_train, X_test, y_test, name_test 

#返回ELM模式，func表示回归器函数类型，nh表示隐藏节点个数，rs表示随机数的选取方法，如果是零的化返回内置随机数（每次运行结果一致）, dorc表示希望结果是分类的还是连续的，以c开头表示连续，以d开头表示分类
def make_regressor(func, nh, rs, dorc = "continuous", _gamma = 0.1):
    if func == "rbf":
        srhl = RBFRandomHiddenLayer(n_hidden=nh*2, gamma=_gamma, random_state=rs)
    else:
        srhl = SimpleRandomHiddenLayer(n_hidden=nh,
                                        activation_func=func,
                                        random_state = rs)
    if dorc.lower().startswith("c"): 
        return ELMRegressor(srhl)
    elif dorc.lower().startswith("d"): 
        return ELMRegressor(srhl, regressor=LogisticRegression())
    else:
        print "The dorc parameter is wrong, it should start with 'c' or 'd'."
        exit(0)

if __name__ == '__main__':
    a = {1:{"a":[1,2,0]},2:{"a":[1,2,0]},3:{"a":[1,2,3]}}
    print getDictAverage(a, "a")