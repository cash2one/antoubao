# /usr/bin/python
# encoding=utf8
# 从project_info_clean中读取全部数据并创建Table_01和Table_03

import sys
from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from atbtools.paymentTools import *
from atbtools.xmlTools import *
from math import floor
import time

if __name__ == '__main__':
    ## 1.预设值处理
    _start_time = time.time()
    #利率的最大值
    annulized_rating_max = 30.0
    # 确定金钱的误差0.01元
    money_error = 0.01 / MONEYUNIT
    #钱数保留几位小数（精确到分）
    money_format = "%." + str(len("%d"%(MONEYUNIT / 0.01))-1) + "f"
    #判断是增量还是全量
    isreset = 0
    if (len(sys.argv) == 2):
        if (sys.argv[1] == "reset"):
            isreset = 1
    # 获取连接    
    srcdb_info = "project_info_clean"
    TABLE_01 = "Table_01_investor_history"
    TABLE_03 = "Table_03_borrower_history"

    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    (cur_db1, cur_db2) = getCursors(conn_db,2)
    initializeCursors(cur_db1, cur_db2)
    
    #从文件中获得老站platform_id
    platform_id_old_list = getPlatformIdList("old_platform_id.txt") #做增量
    
    # 指定查询时间
    stringSQL = "SELECT DISTINCT date FROM "+srcdb_info+" ORDER BY date ASC"
    cur_db1.execute(stringSQL)
    date_list = []
    for _date in cur_db1.fetchall():
        date_list.append(int(_date[0]))
    if isreset == 1:
        initial_date = min(date_list)
    else:
        initial_date = max(date_list)
    end_date = max(date_list)
    
    ## 2.获得原数据并进一步加工
    # 获取母表的全部信息        
    stringSQL = "SELECT id, date, site_id, borrower, borrowing_amount, loan_period, annulized_rating, payment_method, investor, release_time, end_time FROM " + srcdb_info + " WHERE CAST(`end_time` + `loan_period` as SIGNED)  >= '" + str(initial_date) + "'"   
    stringSQL = stringSQL + " AND `site_id` in ('" + "','".join(platform_id_old_list) + "')"
    #stringSQL = stringSQL + " AND `id` < '500'"
    print stringSQL
    print "正在从数据库传输数据回本地..."
    bidNumber = cur_db1.execute(stringSQL)
    bidsPercentList = [floor(float(x) * bidNumber / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)] 
    rows = cur_db1.fetchall()
    _end_time = time.time()
    print "The query program costs " + str(_end_time - _start_time) + " seconds."                         
    # 预处理
    _start_time = time.time()
    print "Query project_info(" + str(bidNumber) + ")"
    platforms = set()  # 网站名称
    platforms_investors = {}  # 网站对应的投资人列表
    platforms_borrowers = {}  # 网站对应的借款人列表
    platforms_bids = {}  # 网站对应的标列表
    platforms_names = {}  # 网站的name对应列表
    investorNumber = 0
    borrowerNumber = 0
    bidNumber = 0
    counter = 0
    # 组装所有数据
    for _id, _date, platform_id, borrower, borrowing_amount, loan_period, annulized_rating, payment_method, investorStr, release_time, end_time in rows:
        if counter in bidsPercentList:
            print "querying: " + str((1 + bidsPercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
        annulized_rating = float(annulized_rating) / 100
        #只考虑还款利率在一定范围内的
        if annulized_rating > annulized_rating_max / 100:
            continue
        release_time = int(release_time)
        end_time = int(end_time)
        loan_period = int(loan_period)
        borrowing_amount = borrowing_amount / MONEYUNIT
        _date = int(_date)
        # 获得且清理项目的计息日期
        interest_date = getInterestDate(end_date, borrowing_amount, borrowing_amount, investorStr)[1]
        # 如果有新网站的话增加新网站
        if platform_id not in platforms:
            platforms.add(platform_id)
            platforms_investors[platform_id] = {}
            platforms_borrowers[platform_id] = {}
        # 获得该投资项目在不同时间的收益率，只要是一个投资项目，所有投资人在同一时刻的收益率都是一定的
        totalRatio = getPayback(0, end_date, loan_period, annulized_rating, payment_method)
        paybackRatio = getPayback(interest_date, end_date, loan_period, annulized_rating, payment_method)            
        # 组装投资人信息
        investorArr = investorStr.split("|")
        for i in range(0, len(investorArr) - 1):
            if i % 3 == 1 :
                investor = investorArr[i]
                investorDate = int(investorArr[i - 1])
                try: 
                    total_gross = float(investorArr[i + 1].replace(",", "")) / MONEYUNIT  # 防止出现2,000.00的情况
                except:
                    total_gross = 0
                if total_gross < money_error:
                    continue
                investorPending = total_gross * (totalRatio - paybackRatio)
                if investor not in platforms_investors[platform_id]:
                    # 投资人信息：[待收款，总投资额，最早入市时间, 新老标签]
                    investorNumber += 1
                    platforms_investors[platform_id][investor] = {"pending_amount":0, "total_amount":0, "instack_time":end_date,"tag":"new"}
                    if isreset == 0:
                        investorTemp = platforms_investors[platform_id][investor]
                        stringSQL = "SELECT `instack_time`, `total_amount` FROM " + TABLE_01 + "  WHERE `platform_id` = '" + str(platform_id) + "' AND `investor_name` = '" + str(investor) + "'"
                        row_number = cur_db2.execute(stringSQL)
                        if row_number == 1:
                            instack_time, total_amount = cur_db2.fetchone()
                            investorTemp["tag"] = "old"
                            investorTemp["instack_time"] = int(instack_time)
                            investorTemp["total_amount"] = float(total_amount)
                investorTemp = platforms_investors[platform_id][investor]
                investorTemp["pending_amount"] += investorPending
                investorTemp["instack_time"] = min(investorTemp["instack_time"], _date)
                if _date >= initial_date:
                    investorTemp["total_amount"] += total_gross
               
        # 组装借款人信息
        total_gross = float(str(borrowing_amount).replace(",", ""))  # 防止出现2,000.00的情况
        if total_gross < money_error:
            continue
        borrowerPending = total_gross * (totalRatio - paybackRatio)
        if borrower not in platforms_borrowers[platform_id]:
            # 借款人信息：[待还款，总还款额，最早入市时间, 新老标签]
            borrowerNumber += 1
            platforms_borrowers[platform_id][borrower] = {"pending_amount":0, "total_amount":0, "instack_time":end_date, "tag":"new"}
            if isreset == 0:
                borrowerTemp = platforms_borrowers[platform_id][borrower] 
                stringSQL = "SELECT `instack_time`, `total_amount` FROM " + TABLE_03 + "  WHERE `platform_id` = '" + str(platform_id) + "' AND `borrower_name` = '" + str(borrower) + "'"
                row_number = cur_db2.execute(stringSQL)
                if row_number == 1:
                    instack_time, total_amount = cur_db2.fetchone()
                    borrowerTemp["tag"] = "old"
                    borrowerTemp["total_amount"] = float(total_amount)
                    borrowerTemp["instack_time"] = int(instack_time)
        borrowerTemp = platforms_borrowers[platform_id][borrower] 
        borrowerTemp["pending_amount"] += borrowerPending
        borrowerTemp["instack_time"] = min(borrowerTemp["instack_time"], _date)
        if _date >= initial_date:
            borrowerTemp["total_amount"] += total_gross
    print "共有" + str(len(platforms_investors)) + "个平台。"
    print "共有" + str(borrowerNumber) + "个借款人。"
    print "共有" + str(investorNumber) + "个投资人。"
    _end_time = time.time()
    print "The pre_treatment program costs " + str(_end_time - _start_time) + " seconds."                         
  
    ## 3.插入Table_01、Table_03
    _start_time = time.time()
    print ""  
    if isreset == 1:  
        print "Reset '" + TABLE_01 + "' and '" + TABLE_03 + "'"
        cur_db1.execute("TRUNCATE " + TABLE_01)
        conn_db.commit()
        cur_db1.execute("TRUNCATE " + TABLE_03)
        conn_db.commit()
        time.sleep(MAXWAITINGTIME) #防止mysql数据库的延时
    else:
        print "Update '" + TABLE_01 + "' and '" + TABLE_03 + "'"
    print ""
    PercentList = [floor(float(x) * (investorNumber + borrowerNumber) / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)]
    print PercentList
    counter = 0
    #插入Table_01
    for platform_id in platforms_investors:
        for investor in platforms_investors[platform_id]:
            counter += 1
            if counter in PercentList:
                print "inserting: " + str((1 + PercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
            investorTemp = platforms_investors[platform_id][investor]
            if investorTemp["tag"] == "new":
                stringSQL = "INSERT INTO " + TABLE_01 + " (`platform_id`, `investor_name`,`instack_time`,`total_amount`,`pending_amount`) VALUES('" + "','".join([str(platform_id), str(investor), str(investorTemp["instack_time"]), money_format % float(investorTemp["total_amount"]), money_format % float(investorTemp["pending_amount"])]) + "')"
                cur_db1.execute(stringSQL)
                conn_db.commit()
            else:
                stringSQL = "UPDATE " + TABLE_01 + " SET `total_amount` = '" + money_format % float(investorTemp["total_amount"]) + "  WHERE `platform_id` = '" + str(platform_id) + "' AND `investor_name` = '" + str(investor) + "'" 
                cur_db1.execute(stringSQL)
                conn_db.commit()
    #插入Table_03
    for platform_id in platforms_borrowers:
        for borrower in platforms_borrowers[platform_id]:
            counter += 1
            if counter in PercentList:
                print "inserting: " + str((1 + PercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
            borrowerTemp = platforms_borrowers[platform_id][borrower]
            if borrowerTemp["tag"] == "new":
                stringSQL = "INSERT INTO " + TABLE_03 + " (`platform_id`, `borrower_name`,`instack_time`,`total_amount`,`pending_amount`) VALUES('" + "','".join([str(platform_id), str(borrower), str(borrowerTemp["instack_time"]), money_format % float(borrowerTemp["total_amount"]), money_format % float(borrowerTemp["pending_amount"])]) + "')"
                cur_db1.execute(stringSQL)
                conn_db.commit()
            else: 
                stringSQL = "UPDATE " + TABLE_03 + " SET `total_amount` = '" + money_format % float(borrowerTemp["total_amount"]) + "  WHERE `platform_id` = '" + str(platform_id) + "' AND `borrower_name` = '" + str(borrower) + "'" 
                cur_db1.execute(stringSQL)
                conn_db.commit()
    ## 4.收尾处理处理
    closeCursors(cur_db1, cur_db2)
    closeConns(conn_db)  
    print ""
    print "finished"
    _end_time = time.time()
    print "Updating 01 and 03 program costs " + str(_end_time - _start_time) + " seconds."
    
