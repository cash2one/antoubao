# /usr/bin/python
# encoding=utf8
# 从project_info_clean中读取全部数据并创建Table_05

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
    TABLE_05 = "Table_05_pending_bill"

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
    end_date = date_list[-1]
    dates_number = len(date_list)
    
    ## 2.获得原数据并进一步加工
    # 获取母表的全部信息  
    stringSQL = "SELECT id, date, site_id, borrower, borrowing_amount, loan_period, annulized_rating, payment_method, investor, release_time, end_time FROM " + srcdb_info + " WHERE `date` >= '" + str(initial_date) + "'"   
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
        # 获得且清理项目的计息日期
        interest_date = getInterestDate(end_date, borrowing_amount, borrowing_amount, investorStr)[1]
        # 如果有新网站的话增加新网站
        if platform_id not in platforms:
            platforms.add(platform_id)
            platforms_investors[platform_id] = {}
            platforms_borrowers[platform_id] = {}
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
                if investor not in platforms_investors[platform_id]:
                    # 投资人信息：[投资周期，投资年化利率，还款策略，计息日期，投资额度]
                    investorNumber += 1
                    platforms_investors[platform_id][investor] = {"loan_period":[], "annulized_rating":[], "payment_method":[], "interest_date":[], "total_gross":[]}
                investorTemp = platforms_investors[platform_id][investor]
                investorTemp["loan_period"].append(loan_period)
                investorTemp["annulized_rating"].append(annulized_rating)
                investorTemp["payment_method"].append(str(payment_method))
                investorTemp["interest_date"].append(interest_date)
                investorTemp["total_gross"].append(total_gross)
               
        # 组装借款人信息
        total_gross = float(str(borrowing_amount).replace(",", ""))  # 防止出现2,000.00的情况
        if total_gross < money_error:
            continue
        if borrower not in platforms_borrowers[platform_id]:
            # 借款人信息：[借款周期，借款年化利率，还款策略，计息日期，借款额度]
            borrowerNumber += 1
            platforms_borrowers[platform_id][borrower] = {"loan_period":[], "annulized_rating":[], "payment_method":[], "interest_date":[], "total_gross":[]}
        borrowerTemp = platforms_borrowers[platform_id][borrower]
        borrowerTemp["loan_period"].append(loan_period)
        borrowerTemp["annulized_rating"].append(annulized_rating)
        borrowerTemp["payment_method"].append(str(payment_method))
        borrowerTemp["interest_date"].append(interest_date)
        borrowerTemp["total_gross"].append(total_gross)
         
    print "共有" + str(len(platforms_investors)) + "个平台。"
    print "共有" + str(borrowerNumber) + "个借款人。"
    print "共有" + str(investorNumber) + "个投资人。"
    _end_time = time.time()
    print "The pre_treatment program costs " + str(_end_time - _start_time) + " seconds."                         
  
    #插入Table05
    _start_time = time.time()
    print
    if isreset == 1:  
        print "Reset '" + TABLE_05 + "'"
        cur_db1.execute("TRUNCATE " + TABLE_05)
        conn_db.commit()
        time.sleep(MAXWAITINGTIME) #防止mysql数据库的延时
    else:
        print "Update '" + TABLE_05 + "'"
    print ""
    # 所有平台参与者的总人数：
    pendingBillNumber = borrowerNumber + investorNumber
    pendingBillPercentList = [floor(float(x) * pendingBillNumber / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)] 
    pendingBillWeekNodes = [initial_date + x * SECONDSPERWEEK for x in range(0, DURATIONWEEKS + 1)]
    counter = 0
    for platform_id in platforms_investors:  # 与for platform_id in platforms_borrowers一致:
        total_PendingInvestor = [0] * (DURATIONWEEKS + 1)
        total_PendingBorrower = [0] * (DURATIONWEEKS + 1)
        have_date = [0] * (DURATIONWEEKS + 1) #当周是否有数据
        total_PendingInvestorStr = get2DEmptyArray(DURATIONWEEKS + 1)
        total_PendingBorrowerStr = get2DEmptyArray(DURATIONWEEKS + 1)
        # 先处理投资者
        for investor in platforms_investors[platform_id]:
            counter += 1
            if counter in pendingBillPercentList:
                print "inserting: " + str((1 + pendingBillPercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
            investorTemp = platforms_investors[platform_id][investor]
            investorbidNumber = len(investorTemp["interest_date"])
            total_pending_per_investor = [0] * (DURATIONWEEKS + 1)
            for i in range(0, investorbidNumber):
                interest_date = investorTemp["interest_date"][i]
                loan_period = investorTemp["loan_period"][i]
                annulized_rating = investorTemp["annulized_rating"][i]
                payment_method = investorTemp["payment_method"][i]
                total_gross = investorTemp["total_gross"][i]
                start_week_node = int((interest_date - initial_date) / SECONDSPERWEEK)
                end_week_node = int(start_week_node + loan_period / DAYSPERWEEK + 4)
                end_week_node = min(end_week_node, DURATIONWEEKS)
                for j in range(start_week_node, end_week_node + 1):
                    pendingBillWeek = pendingBillWeekNodes[j]
                    # 本周待收款是本周日之前的所有代收款-上周日之前的所有代收款
                    lastInterest = getPayback(interest_date, pendingBillWeek - SECONDSPERWEEK, loan_period, annulized_rating, payment_method)
                    thisInterest = getPayback(interest_date, pendingBillWeek, loan_period, annulized_rating, payment_method)
                    weeklyInterest = total_gross * (thisInterest - lastInterest)
                    if weeklyInterest > money_error:
                        have_date[j] = 1
                        total_pending_per_investor[j] += weeklyInterest
            for i in range(0, DURATIONWEEKS):
                if total_pending_per_investor[i] > money_error:
                    total_PendingInvestor[i] += total_pending_per_investor[i]
                    total_PendingInvestorStr[i].append(investor + "|" + money_format % float(total_pending_per_investor[i]))
        # 再处理借款者
        for borrower in platforms_borrowers[platform_id]:
            counter += 1
            if counter in pendingBillPercentList:
                print "inserting: " + str((1 + pendingBillPercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
            borrowerTemp = platforms_borrowers[platform_id][borrower]
            borrowerbidNumber = len(borrowerTemp["interest_date"])
            total_pending_per_borrower = [0] * (DURATIONWEEKS + 1)
            for i in range(0, borrowerbidNumber):
                interest_date = borrowerTemp["interest_date"][i]
                loan_period = borrowerTemp["loan_period"][i]
                annulized_rating = borrowerTemp["annulized_rating"][i]
                payment_method = borrowerTemp["payment_method"][i]
                total_gross = borrowerTemp["total_gross"][i]
                start_week_node = int((interest_date - initial_date) / SECONDSPERWEEK)
                end_week_node = int(start_week_node + loan_period / DAYSPERWEEK + 4)
                end_week_node = min(end_week_node, DURATIONWEEKS)
                for j in range(start_week_node, end_week_node + 1):
                    pendingBillWeek = pendingBillWeekNodes[j]
                    # 本周待收款是本周日之前的所有代收款-上周日之前的所有代收款
                    lastInterest = getPayback(interest_date, pendingBillWeek - SECONDSPERWEEK, loan_period, annulized_rating, payment_method)
                    thisInterest = getPayback(interest_date, pendingBillWeek, loan_period, annulized_rating, payment_method)
                    weeklyInterest = total_gross * (thisInterest - lastInterest)
                    if weeklyInterest > money_error:
                        have_date[j] = 1
                        total_pending_per_borrower[j] += weeklyInterest
            for i in range(0, DURATIONWEEKS):
                if total_pending_per_borrower[i] > money_error:
                    total_PendingBorrower[i] += total_pending_per_borrower[i]
                    total_PendingBorrowerStr[i].append(borrower + "|" + money_format % float(total_pending_per_borrower[i]))
    
        if isreset == 1:              
            for i in range(0, DURATIONWEEKS):  
                if have_date[i] == 1:          
                    stringSQL = "INSERT INTO " + TABLE_05 + " (`platform_id`, `date`,`amount`,`borrower`,`investor`) VALUES('" + "','".join([str(platform_id), str(pendingBillWeekNodes[i]), money_format % float(total_PendingBorrower[i]), '|'.join(total_PendingBorrowerStr[i]), '|'.join(total_PendingInvestorStr[i])]) + "')"
                    cur_db1.execute(stringSQL)
                    conn_db.commit()   
        else:
            for i in range(0, DURATIONWEEKS):
                if have_date[i] == 1:  
                    stringSQL = "SELECT `amount`, `borrower`, `investor` FROM " + TABLE_05 + "  WHERE `platform_id` = '" + str(platform_id) + "' AND `date` = '" + str(pendingBillWeekNodes[i]) + "'"
                    contained = cur_db1.execute(stringSQL)
                    if contained == 1:
                        (total_amount, borrower, investor) = cur_db1.fetchone()
                        total_PendingBorrower[i] += float(total_amount)
                        borrower = str(borrower)
                        investor = str(investor)
                        stringSQL = "UPDATE " + TABLE_05 + " SET `total_amount` = '" + money_format % float(total_PendingBorrower[i]) + "', `borrower` ='" + borrower + "|" + '|'.join(total_PendingBorrowerStr[i]) + "', `investor` ='" + investor + "|" + '|'.join(total_PendingInvestorStr[i]) + "'  WHERE `platform_id` = '" + str(platform_id) + "' AND `date` = '" + str(pendingBillWeekNodes[i]) + "'" 
                        cur_db1.execute(stringSQL)
                        conn_db.commit()
                    else: 
                        stringSQL = "INSERT INTO " + TABLE_05 + " (`platform_id`, `date`,`amount`,`borrower`,`investor`) VALUES('" + "','".join([str(platform_id), str(pendingBillWeekNodes[i]), money_format % float(total_PendingBorrower[i]), '|'.join(total_PendingBorrowerStr[i]), '|'.join(total_PendingInvestorStr[i])]) + "')"
                        cur_db1.execute(stringSQL)
                        conn_db.commit()
                    
    ## 4.收尾处理处理
    closeCursors(cur_db1, cur_db2)
    closeConns(conn_db)  
    print ""
    print "finished"
    _end_time = time.time()
    print "Updating 05 program costs " + str(_end_time - _start_time) + " seconds."
    
