# /usr/bin/python
# encoding=utf8
# 从project_info中读取数据来更新E1，注意是新站的全量

import sys
from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from atbtools.paymentTools import *
from atbtools.xmlTools import *
from math import floor
import time
import hashlib
# from meliae import scanner,loader

if __name__ == '__main__':
    # 确定金钱的误差0.01元
    money_error = 0.01 / MONEYUNIT
    #钱数保留几位小数（精确到分）
    money_format = "%." + str(len("%d"%(MONEYUNIT / 0.01))-1) + "f"
    #利率的最大值
    annulized_rating_max = 30.0
    # 获取连接    
    srcdb_info = "project_info_clean"
    srcdb_F = "platform_qualitative_F"
    srcdb_Y = "platform_problem_record_Y"
    TABLE_01 = "Table_01_investor_history"
    TABLE_02 = "Table_02_investor_current"
    TABLE_03 = "Table_03_borrower_history"
    TABLE_04 = "Table_04_borrower_current"
    TABLE_05 = "Table_05_pending_bill"
    TABLE_06 = "Table_06_parameter_quantitative"

    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    
    #从文件中获得新站platform_id
    platform_id_new_list = getPlatformIdList("new_platform_id.txt") #做全量
    if len(platform_id_new_list) == 0:
        print "并没有新增站..."
        exit(0)
    # 指定查询时间
    stringSQL = "SELECT DISTINCT date FROM "+srcdb_info+" ORDER BY date ASC"
    cur_db.execute(stringSQL)
    date_list = []
    for _date in cur_db.fetchall():
        date_list.append(int(_date[0]))
    initial_date = min(date_list)
    end_date = max(date_list)
    dates_number = len(date_list)
    print date_list
    # 获取母表的全部信息     
    stringSQL = "SELECT id, date, site_id, borrower, borrowing_amount, loan_period, annulized_rating, payment_method, investor, release_time, end_time FROM " + srcdb_info
    stringSQL = stringSQL + " WHERE `site_id` in ('" + "','".join(platform_id_new_list) + "')"

    # 测试用
    # 只考虑坏站对应的信息
    #platform_id_list = ["htctou"]
    #print platform_id_list
    #stringSQL = stringSQL + " AND `id` = '23658'"
    print "正在从数据库传输数据回本地..."
    cur_db.execute(stringSQL)
    rows = cur_db.fetchall()
    bidNumber = len(rows)
    bidsPercentList = [floor(float(x) * bidNumber / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)] 
    print "Query project_info(" + str(bidNumber) + ")"
    # 预处理
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
    platform_start_time_dict = {}
    platform_end_time_dict = {}
    for ID, _date, platform_id, borrower, borrowing_amount, loan_period, annulized_rating, payment_method, investorStr, release_time, end_time in rows:
        platform_id = str(platform_id).strip()
        counter += 1
        if counter in bidsPercentList:
            print "querying: " + str((1 + bidsPercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
        annulized_rating = float(annulized_rating) / 100
        if annulized_rating > annulized_rating_max / 100:
            continue
        release_time = int(release_time)
        end_time = int(end_time)
        loan_period = int(loan_period)
        borrowing_amount = borrowing_amount / MONEYUNIT
        #判断每个平台的最早抓取时间
        if platform_id not in platform_start_time_dict:
            platform_start_time_dict[platform_id] = dates_number - 1
            platform_end_time_dict[platform_id] = 0
        platform_start_time_dict[platform_id] = min(platform_start_time_dict[platform_id], date_list.index(_date))
        platform_end_time_dict[platform_id] = max(platform_end_time_dict[platform_id], date_list.index(_date))

        # 获得且清理项目的放标、计息、截止日期
        interest_date = getInterestDate(end_date, borrowing_amount, borrowing_amount, investorStr)[1] #计息时间
        # 如果有新网站的话增加新网站
        if platform_id not in platforms:
            platforms.add(platform_id)
            platforms_investors[platform_id] = {}
            platforms_borrowers[platform_id] = {}
            platforms_bids[platform_id] = {}
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
                investorPending = total_gross * (totalRatio - paybackRatio)
                if investor not in platforms_investors[platform_id]:
                    # 投资人信息：[待收款，总投资额，最早入市时间，投资时间节点，计息时间节点，节点对应的投资额]
                    investorNumber += 1
                    platforms_investors[platform_id][investor] = {"pending_amount":0, "total_amount":0, "instack_time":end_date, "loan_period":[], "annulized_rating":[], "payment_method":[], "invest_time":[], "interest_date":[], "total_gross":[]}
                investorTemp =  platforms_investors[platform_id][investor]
                investorTemp["pending_amount"] += investorPending
                investorTemp["total_amount"] += total_gross
                investorTemp["instack_time"] = min(investorTemp["instack_time"], _date)
                investorTemp["loan_period"].append(loan_period)
                investorTemp["annulized_rating"].append(annulized_rating)
                investorTemp["payment_method"].append(str(payment_method))
                investorTemp["invest_time"].append(_date)
                investorTemp["interest_date"].append(interest_date)
                investorTemp["total_gross"].append(total_gross)
                 
        # 组装借款人信息
        total_gross = float(str(borrowing_amount).replace(",", ""))  # 防止出现2,000.00的情况
        borrowerPending = total_gross * (totalRatio - paybackRatio)
        if borrower not in platforms_borrowers[platform_id]:
            # 借款人信息：[待还款，总还款额，最早入市时间，借款时间节点，计息时间节点，节点对应的借款额]
            borrowerNumber += 1
            platforms_borrowers[platform_id][borrower] = {"pending_amount":0, "total_amount":0, "instack_time":end_date, "loan_period":[], "annulized_rating":[], "payment_method":[], "invest_time":[], "interest_date":[], "total_gross":[]}
        borrowerTemp =  platforms_borrowers[platform_id][borrower]
        borrowerTemp["pending_amount"] += borrowerPending
        borrowerTemp["total_amount"] += total_gross
        borrowerTemp["instack_time"] = min(borrowerTemp["instack_time"], _date)
        borrowerTemp["loan_period"].append(loan_period)
        borrowerTemp["annulized_rating"].append(annulized_rating)
        borrowerTemp["payment_method"].append(str(payment_method))
        borrowerTemp["invest_time"].append(_date)
        borrowerTemp["interest_date"].append(interest_date)
        borrowerTemp["total_gross"].append(total_gross)
     
        # 组装标信息：[借款人，放标时间，停标时间，满标时间，标总额，还款方式，借款天数，年利率
        bidNumber += 1
        platforms_bids[platform_id][ID] = {}
        bidTemp = platforms_bids[platform_id][ID]
        bidTemp["borrower"] = borrower
        bidTemp["release_time"] = release_time
        bidTemp["end_time"] = end_time
        bidTemp["date"] = int(_date)
        bidTemp["borrowing_amount"] = total_gross
        bidTemp["interest_date"] = interest_date
        bidTemp["payment_method"] = str(payment_method)
        bidTemp["loan_period"] = loan_period
        bidTemp["annulized_rating"] = annulized_rating
    
    # 插入新站到Table01
    print "Update new platform for '" + TABLE_01
    PercentList = [floor(float(x) * investorNumber / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)]
    counter = 0
    for platform_id in platforms_investors:
        for investor in platforms_investors[platform_id]:
            counter += 1
            if counter in PercentList:
                print "inserting: " + str((1 + PercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
            investorTemp = platforms_investors[platform_id][investor]
            stringSQL = "INSERT INTO " + TABLE_01 + " (`platform_id`, `investor_name`,`instack_time`,`total_amount`,`pending_amount`) VALUES('" + "','".join([str(platform_id), str(investor), str(investorTemp["instack_time"]), money_format % float(investorTemp["total_amount"]), money_format % float(investorTemp["pending_amount"])]) + "')"
            cur_db.execute(stringSQL)
            conn_db.commit()
    # 插入Table02
    print "Update new platform for '" + TABLE_02
    PercentList = [floor(float(x) * investorNumber / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)]
    counter = 0
    for platform_id in platforms_investors:
        for investor in platforms_investors[platform_id]:
            counter += 1
            if counter in PercentList:
                print "inserting: " + str((1 + PercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
            investorTemp = platforms_investors[platform_id][investor]
            week_amount = [0] * dates_number
            investorbidNumber = len(investorTemp["invest_time"])
            for i in range(0, investorbidNumber):
                week_amount[date_list.index(investorTemp["invest_time"][i])] += investorTemp["total_gross"][i]
            for i in range(dates_number):
                week_amount_temp = week_amount[i]  
                date_temp = date_list[i]
                if week_amount_temp > money_error:
                    tag = "old" if date_temp > investorTemp["instack_time"] else "new"
                    stringSQL = "INSERT INTO " + TABLE_02 + " (`platform_id`, `investor_name`,`date`,`week_amount`,`tag_new_old`) VALUES('" + "','".join([str(platform_id), str(investor), str(date_temp), money_format % float(week_amount_temp), str(tag)]) + "')"
                    cur_db.execute(stringSQL)
                    conn_db.commit()
    #插入Table_03
    print "Update new platform for '" + TABLE_03
    PercentList = [floor(float(x) * borrowerNumber / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)]
    counter = 0
    for platform_id in platforms_borrowers:
        for borrower in platforms_borrowers[platform_id]:
            counter += 1
            if counter in PercentList:
                print "inserting: " + str((1 + PercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
            borrowerTemp = platforms_borrowers[platform_id][borrower]
            stringSQL = "INSERT INTO " + TABLE_03 + " (`platform_id`, `borrower_name`,`instack_time`,`total_amount`,`pending_amount`) VALUES('" + "','".join([str(platform_id), str(borrower), str(borrowerTemp["instack_time"]), money_format % float(borrowerTemp["total_amount"]), money_format % float(borrowerTemp["pending_amount"])]) + "')"
            cur_db.execute(stringSQL)
            conn_db.commit()
    # 插入Table04
    print "Update new platform for '" + TABLE_04
    PercentList = [floor(float(x) * borrowerNumber / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)]
    counter = 0
    for platform_id in platforms_borrowers:
        for borrower in platforms_borrowers[platform_id]:
            counter += 1
            if counter in PercentList:
                print "inserting: " + str((1 + PercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
            borrowerTemp = platforms_borrowers[platform_id][borrower]
            week_amount = [0] * dates_number
            borrowerbidNumber = len(borrowerTemp["invest_time"])
            for i in range(0, borrowerbidNumber):
                week_amount[date_list.index(borrowerTemp["invest_time"][i])] += borrowerTemp["total_gross"][i]
            for i in range(dates_number):
                week_amount_temp = week_amount[i]  
                date_temp = date_list[i]
                if week_amount_temp > money_error:
                    tag = "old" if date_temp > borrowerTemp["instack_time"] else "new"
                    stringSQL = "INSERT INTO " + TABLE_04 + " (`platform_id`, `borrower_name`,`date`,`week_amount`,`tag_new_old`) VALUES('" + "','".join([str(platform_id), str(borrower), str(date_temp), money_format % float(week_amount_temp), str(tag)]) + "')"
                    cur_db.execute(stringSQL)
                    conn_db.commit()
    # 插入Table05
    print "Update new platform for '" + TABLE_05
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
    
        for i in range(0, DURATIONWEEKS):  
            if have_date[i] == 1:          
                stringSQL = "INSERT INTO " + TABLE_05 + " (`platform_id`, `date`,`amount`,`borrower`,`investor`) VALUES('" + "','".join([str(platform_id), str(pendingBillWeekNodes[i]), money_format % float(total_PendingBorrower[i]), '|'.join(total_PendingBorrowerStr[i]), '|'.join(total_PendingInvestorStr[i])]) + "')"
                cur_db.execute(stringSQL)
                conn_db.commit()   
    # 插入Table06  
    print "Update new platform for '" + TABLE_06
    counter = 0
    platformNumber = len(platforms_investors)
    quantitativeNumber = borrowerNumber + investorNumber + bidNumber + dates_number
    print "共有" + str(platformNumber) + "个平台。"
    print "共有" + str(bidNumber) + "个标。"
    print "共有" + str(borrowerNumber) + "个借款人。"
    print "共有" + str(investorNumber) + "个投资人。"
    quantitativePercentList = [floor(float(x) * quantitativeNumber / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)] 
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
    for platform_id in platforms_investors:
        print platform_id
        having_date = [0] * dates_number
        # 先获得定性属性
        stringSQL = "SELECT " + ",".join(E1_key_inF_list) + " FROM " + srcdb_F + " WHERE `platform_id` = '" + str(platform_id) + "'"
        row_number = cur_db.execute(stringSQL)
        for i in range(0, E1_key_inF_number):
            exec(E1_key_inF_list[i] + "=  [0] * dates_number")
        if row_number == 0:
            print "The " + srcdb_F + " table has no platform_id called " + platform_id
            for i in range(0, dates_number):
                platform_name[i] = platform_id
        else:       
            row = cur_db.fetchone()
            for i in range(0, E1_key_inF_number):
                value = 0 if None == row[i] else row[i] #为避免出现truncate数据的情况，这里全置于0
                for j in range(0, dates_number):
                    exec(E1_key_inF_list[i] + "[j]=value")
        for i in range(0, dates_number):
            vc_cap_usd[i] *= 6 * 0.8
            registered_cap[i] += 0.1 * parent_company_cap[i]
        # 再获得定量属性
        for value in E1_key_L_list:
            exec(value + "=  [WRONGNUMBER] * dates_number")
              
        top10Lending = get2DEmptyArray(dates_number)  # 排名前10的的未来一周待还额的列表（小于10的直接从该列表抽取）
        weeklyInvestList = get2DEmptyArray(dates_number)  # 每周所有投资额的列表
        weeklyborrowList = get2DEmptyArray(dates_number)  # 每周所有借款额的列表
        long_term_InvestList = get2DEmptyArray(dates_number)  # 历史中所有投资额的列表
        long_term_BorrowList = get2DEmptyArray(dates_number)  # 历史中所有借款额的列表
        close_time_list = get2DEmptyArray(dates_number)  # 每周所有标的close_time
        weekly_bid_sum = [0] * dates_number
        weekly_lending_old = [0] * dates_number
        weekly_new_borrower = [0] * dates_number  # 在weekly_total_borrower的基础上，要从history中查找是否有此人
        manual_handling_tag_list = [0] * dates_number  # 该数据是否经过人工处理
        weekly_loan_period_initial = [0] * dates_number
        cash_flow_in_initial = [0] * dates_number
        ave_annualized_return_initial = [0] * dates_number
        # 处理投资人
        for investor in platforms_investors[platform_id]:
            counter += 1
            if counter in quantitativePercentList:
                print "updating: " + str((1 + quantitativePercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
            investorTemp = platforms_investors[platform_id][investor]
            investorbidNumber = len(investorTemp["invest_time"])
            instack_time = investorTemp["instack_time"]
            repeat_times = [0] * dates_number
            repeat_times_new = [0] * dates_number
            weekly_invest_amount = [0] * dates_number
            for i in range(0, investorbidNumber):
                interest_date = investorTemp["interest_date"][i]
                invest_time = investorTemp["invest_time"][i]
                history_time_node = date_list.index(invest_time)
                repeat_times[history_time_node] = 1
                weekly_invest_amount[history_time_node] += investorTemp["total_gross"][i]
                if invest_time <= instack_time:
                    weekly_new_investor[history_time_node] += 1 - repeat_times_new[history_time_node]
                    repeat_times_new[history_time_node] = 1
                else:  # 老投资人
                    weekly_lending_old[history_time_node] += investorTemp["total_gross"][i]
                wholeInterest = getPayback(0, end_date, investorTemp["loan_period"][i], investorTemp["annulized_rating"][i], investorTemp["payment_method"][i])  # 所有本利和
                loan_period = investorTemp["loan_period"][i]
                annulized_rating = investorTemp["annulized_rating"][i]
                payment_method = investorTemp["payment_method"][i]
                total_gross = investorTemp["total_gross"][i]
                invest_time = investorTemp["invest_time"][i]
                interest_end_date = interest_date + (loan_period + 10) * SECONDSPERDAY
                
                for j in range(0, dates_number):
                    history_time_temp = date_list[j]
                    if interest_end_date > history_time_temp >= invest_time:
                        thisInterest = getPayback(interest_date, history_time_temp, loan_period, annulized_rating, payment_method)
                        lastInterest = getPayback(interest_date, history_time_temp - SECONDSPERWEEK, loan_period, annulized_rating, payment_method)
                        cash_flow_in_initial[j] += total_gross * (thisInterest - lastInterest)
            for i in range(0, dates_number):
                weekly_total_investor[i] += repeat_times[i]
                weeklyInvestList[i].append(weekly_invest_amount[i])
                long_term_InvestList[i].append(weekly_invest_amount[i])
                   
        # 处理借款者
        for borrower in platforms_borrowers[platform_id]:
            counter += 1
            if counter in quantitativePercentList:        
                print "updating: " + str((1 + quantitativePercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
            borrowerTemp = platforms_borrowers[platform_id][borrower]
            borrowerbidNumber = len(borrowerTemp["invest_time"])
            instack_time = borrowerTemp["instack_time"]
            pending_repayment = [0] * dates_number
            repeat_times = [0] * dates_number
            repeat_times_new = [0] * dates_number
            weekly_borrowing_amount = [0] * dates_number
            for i in range(0, borrowerbidNumber):
                interest_date = borrowerTemp["interest_date"][i]
                invest_time = borrowerTemp["invest_time"][i]
                history_time_node = date_list.index(invest_time)
                repeat_times[history_time_node] = 1
                weekly_borrowing_amount[history_time_node] += borrowerTemp["total_gross"][i]
                if invest_time <= instack_time:
                    weekly_new_borrower[history_time_node] += 1 - repeat_times_new[history_time_node]
                    repeat_times_new[history_time_node] = 1
                loan_period = borrowerTemp["loan_period"][i]
                annulized_rating = borrowerTemp["annulized_rating"][i]
                payment_method = borrowerTemp["payment_method"][i]
                total_gross = borrowerTemp["total_gross"][i]
                invest_time = borrowerTemp["invest_time"][i]
                interest_end_date = interest_date + (loan_period + 10) * SECONDSPERDAY
                wholeInterest = getPayback(0, end_date, loan_period, annulized_rating, payment_method)  # 所有本利和
                for j in range(0, dates_number):
                    history_time_temp = date_list[j]
                    if interest_end_date > history_time_temp >= invest_time:
                        thisInterest = getPayback(interest_date, history_time_temp, loan_period, annulized_rating, payment_method)  # 所有本利和
                        futureInterest = total_gross * (wholeInterest - thisInterest)
                        weekly_outstanding_loan[j] += futureInterest
                        pending_repayment[j] +=futureInterest
                        future4WeeksWholeInterest = getPayback(interest_date, history_time_temp + FUTUREPAYBACKWEEKS * SECONDSPERWEEK, loan_period, annulized_rating, payment_method)
                        future4week_maturity[j] += total_gross * (future4WeeksWholeInterest - thisInterest)
            for i in range(0, dates_number):
                if pending_repayment[i] > money_error:
                    insertTopQueue(top10Lending[i], pending_repayment[i], 10)
                weekly_total_borrower[i] += repeat_times[i]
                weeklyborrowList[i].append(weekly_borrowing_amount[i])
                long_term_BorrowList[i].append(weekly_borrowing_amount[i]) 
                     
        # 处理标
        for bidID in platforms_bids[platform_id]:
            counter += 1
            if counter in quantitativePercentList:        
                print "updating: " + str((1 + quantitativePercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
            bidTemp = platforms_bids[platform_id][bidID]
            interest_date = bidTemp["interest_date"]
            release_time = bidTemp["release_time"]
            end_time = bidTemp["end_time"]
            history_time_node = date_list.index(bidTemp["date"]) 
            weekly_bid_sum[history_time_node] += 1
            close_time_list[history_time_node].append(end_time - release_time)
            weekly_loan_period_initial[history_time_node] += float(bidTemp["loan_period"]) * bidTemp["borrowing_amount"]
            ave_annualized_return_initial[history_time_node] += bidTemp["annulized_rating"] * bidTemp["borrowing_amount"]
            weekly_lending[history_time_node] += bidTemp["borrowing_amount"]
 
        # 汇总
        start_date_index = platform_start_time_dict[platform_id]
        end_date_index = platform_end_time_dict[platform_id]
        for i in range(start_date_index, dates_number):
            counter += 1
            if counter in quantitativePercentList:
                print "inserting: " + str((1 + quantitativePercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
            #和过去有关的指标
            if i >= LASTLENDINGWEEKS:
                for j in range(0, i-LASTLENDINGWEEKS+1)[::-1]:
                    if weekly_total_borrower[j] != 0:
                        borrower_growth[i] = weekly_total_borrower[i] / weekly_total_borrower[j]
                        break 
                for j in range(0, i-LASTLENDINGWEEKS+1)[::-1]:
                    if weekly_total_investor[j] != 0:
                        investor_growth[i] = weekly_total_investor[i] / weekly_total_investor[j]
                        break
            k = 0
            for j in range(0, i)[::-1]:
                if weekly_lending[j] != 0:
                    k += 1 
                    latest4week_lending[i] += weekly_lending[j]
                    if k == LASTLENDINGWEEKS:
                        break
            multiple = 1 #人工干预weekly_outstanding_loan系数
            #weekly_lending分母
            if weekly_lending[i] != 0:
                weekly_loan_period[i] = weekly_loan_period_initial[i] / weekly_lending[i]
                #人工干预系数计算，通过weekly_loan_period来计算
                passed_week = i - start_date_index + 1
                weekly_loan_period_week = int(weekly_loan_period[i] / DAYSPERWEEK) 
                if passed_week < weekly_loan_period_week:
                    manual_handling_tag_list[i] = 1
                    multiple = float(weekly_loan_period_week) / passed_week
                cash_flow_in[i] = (weekly_lending[i] - cash_flow_in_initial[i] * multiple) / weekly_lending[i]
                ave_annualized_return[i] = ave_annualized_return_initial[i] / weekly_lending[i] *100
                if weekly_bid_sum[i] != 0:
                    weekly_ave_bid_close_time[i] = getCenterSum(close_time_list[i]) / weekly_bid_sum[i] / weekly_lending[i]
                    weekly_ave_lending_per_bid[i] = weekly_lending[i] / weekly_bid_sum[i] * MONEYUNIT
            
            #future4week_maturity分母   
            if future4week_maturity[i] != 0:
                future4week_maturity[i] *= multiple
                not_returned_yet[i] = latest4week_lending[i] / future4week_maturity[i]
            #weekly_outstanding_loan分母
            if weekly_outstanding_loan[i] != 0:   
                top10_ratio_loan[i] = sum(top10Lending[i]) / weekly_outstanding_loan[i]
                top5_ratio_loan[i] = sum(top10Lending[i][:5]) / weekly_outstanding_loan[i]
                weekly_outstanding_loan[i] *= multiple
                short_term_debt_ratio[i] = future4week_maturity[i] / weekly_outstanding_loan[i]
                turnover_registered[i] = (vc_cap_usd[i] + registered_cap[i]) / weekly_outstanding_loan[i]
                outstanding_loan[i] = latest4week_lending[i] / weekly_outstanding_loan[i]
            #latest4week_lending分母   
            money_growth[i] = WRONGNUMBER if weekly_loan_period[i] == 0 or latest4week_lending[i] == 0 else (future4week_maturity[i] / latest4week_lending[i]) ** (1 / weekly_loan_period[i])

            investor_HHI[i] = getHHI(weeklyInvestList[i]) 
            borrower_HHI[i] = getHHI(weeklyborrowList[i]) 
            weekly_ave_investment[i] = WRONGNUMBER if weekly_total_investor[i] == 0 else weekly_lending[i] / weekly_total_investor[i]
            weekly_ave_investment_old[i] = WRONGNUMBER if weekly_total_investor[i] == weekly_new_investor[i] else weekly_lending_old[i] / (weekly_total_investor[i] - weekly_new_investor[i])
            weekly_ratio_new_old[i] = WRONGNUMBER if weekly_total_investor[i] == weekly_new_investor[i] else float(weekly_new_investor[i]) / (weekly_total_investor[i] - weekly_new_investor[i])
            weekly_ave_lending_per_borrower[i] = WRONGNUMBER if weekly_total_borrower[i] == 0 else weekly_lending[i] / weekly_total_borrower[i]
            turnover_period[i] = weekly_lending[i] * weekly_loan_period[i] / MONTHSPERYEAR
            platform_name[i] = platform_name[i].strip()
            if weekly_total_borrower[i] > 0:
                having_date[i] = 1
            if weekly_outstanding_loan[i] > money_error:
                having_date[i] = 1
        platform_id_md5 = hashlib.md5(platform_name[i]).hexdigest()[0:10]
        platform_id_md5_dict[platform_id] = platform_id_md5 
        for i in range(start_date_index, dates_number):  # 为避免本周数据的干扰，特别的将本周数据去掉
            #有数据的时候才插入
            if having_date[i] == 1: 
                history_time_node = date_list[i]
                key_str = ["date", "platform_id"]
                value_str = [str(history_time_node), platform_id_md5]
                for key in E1_key_inE1_list:
                    if key not in neglect_field_list:
                        key_str.append(str(key))
                        exec("value_str.append(str(" + key + "[i]))")
                stringSQL = "INSERT INTO " + TABLE_06 + "(`" + "`,`".join(key_str) + "`) VALUES('" + "','".join(value_str) + "')"
                cur_db.execute(stringSQL)
                conn_db.commit()
                 
    closeCursors(cur_db)
    closeConns(conn_db)  
    print ""
    print "finished"
