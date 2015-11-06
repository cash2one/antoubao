# /usr/bin/python
# coding=utf8

#1.获得指数指标的时间节点
#2.在E1表中寻找所有非坏站并依据value进行排序

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pylab import *
import matplotlib
import numpy as np
import time

if __name__ == '__main__':
    _start_time = time.time()
    #获得连接        
    conn_dev = getConn(DEVHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_dev = getCursors(conn_dev)
    initializeCursors(cur_dev)
    
    SRCDB_INDEX = "index_weekly_report"
    
    #1.获得指数指标的时间节点
    date_list = getDifferentFieldlist(SRCDB_INDEX, cur_dev, "date")
    date_number =len(date_list)
    field_list = getAllColumnsFromTable(cur_dev, SRCDB_INDEX, del_list = ["Id","date"], merge_list = None)
    field_number = len(field_list)
    
    #获取所有数据
    field_dict = {}
    for field in field_list:
        field_dict[field] = []
    stringSQL = "SELECT `" + "`,`".join(field_list) + "` FROM " + SRCDB_INDEX + " ORDER BY date ASC"
    cur_dev.execute(stringSQL)
    for value_list in cur_dev.fetchall():
        for i in range(field_number):
            if None == value_list[i]:
                field_dict[field_list[i]].append(0)
            else:
                field_dict[field_list[i]].append(float(value_list[i]))
    print field_dict
    #exit(0)
    #画图
    for field in field_list:
    #for field in ["real_interest_rate"]:
        figure()
        plt.plot(np.array(range(date_number)), field_dict[field], '-o', ms=8, label = "Origin")
        matplotlib.rcParams["font.size"] = 20 #修改画图的默认值
        plt.xlabel("date")
        plt.ylabel("value")
        #plt.xlim(-0.5,weight_number+0.5)
        #plt.ylim(min(correct_proportion_min_list)-0.1,max(correct_proportion_max_list)+0.1)
        #plt.xticks(range(0,weight_number+1,5))
        #plt.yticks(fontsize = 20)
        _title = field
        plt.title(_title, fontsize = 20)
        #plt.legend(loc='lower right', numpoints = 1, scatterpoints = 1, fontsize = 15)  
        picture_name = "picture/" + field + ".png"
        plt.savefig(picture_name)
        close() 
     
    closeCursors(cur_dev)
    closeConns(conn_dev)  
    _end_time = time.time()
    print "The whole program costs " + str(_end_time - _start_time) + " seconds."  
    
