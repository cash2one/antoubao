#!/usr/bin/python
#coding=utf-8
import time
from atbtools.header import *
from atbtools.mysqlTools import *
from atbtools.computeTools import *


if __name__ == '__main__':
    _start_time = time.time()
    
    #获取连接
    conn_ddpt_data=MySQLdb.connect(host=DDPT_DATAHOST_OUT, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT) 
    cur_ddpt_data=getCursors(conn_ddpt_data)
    conn_dev=MySQLdb.connect(host=DEVHOST_OUT, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT) 
    cur_dev=getCursors(conn_dev)
    initializeCursors(cur_ddpt_data, cur_dev)
    
    SRCDB_V = "V_view"
    SRCDB_E2 = "E2_quantitative_data"
    
    #从E2表获取整个ave_annualized_return的信息
    aar_dict = {}
    stringSQL = "SELECT `date`, `platform_name`, `ave_annualized_return` FROM " + SRCDB_E2
    cur_dev.execute(stringSQL)
    for date, platform_name, ave_annualized_return in cur_dev.fetchall():
        if platform_name == "前海理想金融":
            platform_name = "前海理想"
        if platform_name == "凤凰金融（江西）":
            platform_name = "江西凤凰"
        if platform_name == "汇盈金服(汇盈贷)":
            platform_name = "汇盈金服"
        if platform_name not in aar_dict:
            aar_dict[platform_name] = {}
        if date not in aar_dict[platform_name]:
            aar_dict[platform_name][date] = 0
        aar_dict[platform_name][date] = ave_annualized_return
        
    date_list = getDifferentFieldlist(SRCDB_V, cur_ddpt_data, "date")
    for date in date_list :
        #获得当周总平台数
        stringSQL = "SELECT * FROM " + SRCDB_V + " WHERE `date` = '" + str(date) + "'"
        platform_number_sum = cur_ddpt_data.execute(stringSQL)
        
        #先确定每一周B++中分数最高的坏站（注意一定是本周坏的站，否则+500分没有意义），取它的分数+500之前的站作为集合，如果B++没有本周的坏站，则直接取B++及之前所有的站
        stringSQL = "SELECT `score` FROM " + SRCDB_V + " WHERE `date` = '" + str(date) + "' AND `level` = 'B++' AND `old_date` IS NULL AND `status` < 0.89 ORDER BY `score` DESC LIMIT 1"
        ret = cur_ddpt_data.execute(stringSQL)
        if ret == 0:
            stringSQL = "SELECT `score` FROM " + SRCDB_V + " WHERE `date` = '" + str(date) + "' AND `level` = 'B++' AND `status` > 0.89 ORDER BY `score` ASC LIMIT 1"
            cur_ddpt_data.execute(stringSQL)
            min_score = cur_ddpt_data.fetchone()[0]
        else:
            min_score = cur_ddpt_data.fetchone()[0] + 500
            
        stringSQL = "SELECT `platform_name`, `old_date`, `rank_score`, `level` FROM " + SRCDB_V + " WHERE `date` = '" + str(date) + "' AND `status` > '0.89' AND `score` >= '" + str(min_score) + "' ORDER BY `rank_score` DESC"
        count = cur_ddpt_data.execute(stringSQL)
        rank_score_sum = 0
        aar_rank_score_product = 0
        rank_score_list = []
        aar_rank_score_product_list = []
        r_max = 0
        for platform_name, old_date, rank_score, level in cur_ddpt_data.fetchall():
            if level not in ["A++", "A+", "A", "B++"]:
                print "数据集中存在等级在B++以下的站："
                print date, platform_name, rank_score, level
                exit(0)
            
            #如果该好站是补数，那么用所补的数据来代替
            date_real = date
            if None != old_date:
                date_real = old_date
            if date_real in aar_dict[platform_name]:
                rank_score_list.append(rank_score)
                aar_rank_score_product_list.append(aar_dict[platform_name][date_real] * rank_score)
                r_max += 1
        aar_rank_ave_list = []
        for i in range(r_max):
            aar_rank_ave_list.append(float(sum(aar_rank_score_product_list[i:r_max])) / sum(rank_score_list[i:r_max]))
            if i == 0 :
                ave_return = aar_rank_ave_list[0]
            elif aar_rank_ave_list[i] > aar_rank_ave_list[i-1]:
                r = r_max - i
                ave_return = aar_rank_ave_list[i]
                break
        _str = "date = " + str(date) + "    sum = " + str(platform_number_sum) + "    r_max = " + str(r_max) + "    r = " + str(r) + "    ratio = " + "%.2f" % (100 * float(r) / platform_number_sum) + "%    ave_return = " + "%.2f" % ave_return + "%\n"
        print _str
            
    closeCursors(cur_dev, cur_ddpt_data)
    closeConns(conn_dev, conn_ddpt_data)
    _end_time = time.time()
    print "The whole program costs " + str(_end_time - _start_time) + " seconds." 