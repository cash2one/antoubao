# /usr/bin/python
# coding=utf8

#1.从y表中获得所有坏站（status < 1）的name和坏站时间，同时筛选出在坏站前2至5共4周有数据的坏站集合X
#2.选择在3月份第2周(1426348800)到4月份第1周(1428163200)这四周有数据的好站。
#3.从3sigma中找到阈值(只关心merge_list,同时值关心最大值)
#4.从人工表4sigma中找到阈值(只关心merge_list)
#5.组装好站和坏站，并从E2表获得属性值（如果某一个指标为零，则一直向前追溯至不为零的值），从T表获得score，从F表获得background，删除关键量为零的值，并且根据人工4sigma和3sigma阈值（只关心最大值）进行筛选

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
import time

if __name__ == '__main__':
    _start_time = time.time()
    conn_dev = getConn(DEVHOST, USERNAME, PASSWORD, DB, PORT)
    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_dev = getCursors(conn_dev)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_dev, cur_db)
    SRCDB_Y = "platform_problem_record_Y"   
    SRCDB_E2 = "platform_quantitative_data_E2"
    SRCDB_T = "platform_score_T"   
    SRCDB_F = "platform_qualitative_F"
    SRCDB_4sigma = "platform_quantitative_data_4sigma_test"
    SRCDB_3sigma = "platform_quantitative_data_3sigma_O"
    SRCDB_E2_ML = "platform_quantitative_data_E2_ML"
    
    #1.从y表中获得所有坏站（status < 1）的name和坏站时间，同时筛选出在坏站前2至5共4周有数据的坏站集合X    bad_status_list = [0, 0.3, 0.6]
    stringSQL = "SELECT DISTINCT platform_name , min(date), max(status) FROM " + SRCDB_Y
    #stringSQL = stringSQL + " WHERE " + status_str + " GROUP BY platform_name "
    stringSQL = stringSQL + " WHERE `status` < '1' GROUP BY platform_name"
    #print stringSQL
    bad_platform_dict_number = cur_db.execute(stringSQL)
    rets = cur_db.fetchall()
    bad_platform_list=[]
    for platform_name in rets:
        bad_platform_list.append(str(platform_name[0]))
    print "Y表内一共有" + str(bad_platform_dict_number) + "个坏站."
    bad_platform_dict = {}
    level_list = ["levelaplusplus", "levelaplus", "levela", "levelbplusplus", "levelbplus", "levelb", "levelc"]
    for platform_name, _date, status in rets:
        platform_name = str(platform_name)
        _date_end = getTimestampZero(int(_date), 0, 0) - (SHIFTWEEKS-1) * SECONDSPERWEEK #本身就是前一周的数据
        _date_start =  _date_end - (LASTWEEKS - 1) * SECONDSPERWEEK
        stringSQL = "SELECT * FROM " + SRCDB_E2 + " WHERE `date` <= " + str(_date_end) + " AND `date`  >= " + str(_date_start) + " AND `platform_name` = '" + platform_name + "'"
        ret = cur_dev.execute(stringSQL)
        if ret != 0:
            if platform_name not in level_list:
                bad_platform_dict[platform_name] = {}
                bad_platform_dict[platform_name]["status"] = float("%.1f " % float(status))
                bad_platform_dict[platform_name]["date_start"] = _date_start
                bad_platform_dict[platform_name]["date_end"] = _date_end
                bad_platform_dict[platform_name]["score"] = 0
                bad_platform_dict[platform_name]["background"] = 0
                bad_platform_dict[platform_name]["fields"] = []
    bad_platform_dict_number = len(bad_platform_dict)
    print "在提前" + str(SHIFTWEEKS) + "周到" + str(SHIFTWEEKS + LASTWEEKS - 1) + "周的条件下，有" + str(bad_platform_dict_number) + "个坏站有数据."

    #2.选择在3月份第2周(1426348800)到4月份第1周(1428163200)这四周有数据的好站。
    _date_start = 1426348800
    _date_end= 1428163200
    stringSQL = "SELECT DISTINCT platform_name FROM " + SRCDB_E2 + " WHERE `date` <= " + str(_date_end) + " AND `date`  >= " + str(_date_start)
    cur_dev.execute(stringSQL)
    good_platform_dict = {}
    del_list = list(set(bad_platform_list) | set(level_list))
    rets = cur_dev.fetchall()
    for platform_name in rets:
        platform_name = str(platform_name[0])
        if platform_name not in del_list :
            good_platform_dict[platform_name] = {}
            good_platform_dict[platform_name]["status"] = 1.0
            good_platform_dict[platform_name]["date_start"] = _date_start
            good_platform_dict[platform_name]["date_end"] = _date_end
            good_platform_dict[platform_name]["score"] = 0
            good_platform_dict[platform_name]["background"] = 0
            good_platform_dict[platform_name]["fields"] = []
    good_platform_dict_number = len(good_platform_dict)
    print "在3月份第2周到4月份第1周这个时间段内，共有" + str(good_platform_dict_number) + "个好站有数据."
    good_platform_list = good_platform_dict.keys()
    
    #3.从3sigma中找到阈值(只关心merge_list)
    #merge_list = ["weekly_total_borrower","weekly_total_investor","provision_of_risk","weekly_ave_lending_per_bid","outstanding_loan","weekly_ave_bid_close_time","top10_ratio_loan","top5_ratio_loan","top5_ratio_investment","top10_ratio_investment","not_returned_yet","investor_growth","market_share_growth","borrower_growth","PR_transparency1"]
    merge_simga3_list = ["weekly_total_borrower","weekly_total_investor","weekly_ave_lending_per_bid","outstanding_loan","weekly_ave_bid_close_time","top10_ratio_loan","top5_ratio_loan","not_returned_yet","investor_growth","market_share_growth","borrower_growth"]
    sigma3_dict = {}
    del_list = ["id", "date", "type"]
    sigma3_fields_list = getAllColumnsFromTable(cur_dev, SRCDB_3sigma, del_list, merge_simga3_list)
    sigma3_fields_number = len(sigma3_fields_list)
    sigma3_dates_list = getDifferentFieldlist(SRCDB_3sigma, cur_dev, "date")
    for field in sigma3_fields_list:
        sigma3_dict[field] = {}
        for _date in sigma3_dates_list:
            sigma3_dict[field][_date] = {}
            sigma3_dict[field][_date]["low"] = None
            sigma3_dict[field][_date]["high"] = None
    stringSQL = "SELECT `date`, `type`, `" + "`,`".join(sigma3_fields_list) + "` FROM " + SRCDB_3sigma
    cur_dev.execute(stringSQL)
    rets = cur_dev.fetchall()
    for _list in rets:
        for i in range(sigma3_fields_number):
            sigma3_dict[sigma3_fields_list[i]][_list[0]][_list[1]] = _list[i + 2]
    
    #4.从人工表4sigma中找到阈值(只关心merge_list)
    sigma4_dict = {}
    del_list = ["id", "type"]
    sigma4_fields_list = getAllColumnsFromTable(cur_dev, SRCDB_4sigma, del_list)
    sigma4_fields_number = len(sigma4_fields_list)
    for field in sigma4_fields_list:
        sigma4_dict[field] = {}
        sigma4_dict[field]["low"] = None
        sigma4_dict[field]["high"] = None
    stringSQL = "SELECT `type`, `" + "`,`".join(sigma4_fields_list) + "` FROM " + SRCDB_4sigma
    cur_dev.execute(stringSQL)
    rets = cur_dev.fetchall()
    for _list in rets:
        for i in range(sigma4_fields_number):
            sigma4_dict[sigma4_fields_list[i]][_list[0]] = _list[i + 1]
    
    #5.组装好站和坏站，并从E2表获得属性值，从T表获得score，从F表获得background，删除关键量为零的值，并且根据人工4sigma和3sigma阈值进行筛选
    cur_dev.execute("TRUNCATE " + SRCDB_E2_ML)
    conn_dev.commit()
    platform_dict=dict(bad_platform_dict, **good_platform_dict)
    bad_platform_list = bad_platform_dict.keys()
    good_platform_list = good_platform_dict.keys()
    platform_number = len(platform_dict)
    print "一共有" + str(platform_number) + "个站."
    merge_E2_list = ["platform_id","platform_name","date","weekly_lending","weekly_total_borrower","weekly_total_investor","weekly_new_investor","provision_of_risk","vc_cap_usd","registered_cap","turnover_registered","ave_annualized_return","weekly_loan_period","weekly_ave_lending_per_borrower","weekly_ave_lending_per_bid","weekly_ave_investment","weekly_ratio_new_old","outstanding_loan","weekly_ave_bid_close_time","weekly_ave_investment_old","turnover_period","top10_ratio_loan","top5_ratio_loan","top5_ratio_investment","top10_ratio_investment","not_returned_yet","cash_flow_in","short_term_debt_ratio","money_growth","investor_growth","market_share_growth","borrower_growth","PR_transparency1","background"]
    del_list = ["id"]
    fields_list = getAllColumnsFromTable(cur_dev, SRCDB_E2, del_list, merge_E2_list)
    fields_number = len(fields_list)
    print "一共有" + str(fields_number -3 + 1) + "个指标."
    del_list = ["weekly_lending", "registered_cap"]
    del_index_list = getIndexFromList(fields_list, del_list)
    sigma3_index_list = getIndexFromList(fields_list, sigma3_fields_list)
    sigma4_index_list = getIndexFromList(fields_list, sigma4_fields_list)
    print sigma3_index_list
    print sigma4_index_list
    #从E2表获取指标，从T表获取得分，从F表获取背景（国有，投资，银行）
    fp = open("threshold_wrong.txt","w")
    review_list = ["top10_ratio_loan", "top5_ratio_loan", "top5_ratio_investment", "top10_ratio_investment"]
    review_index_list = getIndexFromList(fields_list, review_list)
    for platform_name in platform_dict:
        print platform_name
        #F表中获取background
        stringSQL = "SELECT `listing`, `state_owned`, `bank` FROM " + SRCDB_F + " WHERE `platform_name`  = '" + str(platform_name) + "'"
        ret = cur_db.execute(stringSQL)
        if ret != 0:
            (listing, state_owned, bank) = cur_db.fetchone()
            _sum = int(listing) + int(state_owned) + int(bank)
            _sum = 0 if _sum == 0 else 1
            platform_dict[platform_name]["background"] = _sum
        date_start = platform_dict[platform_name]["date_start"]
        date_end = platform_dict[platform_name]["date_end"]
        dates_list = range(date_start, date_end + 1, SECONDSPERWEEK)
        dates_number = len(dates_list)
        for i in range(dates_number):
            _date = dates_list[i]
            platform_dict[platform_name]["fields"] = []
            platform_dict_fields = platform_dict[platform_name]["fields"]
            #E2中获取指标值（如果某一个指标为零，则一直向前追溯至不为零的值）
            stringSQL = "SELECT " + ','.join(fields_list) + " FROM " + SRCDB_E2 + " WHERE `date` = " + str(_date) + " AND `platform_name`  = '" + str(platform_name) + "'"
            ret = cur_dev.execute(stringSQL)
            if ret == 0:
                continue
            rets = list(cur_dev.fetchone())
            for j in range(fields_number):
                if None == rets[j]:
                    rets[j] = 0.0
                if j in review_index_list:
                    if rets[j] == 0: 
                        #print 1111, fields_list[j], rets[j]
                        #一直向上追溯
                        rets[j] = getLastNoneZero(cur_dev, SRCDB_E2, fields_list[j], platform_name, _date, 0.0)
                        if rets[j] == 0:
                            #一直向下追溯
                            rets[j] = getNewestNoneZero(cur_dev, SRCDB_E2, fields_list[j], platform_name, _date, 0.0)
                            #print 2222, fields_list[j], rets[j]
                platform_dict_fields.append(str(rets[j]))
            #删除关键量为0的对应量
            _insert = 1
            for k in del_index_list: 
                if float(platform_dict_fields[k]) == 0:
                    _insert = 0
                    break
            if _insert == 0:
                continue
            #T表得到score
            stringSQL = "SELECT score FROM " + SRCDB_T + " WHERE `date` = " + str(_date) + " AND `platform_name`  = '" + str(platform_name) + "'"
            ret = cur_dev.execute(stringSQL)
            if ret != 0:
                platform_dict[platform_name]["score"] = float(cur_dev.fetchone()[0])  
            #对好战数据进行筛选
            if platform_name in good_platform_list:
                #事先进行筛选
                for index in sigma3_index_list:
                    if float(platform_dict_fields[index]) == 0.0:
                        fp.write(platform_name + "(" + str(_date) + "): '" + fields_list[index] + "' = 0. \n") 
                        _insert = 0
                        break
                if _insert == 0:
                    continue
                #进行3sigma阈值筛选
                if _date in sigma3_dates_list:
                    for index in sigma3_index_list:
                        if index == -1:
                            continue
                        if float(platform_dict_fields[index]) == 0.0:
                            fp.write(platform_name + "(" + str(_date) + "): '" + fields_list[index] + "' = 0. \n") 
                            _insert = 0
                            break
                        else:
                            _insert = checkMax(platform_dict_fields[index], sigma3_dict[fields_list[index]][_date]["high"])
                            if _insert == 0 :
                                #fp.write(platform_name + "(" + str(_date) + "): '" + fields_list[index] + "'超过sigma3阈值————num: " + str(platform_dict_fields[index]) + ", min: " + str(sigma3_dict[fields_list[index]][_date]["low"]) + ", max: " + str(sigma3_dict[fields_list[index]][_date]["high"]) + "\n")
                                fp.write(platform_name + "(" + str(_date) + "): '" + fields_list[index] + "'超过sigma3最大值————num: " + str(platform_dict_fields[index]) + ", max: " + str(sigma3_dict[fields_list[index]][_date]["high"]) + "\n")
                                break
                if _insert == 0:
                    continue
                #进行4sigma阈值筛选  
                for index in sigma4_index_list:
                    if index == -1:
                        continue
                    _insert = checkThresholdValue(platform_dict_fields[index], sigma4_dict[fields_list[index]]["low"], sigma4_dict[fields_list[index]]["high"])
                    if _insert == 0 :
                        fp.write(platform_name + "(" + str(_date) + "): '" + fields_list[index] + "'超过sigma4阈值————num: " + str(platform_dict_fields[index]) + ", min: " + str(sigma4_dict[fields_list[index]]["low"]) + ", max: " + str(sigma4_dict[fields_list[index]]["high"]) + "\n")
                        break
                if _insert == 0:
                    continue
            #插入数据库
            key_list = fields_list + ["score", "background", "status", "order"]
            value_list = platform_dict_fields + [str(platform_dict[platform_name]["score"]), str(platform_dict[platform_name]["background"]), str(platform_dict[platform_name]["status"]), str(0-2-i)]
            stringSQL = "INSERT INTO " + SRCDB_E2_ML + "(`" + "`,`".join(key_list) + "`) VALUES('" + "','".join(value_list) + "')"
            cur_dev.execute(stringSQL)
            conn_dev.commit()
    fp.close() 
    closeCursors(cur_dev, cur_db)
    closeConns(conn_dev, conn_db)  
    _end_time = time.time()
    print "The whole program costs " + str(_end_time - _start_time) + " seconds."  
    
