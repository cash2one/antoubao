#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import pylab as pl

from sklearn.preprocessing import StandardScaler
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression

from elm import ELMRegressor
from random_hidden_layer import SimpleRandomHiddenLayer
from sklearn.metrics import r2_score
        

#构造数据集
def make_datasets():
    attribute_list = [[1.,1.,1.],[2.,2.,2.],[3.,3.,3.],[4.,40.,200.],[4.,40.,400.]]
    score_list = [0.3,0.6,0.9,1.0,1.1]
    attribute_list = [[1.,1.,1.],[2.,2.,2.],[3.,3.,3.],[4.,40.,200.],[1.,1.,1.],[2.,2.,2.],[3.,3.,3.],[4.,40.,200.]]
    score_list = [0,1,0,1,5,2,1,1] ####有问题！！
    return [(attribute_list, score_list)]

#返回方法以及对应的elm模式
def make_regressors():
    nh = 10
    names = ["ELM(10,tanh,LR)"]
    srhl_tanh = SimpleRandomHiddenLayer(n_hidden=nh,
                                        activation_func='tanh',
                                        random_state=0)
    log_reg = LogisticRegression()
    classifiers = [ELMRegressor(srhl_tanh, regressor=log_reg)]
    return names, classifiers

###############################################################################

#得到数据集（坐标x, y和标签）
datasets = make_datasets()
#初始化模型参数，隐藏节点个数 + 激活函数（elm）
names, regressors = make_regressors()
print names, regressors
#开始回归计算, X特征集合，y标签
for X, y in datasets: 
    #归一化
    X = StandardScaler().fit_transform(X)
    #划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.4, random_state=5)
    print type(X_train)
    # 迭代回归方法
    for name, clf in zip(names, regressors):
        #训练数据
        clf.fit(X_train, y_train)
        #预测得分
        predictions =  clf.predict(X_test)
        print predictions
        #虚拟判定系数pseudo-R2
        r2 = r2_score(y_test, predictions)
        print r2
