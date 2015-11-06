# /usr/bin/python
# encoding=utf8
# 从project_info中读取数据来更新E1

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from atbtools.paymentTools import *
from math import floor
import time
import hashlib

if __name__ == '__main__':
    # 确定金钱的误差0.01元
    money_error = 0.01 / MONEYUNIT
    #利率的最大值
    annulized_rating_max = 30.0
    # 获取连接    
    srcdb_info = "project_info_clean_temp"
    srcdb_F = "platform_qualitative_F"
    srcdb_Y = "platform_problem_record_Y"
    dstdb_E1 = "platform_quantitative_data_E1"

    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)

    #从文件中获得坏站platform_id
    platform_id_list = getPlatformIdList("badplatform_id.txt")
    platform_id_del_list = getPlatformIdList("badplatform_id_del.txt")
    platform_id_list = list(set(platform_id_list) - set(platform_id_del_list))
    
    # 指定查询时间
    stringSQL = "SELECT DISTINCT date FROM " + srcdb_info
    stringSQL = stringSQL + " WHERE `site_id` in ('" + "','".join(platform_id_list) + "')" + " ORDER BY date ASC"
    cur_db.execute(stringSQL)
    date_list = []
    for _date in cur_db.fetchall():
        date_list.append(int(_date[0]))
    if len(date_list) == 0:
        print stringSQL
        print "没有找到相应的时间戳."
        exit(1)
    initial_date = min(date_list)
    end_date = max(date_list)
    dates_number = len(date_list)
    # 查询E1表中的所有时间戳
    E1_date_nodes = []
    stringSQL = "SELECT DISTINCT date FROM " + dstdb_E1 + " ORDER BY `date` ASC"
    E1_date_nodes_number = cur_db.execute(stringSQL)
    rows = cur_db.fetchall()
    for row in rows:
        if row[0] in date_list:
            E1_date_nodes.append(date_list.index(row[0])) 
    if len(E1_date_nodes) == 0:
        print "在" + dstdb_E1 + "中没有相应的时间戳."
        exit(1)
    
    # 获取母表的全部信息     
    stringSQL = "SELECT id, date, site_id, borrower, borrowing_amount, loan_period, annulized_rating, payment_method, investor, release_time, end_time FROM " + srcdb_info
    stringSQL = stringSQL + " WHERE `site_id` in ('" + "','".join(platform_id_list) + "')"
    print "正在从数据库传输数据回本地..."
    cur_db.execute(stringSQL)
    rows = cur_db.fetchall()
    bidNumber = len(rows)
    bidsPercentList = [floor(float(x) * bidNumber / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)] 
    #print "Query project_info(" + str(bidNumber) + ")"
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
                investorTemp["payment_method"].append(payment_method)
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
        borrowerTemp["payment_method"].append(payment_method)
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
        bidTemp["payment_method"] = payment_method
        bidTemp["loan_period"] = loan_period
        bidTemp["annulized_rating"] = annulized_rating
    counter = 0
    platformNumber = len(platforms_investors)
    quantitativeNumber = borrowerNumber + investorNumber + bidNumber + dates_number
    print "共有" + str(platformNumber) + "个平台。 "
    print "共有" + str(bidNumber) + "个标。"
    print "共有" + str(borrowerNumber) + "个借款人。"
    print "共有" + str(investorNumber) + "个投资人。"
    print "开始更新'" + dstdb_E1 + "'"
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    quantitativePercentList = [floor(float(x) * quantitativeNumber / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)] 
    E1_key_dict = {}
    E1_key_dict["L"] = {}
    E1_key_dict["X"] = {}
    E1_key_dict["L"]["initial"] = ["weekly_total_investor", "weekly_lending", "weekly_total_borrower", "weekly_loan_period", "ave_annualized_return", "future4week_maturity", "cash_flow_in", "weekly_outstanding_loan", "investor_HHI", "borrower_HHI", "weekly_ave_lending_per_bid", "weekly_ave_bid_close_time", "weekly_new_investor", "provision_of_risk", "weekly_ave_investment_old", "top5_ratio_loan", "top10_ratio_loan", "top5_ratio_investment", "top10_ratio_investment", "weekly_ave_lending_per_borrower", "weekly_ave_investment", "weekly_ratio_new_old", "borrower_growth", "investor_growth", "latest4week_lending", "outstanding_loan", "turnover_registered", "not_returned_yet", "money_growth", "turnover_period", "short_term_debt_ratio", "market_share_growth"]
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
              
        top10Lending = get2DEmptyArray(dates_number)  # 排名前10的的借款人的未来一周待还额的列表（小于10的直接从该列表抽取）
        top10Investing = get2DEmptyArray(dates_number)  # 排名前10的投资人的未来一周待还额的列表（小于10的直接从该列表抽取）

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
            pending_repayment = [0] * dates_number
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
                        futureInterest = total_gross * (wholeInterest - thisInterest)
                        pending_repayment[j] += futureInterest
                        
            for i in range(0, dates_number):
                if pending_repayment[i] > money_error:
                    insertTopQueue(top10Investing[i], pending_repayment[i], 10)
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
                print "updating: " + str((1 + quantitativePercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
            weekly_lending[i] = float(weekly_lending[i])
            weekly_outstanding_loan[i] = float(weekly_outstanding_loan[i])
            future4week_maturity[i] = float(future4week_maturity[i])
            latest4week_lending[i] = float(latest4week_lending[i])
            weekly_lending_old[i] = float(weekly_lending_old[i])
            #和过去有关的指标
            if i >= LASTLENDINGWEEKS:
                for j in range(0, i-LASTLENDINGWEEKS+1)[::-1]:
                    if weekly_total_borrower[j] != 0:
                        borrower_growth[i] = float(weekly_total_borrower[i]) / weekly_total_borrower[j]
                        break 
                for j in range(0, i-LASTLENDINGWEEKS+1)[::-1]:
                    if weekly_total_investor[j] != 0:
                        investor_growth[i] = float(weekly_total_investor[i]) / weekly_total_investor[j]
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
                weekly_loan_period[i] = weekly_loan_period_initial[i] / weekly_lending[i] #天
                #人工干预系数计算，通过weekly_loan_period来计算
                passed_week = i - start_date_index + 1
                weekly_loan_period_week = int(weekly_loan_period[i] / DAYSPERWEEK) 
                if passed_week < weekly_loan_period_week:
                    manual_handling_tag_list[i] = 1
                    multiple = float(weekly_loan_period_week) / passed_week
                cash_flow_in[i] = (weekly_lending[i] - cash_flow_in_initial[i] * multiple) / weekly_lending[i]
                ave_annualized_return[i] = ave_annualized_return_initial[i] / weekly_lending[i] *100
                if weekly_bid_sum[i] != 0:
                    #weekly_ave_bid_close_time[i] = getCenterSum(close_time_list[i]) / weekly_bid_sum[i] / weekly_lending[i]
                    weekly_ave_bid_close_time[i] = getCenterSum(close_time_list[i]) / weekly_lending[i]
                    weekly_ave_lending_per_bid[i] = weekly_lending[i] / weekly_bid_sum[i] * MONEYUNIT
            #future4week_maturity分母   
            if future4week_maturity[i] != 0:
                future4week_maturity[i] *= multiple
                not_returned_yet[i] = latest4week_lending[i] / future4week_maturity[i]
            #weekly_outstanding_loan分母
            if weekly_outstanding_loan[i] != 0:
                top10_ratio_loan[i] = sum(top10Lending[i]) / weekly_outstanding_loan[i]
                top5_ratio_loan[i] = sum(top10Lending[i][:5]) / weekly_outstanding_loan[i]
                top10_ratio_investment[i] = sum(top10Investing[i]) / weekly_outstanding_loan[i]
                top5_ratio_investment[i] = sum(top10Investing[i][:5]) / weekly_outstanding_loan[i]
                weekly_outstanding_loan[i] *= multiple
                short_term_debt_ratio[i] = future4week_maturity[i] / weekly_outstanding_loan[i]
                turnover_registered[i] = (vc_cap_usd[i] + registered_cap[i]) / weekly_outstanding_loan[i]
                outstanding_loan[i] = latest4week_lending[i] / weekly_outstanding_loan[i]
            #latest4week_lending分母   
            money_growth[i] = WRONGNUMBER if weekly_loan_period[i] == 0 or not_returned_yet[i] == 0 else (not_returned_yet[i]) ** (1.0 / (weekly_loan_period[i] / DAYSPERMONTH))
             
            investor_HHI[i] = getHHI(weeklyInvestList[i]) * 10000
            borrower_HHI[i] = getHHI(weeklyborrowList[i]) * 10000
            weekly_ave_investment[i] = WRONGNUMBER if weekly_total_investor[i] == 0 else weekly_lending[i] / weekly_total_investor[i]
            weekly_ave_investment_old[i] = WRONGNUMBER if weekly_total_investor[i] == weekly_new_investor[i] else weekly_lending_old[i] / (weekly_total_investor[i] - weekly_new_investor[i])
            weekly_ratio_new_old[i] = WRONGNUMBER if weekly_total_investor[i] == 0 else float(weekly_new_investor[i]) / weekly_total_investor[i]
            weekly_ave_lending_per_borrower[i] = WRONGNUMBER if weekly_total_borrower[i] == 0 else weekly_lending[i] / weekly_total_borrower[i]
            turnover_period[i] = latest4week_lending[i] / 4 * weekly_loan_period[i] / DAYSPERYEAR #万元*年
            platform_name[i] = platform_name[i].strip()
            if weekly_total_borrower[i] > 0:
                having_date[i] = 1
            if weekly_outstanding_loan[i] > money_error:
                having_date[i] = 1
        platform_id_md5 = hashlib.md5(platform_name[i]).hexdigest()[0:10]
        platform_id_md5_dict[platform_id] = platform_id_md5 
        
        
        
        
        
        
        
        
        
        start_date = having_date.index(1) #以是否有借款人作为平台的初始营业时间
        for i in E1_date_nodes:  # 为避免本周数据的干扰，特别的将本周数据去掉
            #有数据的时候才插入
            if i >= start_date and having_date[i] == 1: 
                history_time_node = date_list[i]
                stringSQL = "SELECT count(*) FROM " + dstdb_E1 + " WHERE `platform_id` = '" + platform_id_md5 + "' AND `date` = '" + str(history_time_node) + "'"               
                cur_db.execute(stringSQL)
                row = cur_db.fetchone()[0]
                    
                # 插入
                if None == row or 0 == row:
                    key_str = ["date", "platform_id"]
                    value_str = [str(history_time_node), platform_id_md5]
                    for key in E1_key_inE1_list:
                        if key not in neglect_field_list:
                            key_str.append(str(key))
                            exec("value_str.append(str(" + key + "[i]))")
                    stringSQL = "INSERT INTO " + dstdb_E1 + "(`" + "`,`".join(key_str) + "`) VALUES('" + "','".join(value_str) + "')"
                    cur_db.execute(stringSQL)
                    conn_db.commit()
                # 更新
                else:
                    key_value_str = []
                    for key in E1_key_inE1_list:
                        if key not in neglect_field_list:
                            exec("temp_arr = " + key + "[i]")
                            key_value_str.append("`" + str(key) + "` = '" + str(temp_arr) + "'")
                    stringSQL = "UPDATE " + dstdb_E1 + " SET " + ",".join(key_value_str) + " WHERE `platform_id` = '" + platform_id_md5 + "' AND `date` = '" + str(history_time_node) + "'"    
                    cur_db.execute(stringSQL)
                    conn_db.commit() 
#                   
    # 单独处理market_share_growth 
    time.sleep(MAXWAITINGTIME) 
    print "开始计算'market_share_growth'."
    print E1_date_nodes
    total_market_share = [0] * dates_number
    for i in E1_date_nodes:
        history_time_node = date_list[i]
        stringSQL = "SELECT SUM(weekly_lending) FROM " + dstdb_E1 + " WHERE `date` = '" + str(history_time_node) + "'"
        cur_db.execute(stringSQL)
        total_market_share[i] = cur_db.fetchone()[0]
    for platform_id in platforms_investors:
        platform_id_md5 = platform_id_md5_dict[platform_id]
        market_share = [0] * dates_number
        having_date = [0] * dates_number
        for i in range(dates_number):
            if i in E1_date_nodes:
                history_time_node = date_list[i]
                stringSQL = "SELECT weekly_lending FROM " + dstdb_E1 + " WHERE `date` = '" + str(history_time_node) + "' AND `platform_id` = '" + platform_id_md5 + "'"
                ret = cur_db.execute(stringSQL)
                if ret == 0:
                    continue
                having_date[i] = 1
                market_share[i] = cur_db.fetchone()[0]
                market_share[i] = WRONGNUMBER if total_market_share[i] == 0 else market_share[i] / total_market_share[i]
                if market_share[i] == 1:
                    market_share[i] = 0 #排除只有该时间段只有唯一数据源
                if market_share[i] > 1:
                    print history_time_node , platform_id , market_share[i], total_market_share[i]
            else:
                #如果没有在E1_date_nodes中的时间节点，则market_share用最近的替换
                if i > min(E1_date_nodes):
                    j = i - 1
                    while(j not in E1_date_nodes):
                        j = j - 1
                    market_share[i] = market_share[j]
        market_share_growth = [0] * dates_number
        for i in E1_date_nodes:
            if having_date[i] == 1:
                market_share_growth[i] = WRONGNUMBER if i < 4 else (WRONGNUMBER if (market_share[i - 4] == 0 or market_share[i - 4] == WRONGNUMBER or market_share[i] == WRONGNUMBER) else market_share[i] / market_share[i - 4])
                if market_share_growth[i] != WRONGNUMBER:
                    stringSQL = "UPDATE " + dstdb_E1 + " SET `market_share_growth` = '" + str(market_share_growth[i]) + "' WHERE `platform_id` = '" + platform_id_md5 + "' AND `date` = '" + str(date_list[i]) + "'"   
                    cur_db.execute(stringSQL)
                    conn_db.commit() 
                    
    closeCursors(cur_db)
    closeConns(conn_db)  
