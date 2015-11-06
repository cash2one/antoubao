# /usr/bin/python
# encoding=utf8
# 从project_info、Table_01至Table_05中读取数据并合并表F创建Table_06

import sys
from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from atbtools.paymentTools import *
from atbtools.xmlTools import *
from math import floor
import hashlib
import time

if __name__ == '__main__':
    ## 1.预设值处理
    _start_time = time.time()
    isreset = 0
    if (len(sys.argv) == 2):
        if (sys.argv[1] == "reset"):
            isreset = 1
    # 确定金钱的误差0.01元
    money_error = 0.01 / MONEYUNIT
    #钱数保留几位小数（精确到分）
    money_format = "%." + str(len("%d"%(MONEYUNIT / 0.01))-1) + "f"
    # 获取连接    
    srcdb_info = "project_info_clean"
    srcdb_F = "platform_qualitative_F"
    TABLE_01 = "Table_01_investor_history"
    TABLE_02 = "Table_02_investor_current"
    TABLE_03 = "Table_03_borrower_history"
    TABLE_04 = "Table_04_borrower_current"
    TABLE_05 = "Table_05_pending_bill"
    TABLE_06 = "Table_06_parameter_quantitative"
    
    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    (cur_db1, cur_db2) = getCursors(conn_db,2)
    initializeCursors(cur_db1, cur_db2)
    
    #从文件中获得老站platform_id
    platform_id_old_list = getPlatformIdList("old_platform_id.txt") #做增量
    
    # 指定查询时间
    stringSQL = "SELECT DISTINCT date FROM " + srcdb_info
    cur_db1.execute(stringSQL)
    date_list = []
    for _date in cur_db1.fetchall():
        date_list.append(int(_date[0]))
    dates_number = len(date_list)
    if isreset == 1:
        start = 0        
    else:
        start = dates_number - 1
    initial_date = date_list[start]
    end_data = date_list[-1]
        
    ## 2.获得原数据并进一步加工
    #从project_info_clean中读取标的信息
    platforms_bids = {}  # 网站对应的标列表
    #0.获取所有平台最早数据时间
    platform_start_time_dict = {}
    stringSQL = "SELECT DISTINCT site_id, MIN(date) FROM " + srcdb_info + " GROUP BY site_id" 
    cur_db1.execute(stringSQL)
    for site_id, _date in cur_db1.fetchall(): 
        platform_start_time_dict[str(site_id)] = int(_date)

    #1. 获取所有的标
    stringSQL = "SELECT id, date, site_id, borrowing_amount, loan_period, annulized_rating, release_time, end_time FROM " + srcdb_info + " WHERE `date` >= '" + str(initial_date) + "'" 
    stringSQL = stringSQL + " AND `site_id` in ('" + "','".join(platform_id_old_list) + "')"
    #stringSQL = stringSQL + " AND `id` < '500'"
    print stringSQL
    print "正在从数据库传输数据回本地..."
    bidNumber = cur_db1.execute(stringSQL)
    _end_time = time.time()
    print "The query program costs " + str(_end_time - _start_time) + " seconds."                         
    # 预处理
    _start_time = time.time()
    for _id, _date, platform_id, borrowing_amount, loan_period, annulized_rating, release_time, end_time in cur_db1.fetchall():
        if platform_id not in platforms_bids:
            platforms_bids[platform_id] = {}
        total_gross = float(str(borrowing_amount).replace(",", ""))  # 防止出现2,000.00的情况
        platforms_bids[platform_id][_id] = {}
        bidTemp =  platforms_bids[platform_id][_id]
        bidTemp["release_time"] = int(release_time)
        bidTemp["end_time"] = int(end_time)
        bidTemp["date"] = int(_date)
        bidTemp["borrowing_amount"] = float(total_gross)
        bidTemp["loan_period"] = int(loan_period)
        bidTemp["annulized_rating"] = float(annulized_rating)
    #2. 获得每个网站、时间节点的性质
    bid_v={}
    for platform_id in platforms_bids:
        bid_v[platform_id]={}
        for _date in date_list:
            bid_v[platform_id][_date] = {}
            bid_v[platform_id][_date]["bid_sum"] = 0
            bid_v[platform_id][_date]["weekly_loan_period"] = 0
            bid_v[platform_id][_date]["ave_annualized_return"] = 0
            bid_v[platform_id][_date]["close_time_list"] = []
        for bid_id in platforms_bids[platform_id]:
            bidTemp = platforms_bids[platform_id][bid_id]
            release_time = bidTemp["release_time"]
            end_time = bidTemp["end_time"]
            _date = bidTemp["date"]  
            bid_v[platform_id][_date]["bid_sum"] += 1
            bid_v[platform_id][_date]["weekly_loan_period"] += float(bidTemp["loan_period"]) * bidTemp["borrowing_amount"]
            bid_v[platform_id][_date]["ave_annualized_return"] += bidTemp["annulized_rating"] * bidTemp["borrowing_amount"]
            bid_v[platform_id][_date]["close_time_list"].append(end_time - release_time)
    platform_id_list = platforms_bids.keys()
    _end_time = time.time()
    print "The pre_treatment program costs " + str(_end_time - _start_time) + " seconds."                         
    _start_time = time.time()
    #设定字段属性
    E1_key_dict = {}
    E1_key_dict["L"] = {}
    E1_key_dict["X"] = {}
    E1_key_dict["L"]["initial"] = ["weekly_total_investor", "weekly_lending", "weekly_total_borrower", "weekly_loan_period", "ave_annualized_return", "future4week_maturity", "cash_flow_in", "weekly_outstanding_loan", "investor_HHI", "borrower_HHI", "weekly_ave_lending_per_bid", "weekly_ave_bid_close_time", "weekly_new_investor", "provision_of_risk", "weekly_ave_investment_old", "top5_ratio_loan", "top10_ratio_loan", "weekly_ave_lending_per_borrower", "weekly_ave_investment", "weekly_ratio_new_old", "borrower_growth", "investor_growth", "latest4week_lending", "outstanding_loan", "turnover_registered", "not_returned_yet", "money_growth", "turnover_period", "short_term_debt_ratio", "market_share_growth"]
    E1_key_dict["X"]["initial"] = ["platform_name", "Compensation", "third_entrust", "technical_security", "customer_service", "third_assurance", "financial_transparency", "overdue_transparency", "borrower_transparency", "PR_transparency1", "PR_transparency2", "debt_transfer", "real_name", "vc_cap_usd", "registered_cap"]
    E1_key_dict["X"]["middle"] = ["parent_company_cap", "provision_of_risk1", "provision_of_risk2" ]  # 中间变量
    E1_key_inF_list = E1_key_dict["X"]["initial"] + E1_key_dict["X"]["middle"]
    E1_key_L_list = E1_key_dict["L"]["initial"]
    E1_key_inF_number = len(E1_key_inF_list)
    E1_key_inE1_list = E1_key_dict["L"]["initial"] + E1_key_dict["X"]["initial"]
    platform_id_md5_dict = {}
    neglect_field_list = [] #不写入的字段
    v={}
    if isreset == 1:  
        print "Reset '" + TABLE_06 + "'"
        cur_db1.execute("TRUNCATE " + TABLE_06)
        conn_db.commit()
        time.sleep(MAXWAITINGTIME) #防止mysql数据库的延时
    else:
        print "Update '" + TABLE_06 + "'" 
        stringSQL = "DELETE FROM " + TABLE_06 +" WHERE `date` = '"+str(date_list[-1])+"'"
        cur_db1.execute(stringSQL)
        conn_db.commit()
    counter = 0
    platform_number = len(platform_id_list)
    bidsPercentList = [floor(float(x) * platform_number * dates_number / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)] 

    for platform_id in platform_id_list:
        print platform_id
        for i in range(E1_key_inF_number):
            v[E1_key_inF_list[i]] = 0
        #先获得定性字段
        stringSQL = "SELECT " + ",".join(E1_key_inF_list) + " FROM " + srcdb_F + " WHERE `platform_id` = '" + str(platform_id) + "'"
        row_number = cur_db1.execute(stringSQL)
        if row_number == 0:
            print "The " + srcdb_F + " table has no platform_id called " + platform_id
            v["platform_name"] = platform_id
        else:
            row = cur_db1.fetchone()
            for i in range(0, E1_key_inF_number):
                v[E1_key_inF_list[i]] = 0 if None == row[i] else row[i] #为避免出现truncate数据的情况，这里全置于0
        v["vc_cap_usd"] *= 6 * 0.8
        v["registered_cap"] += 0.1 * v["parent_company_cap"]
        platform_id_md5 = hashlib.md5(v["platform_name"]).hexdigest()[0:10]
        platform_id_md5_dict[platform_id] = platform_id_md5
        #再获得定量字段
        having_date = [0] * (dates_number - start)
        operating = [0] * (dates_number - start)
        for i in range(start, dates_number):
            counter += 1
            if counter in bidsPercentList:
                print "updating: " + str((1 + bidsPercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
            for j in range(len(E1_key_L_list)):
                v[E1_key_L_list[j]] = WRONGNUMBER #设置初始值
            _date = date_list[i]
            #通过sql语句获得相应的字段
            #1 weekly_total_borrower
            stringSQL = "SELECT count(*) FROM " + TABLE_04 + " WHERE `platform_id` = '" + str(platform_id) + "' AND `date` = '" + str(_date) + "'"
            row_number = cur_db1.execute(stringSQL)
            weekly_total_borrower = cur_db1.fetchone()[0]
            v["weekly_total_borrower"] = int(weekly_total_borrower)
            if v["weekly_total_borrower"] != 0:
                operating[i] = 1 #以是否有借款人作为平台的初始营业时间
            if 1 not in operating:
                continue
            #2.weekly_total_investor, 3.weekly_lending
            stringSQL = "SELECT count(*), sum(week_amount) FROM " + TABLE_02 + " WHERE `platform_id` = '" + str(platform_id) + "' AND `date` = '" + str(_date) + "'"
            row_number = cur_db1.execute(stringSQL)
            (weekly_total_investor,weekly_lending) = cur_db1.fetchone()
            if weekly_total_investor != 0:
                v["weekly_total_investor"] = int(weekly_total_investor)
                v["weekly_lending"] = float(weekly_lending)
            #4.weekly_new_investor
            stringSQL = "SELECT count(*), sum(week_amount) FROM " + TABLE_02 + " WHERE `platform_id` = '" + str(platform_id) + "' AND `date` = '" + str(_date) + "' AND `tag_new_old` = 'new'"
            row_number = cur_db1.execute(stringSQL)
            (weekly_new_investor,weekly_lending_new) = cur_db1.fetchone()
            if weekly_new_investor == 0:
                weekly_lending_new = 0
            v["weekly_new_investor"] = int(weekly_new_investor)
            #5.investor_HHI
            weeklyInvestList = []
            stringSQL = "SELECT week_amount FROM " + TABLE_02 + " WHERE `platform_id` = '" + str(platform_id) + "' AND `date` = '" + str(_date) +"'"
            row_number = cur_db1.execute(stringSQL)
            if row_number != 0:
                for week_amount in cur_db1.fetchall():
                    week_amount = float(week_amount[0])
                    if None != week_amount and week_amount >= money_error:
                        weeklyInvestList.append(week_amount)
                v["investor_HHI"] = getHHI(weeklyInvestList)
            #6.borrower_HHI
            weeklyInvestList = []
            stringSQL = "SELECT week_amount FROM " + TABLE_04 + " WHERE `platform_id` = '" + str(platform_id) + "' AND `date` = '" + str(_date)+ "'"
            row_number = cur_db1.execute(stringSQL)
            if row_number != 0:
                for week_amount in cur_db1.fetchall():
                    week_amount = float(week_amount[0])
                    if None != week_amount and week_amount >= money_error:
                        weeklyInvestList.append(week_amount)
                v["borrower_HHI"] = getHHI(weeklyInvestList)
            #7.weekly_outstanding_loan
            stringSQL = "SELECT sum(amount) FROM " + TABLE_05 + " WHERE `platform_id` = '" + str(platform_id) + "' AND `date` > '" + str(_date) + "'"
            row_number = cur_db1.execute(stringSQL)
            weekly_outstanding_loan = cur_db1.fetchone()[0]
            if None != weekly_outstanding_loan:
                v["weekly_outstanding_loan"] = float(weekly_outstanding_loan)
            #8.future4week_maturity
            stringSQL = "SELECT sum(amount) FROM " + TABLE_05 + " WHERE `platform_id` = '" + str(platform_id) + "' AND `date` > '" + str(_date) + "' AND `date` <= '" + str(_date + FUTUREPAYBACKWEEKS * SECONDSPERWEEK) + "'"
            row_number = cur_db1.execute(stringSQL)
            future4week_maturity = cur_db1.fetchone()[0]
            if None != future4week_maturity:
                v["future4week_maturity"] = float(future4week_maturity)
            #9.latest4week_lending，和过去有关
            k = 0
            for j in range(0, i)[::-1]:
                stringSQL = "SELECT sum(week_amount) FROM " + TABLE_04 + " WHERE `platform_id` = '" + str(platform_id) + "' AND `date` = '" + str(date_list[j]) + "'"
                ret = cur_db1.execute(stringSQL)
                weekly_lending = float(cur_db1.fetchone()[0])
                if weekly_lending != 0:
                    k += 1 
                    v["latest4week_lending"] += weekly_lending
                    if k == LASTLENDINGWEEKS:
                        break
            #10.borrower_growth，和过去有关
            for j in range(0, i-LASTLENDINGWEEKS+1)[::-1]:
                stringSQL = "SELECT count(*) FROM " + TABLE_04 + " WHERE `platform_id` = '" + str(platform_id) + "' AND `date` = '" + str(date_list[j]) + "'"
                ret = cur_db1.execute(stringSQL)
                weekly_total_borrower_old = int(cur_db1.fetchone()[0])
                if weekly_total_borrower_old != 0:
                    v["borrower_growth"] = float(v["weekly_total_borrower"]) / weekly_total_borrower_old
                    break
            #11.investor_growth，和过去有关
            for j in range(0, i-LASTLENDINGWEEKS+1)[::-1]:
                stringSQL = "SELECT count(*) FROM " + TABLE_02 + " WHERE `platform_id` = '" + str(platform_id) + "' AND `date` = '" + str(date_list[j]) + "'"
                ret = cur_db1.execute(stringSQL)
                weekly_total_investor_old = int(cur_db1.fetchone()[0])
                if weekly_total_investor_old != 0:
                    v["investor_growth"] = float(v["weekly_total_investor"]) / weekly_total_investor_old
                    break
            #其他一些计算属性
            #weekly_lending分母
            multiple = 1 #人工干预weekly_outstanding_loan系数
            weekly_bid_sum = bid_v[platform_id][_date]["bid_sum"]
            if v["weekly_lending"] != 0:
                #12.weekly_loan_period
                v["weekly_loan_period"] = float(bid_v[platform_id][_date]["weekly_loan_period"]) / v["weekly_lending"] / MONEYUNIT
                #人工干预系数计算，通过weekly_loan_period来计算
                passed_week = (_date - platform_start_time_dict[platform_id]) / SECONDSPERWEEK + 1
                weekly_loan_period_week = int(v["weekly_loan_period"] / DAYSPERWEEK) 
                if passed_week < weekly_loan_period_week:
                    manual_handling_tag_list = 1
                    multiple = float(weekly_loan_period_week) / passed_week
                v["ave_annualized_return"] = bid_v[platform_id][_date]["ave_annualized_return"] / v["weekly_lending"] / MONEYUNIT
                #13. cash_flow_in
                stringSQL = "SELECT amount FROM " + TABLE_05 + " WHERE `platform_id` = '" + str(platform_id) + "' AND `date` = '" + str(_date) + "'"
                row_number = cur_db1.execute(stringSQL)
                if row_number != 0:
                    weekly_pending = cur_db1.fetchone()[0]
                    v["cash_flow_in"] = (v["weekly_lending"] - float(weekly_pending)) / v["weekly_lending"]
                if weekly_bid_sum != 0:
                    #14.weekly_ave_bid_close_time, 15.weekly_ave_lending_per_bid
                    v["weekly_ave_bid_close_time"] = getCenterSum(bid_v[platform_id][_date]["close_time_list"]) / weekly_bid_sum / v["weekly_lending"]
                    v["weekly_ave_lending_per_bid"] = v["weekly_lending"] / weekly_bid_sum * MONEYUNIT
            #future4week_maturity分母
            if v["future4week_maturity"] != 0:
                v["future4week_maturity"] *= multiple
                #16. not_returned_yet
                v["not_returned_yet"] = v["latest4week_lending"] / v["future4week_maturity"]    
            #weekly_outstanding_loan分母
            if v["weekly_outstanding_loan"] != 0:
                #17.top10_ratio_loan
                stringSQL = "SELECT SUM(pending_amount) FROM (SELECT pending_amount FROM " + TABLE_03 + " WHERE `platform_id` = '" + str(platform_id) + "' ORDER BY pending_amount DESC LIMIT 10) Top_temp"
                row_number = cur_db1.execute(stringSQL)
                top_10 = float(cur_db1.fetchone()[0])
                v["top10_ratio_loan"] = top_10 / v["weekly_outstanding_loan"]
                #18.top5_ratio_loan
                stringSQL = "SELECT SUM(pending_amount) FROM (SELECT pending_amount FROM " + TABLE_03 + " WHERE `platform_id` = '" + str(platform_id) + "' ORDER BY pending_amount DESC LIMIT 5) Top_temp"
                row_number = cur_db1.execute(stringSQL)
                top_5 = float(cur_db1.fetchone()[0])
                v["top5_ratio_loan"] = top_5 / v["weekly_outstanding_loan"]
                v["weekly_outstanding_loan"] *= multiple
                #19.outstanding_loan, 20.short_term_debt_ratio, 21.turnover_registered
                v["outstanding_loan"] = v["latest4week_lending"] / v["weekly_outstanding_loan"]
                v["short_term_debt_ratio"] = v["future4week_maturity"] / v["weekly_outstanding_loan"]
                v["turnover_registered"] = (v["vc_cap_usd"] + v["registered_cap"]) / v["weekly_outstanding_loan"]
            #latest4week_lending分母 
            if v["weekly_loan_period"] * v["latest4week_lending"] != 0:
                #22.money_growth
                v["money_growth"] = (v["future4week_maturity"] / v["latest4week_lending"]) ** (1 / v["weekly_loan_period"])  
            
            #23.weekly_ave_investment
            if v["weekly_total_investor"] != 0:
                v["weekly_ave_investment"] = v["weekly_lending"] / v["weekly_total_investor"]
            #24.weekly_ave_investment_old, 25.weekly_ratio_new_old
            weekly_old_investor = v["weekly_total_investor"] - v["weekly_new_investor"]
            if weekly_old_investor != 0:
                v["weekly_ratio_new_old"] = float(v["weekly_new_investor"]) / weekly_old_investor
                v["weekly_ave_investment_old"] = (v["weekly_lending"] - weekly_lending_new) / weekly_old_investor
            #26.weekly_ave_lending_per_borrower
            if v["weekly_total_borrower"] != 0:
                v["weekly_ave_lending_per_borrower"] = v["weekly_lending"] / v["weekly_total_borrower"]
            weekly_ave_investment_per_bid = v["weekly_ave_lending_per_borrower"]
            #27.turnover_period
            v["turnover_period"] = v["weekly_lending"] * v["weekly_loan_period"] / MONTHSPERYEAR
            provision_of_risk_num = v["provision_of_risk1"] + v["provision_of_risk2"] * v["weekly_lending"] / 100
            
            if v["weekly_outstanding_loan"] > money_error:
                having_date[i] = 1    
            #插入T06表格，有数据才插入
            if 1 in operating and having_date[i] == 1: 
                key_str = ["date", "platform_id"]
                value_str = [str(_date), str(platform_id_md5)]
                for key in E1_key_inE1_list:
                    if key not in neglect_field_list:
                        key_str.append(str(key))
                        value_str.append(str(v[key]))
                stringSQL = "INSERT INTO " + TABLE_06 + "(`" + "`,`".join(key_str) + "`) VALUES('" + "','".join(value_str) + "')"
                cur_db1.execute(stringSQL)
                conn_db.commit()

    closeCursors(cur_db1, cur_db2)
    closeConns(conn_db)  
    print ""
    print "finished"
    _end_time = time.time()
    print "The 06 reset program costs " + str(_end_time - _start_time) + " seconds."
    
