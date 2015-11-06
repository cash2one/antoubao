# /usr/bin/python
# encoding=utf8
# 将project_info中的脏数据去掉，方便后续处理

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.paymentTools import *
from atbtools.computeTools import *
from math import floor

if __name__ == '__main__':
    
    # 确定金钱的误差0.01元
    money_error = 0.01 / MONEYUNIT
    # 获取连接    
    srcdb_info = "project_info_a"
    srcdb_daily_error = "platform_error_daily_report"
    srcdb_daily_bids = "platform_bids_daily_report"
    
    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    
    #组装还款方式
    (one_time_principal_by_day_Name, monthly_first_interest_Name, ave_capital_plus_interest_Name, quarterly_first_interest_Name, monthly_interest_quarter_onefouth_capital_Name, once_Interest_once_principal_by_day_Name, quarterly_ave_capital_plus_interest_Name, yearly_first_interest_Name, free_interest_Name) = getPaymentMethodName()
    day_payment_method_list = one_time_principal_by_day_Name
    monthly_payment_method_list = monthly_first_interest_Name + ave_capital_plus_interest_Name
    quarter_payment_method_list = quarterly_first_interest_Name
    month_quarter_payment_method_list = monthly_interest_quarter_onefouth_capital_Name
    once_Interest_once_principal_list = once_Interest_once_principal_by_day_Name
    yearly_first_interest_list = yearly_first_interest_Name
    free_interest_list = free_interest_Name
    payment_method_list = monthly_payment_method_list + day_payment_method_list + quarter_payment_method_list + month_quarter_payment_method_list + once_Interest_once_principal_list
    payment_method_dict={}.fromkeys(one_time_principal_by_day_Name, "按天一次性本息")
    payment_method_dict.update({}.fromkeys(monthly_first_interest_Name, "按月付息,到期还本"))
    payment_method_dict.update({}.fromkeys(ave_capital_plus_interest_Name, "按月等额本息"))
    payment_method_dict.update({}.fromkeys(quarterly_first_interest_Name, "按季分期"))
    payment_method_dict.update({}.fromkeys(monthly_interest_quarter_onefouth_capital_Name, "按月还息，季还1/4本金"))
    payment_method_dict.update({}.fromkeys(once_Interest_once_principal_by_day_Name, "一次付息，到期还本"))
    payment_method_dict.update({}.fromkeys(quarterly_ave_capital_plus_interest_Name, "按季等额本金"))
    payment_method_dict.update({}.fromkeys(yearly_first_interest_list, "按年付息到期还本"))
    payment_method_dict.update({}.fromkeys(free_interest_list, "无需还款"))
    
    this_date = time.strftime("%Y%m%d")
    neglect_payment_method_list = ["",None,"无", "无担保"]
#     repeat_white_platform_name_list = getPlatformIdList("repeatwhiteplatform_id.txt")
    fields_list = getAllColumnsFromTable(cur_db, srcdb_info, del_list = ["date", "error"])
    fields_number = len(fields_list)
    
    platform_id_list = getListByTxt("platform_id.txt")

    for site_id in platform_id_list:
        srcdb_info = getProjectInfo("project_info", site_id)
        bad_bids_number = 0
        counter = 0
        bids_number_unfull = 0
        v={}
        error_set = set()
        #获得所有字段
        stringSQL = "SELECT `" +"`,`".join(fields_list) + "` FROM "+ srcdb_info + " WHERE `site_id` ='" + site_id + "'"
        #print "正在从数据库传输数据回本地..."
        bids_number = cur_db.execute(stringSQL)
        rows = cur_db.fetchall()
#         bidsPercentList = [floor(float(x) * bids_number / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)] 
#         print "checking: 0%"
        for row in rows:
            counter += 1
#             if counter in bidsPercentList:
#                 print "checking: " + str((1 + bidsPercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
            for i in range(fields_number):
                v[fields_list[i]] = row[i]
            v["id"] = str(v["id"])
            error = ""
            last_error = 0
            #投资人列表以及相应的满标时间，发标时间
            #1.投资人字段检查
            v["investor"] = v["investor"].strip()
            #1.投资人列表为空
            if len(v["investor"]) == 0:
                bad_bids_number += 1
                error += "1, "
                error_set.add(1)
                last_error = 1
            else:
                #2.投资人列表以"|"开头
                if v["investor"][0] == "|":
                    bad_bids_number += 1
                    error += "2, "
                    error_set.add(2)
                    last_error = 1
                else:
                    #3.投资人列表信息不完整（至少应该有3个1组）
                    investor = v["investor"]
                    investor_set = set()
                    investor_list = investor.split("|")
                    if len(investor_list) < 3:
                        bad_bids_number += 1
                        error += "3, "
                        error_set.add(3)
                        last_error =1
                    else:
                        #4.投资人列表时间戳有误
                        full_time= getInterestDate(0, 0, 0, v["investor"])[0] #计息时间
                        if full_time <= 0:
                            bad_bids_number += 1
                            error += "4, "
                            error_set.add(4)
                            last_error = 1
                        else:
                            count_date = getTimestampZero(full_time, 0, 0) + SECONDSPERWEEK
                            stringSQL = "UPDATE " + srcdb_info + " SET `date` = '" + str(count_date) + "' WHERE `id` = '" + v["id"] + "'"
                            cur_db.execute(stringSQL) 
                            conn_db.commit()
                            first_time = getFirstDate(0, v["investor"])[0]  # 初次被投资时间
                            if first_time <= 0:
                                bad_bids_number += 1
                                error += "4, "
                                error_set.add(4)
                                last_error = 1
                            else:
                                """
                                #5.投资人列表出现大量重复
                                if site_id not in repeat_white_platform_name_list:
                                    investor_number = len(investor_list) / 3
                                    investor_dict = {}
                                    for i in range(investor_number):
                                        investor_str = investor_list[i * 3:(i + 1) * 3]
                                        investor_name = investor_str[1]
                                        if investor_name not in investor_dict:
                                            investor_dict[investor_name] = 0
                                        investor_dict[investor_name] += 1
                                        investor_set.add("|".join(investor_str))
                                    repeat_time = min(investor_dict.values())
                                    if repeat_time > 1:
                                        bad_bids_number += 1
                                        error += "5, "
                                        error_set.add(5)
                                        investor = "|".join(investor_set)
                                        v["investor"] = investor
                                        last_error = 1
                                """
                                #6.投资人列表金额有误
                                v["invested_amount"] = countGross(v["investor"], 3)
                                if v["invested_amount"] <= money_error:
                                    if last_error == 0:
                                        bad_bids_number += 1
                                    error += "6, "
                                    error_set.add(6)
                                    last_error = 1
            #7.还款方式有误
            v["payment_method"] = changePaymentMethod(v["payment_method"].strip())
            if v["payment_method"] in neglect_payment_method_list or v["payment_method"] not in payment_method_dict.keys():
                error += "7, "
                error_set.add(7)
                if last_error == 0:
                    bad_bids_number += 1
                    last_error = 1
            #8.利率有误
            try:
                v["annulized_rating"] = float(v["annulized_rating"])
            except:
                error += "8, "
                error_set.add(8)
                if last_error == 0:
                    bad_bids_number += 1
                    last_error = 1
            else:
                if v["annulized_rating"] <= 1E-6 or v["annulized_rating"] > 100:
                    error += "8, "
                    error_set.add(8)
                    if last_error == 0:
                        bad_bids_number += 1
                        last_error = 1
            #9.还款期限有误
            try: 
                v["loan_period"] = int(v["loan_period"])
            except:
                error += "9, "
                error_set.add(9)
                if last_error == 0:
                    bad_bids_number += 1
                    last_error = 1
            #10.借款人姓名为空
            v["borrower"] = v["borrower"].strip()
            if len(v["borrower"]) == 0:
                error += "10, "
                error_set.add(10)
                if last_error == 0:
                    bad_bids_number += 1
                    last_error = 1
            #11.过于满标
            v["borrowing_amount"] = float(v["borrowing_amount"])
            if v["invested_amount"] > (2 - FULLBIDPERCENT) * v["borrowing_amount"]:
                error += "5, "
                error_set.add(5)
                if last_error == 0:
                    bad_bids_number += 1
                    last_error = 1
            #12.没有满标
            if v["invested_amount"] < FULLBIDPERCENT * v["borrowing_amount"]:
                error += "0, "
                error_set.add(0)
                bids_number_unfull += 1
            #13.写入数据库
            if error != "":
                error = error[:-2]
            count_date = -1
            try:
                full_time= getInterestDate(0, 0, 0, v["investor"])[0]
                count_date = getTimestampZero(full_time, 0, 0) + SECONDSPERWEEK
            except:
                pass
            if count_date <= 0:
                stringSQL = "UPDATE " + srcdb_info + " SET `error` = '" + error + "' WHERE `id` = '" + v["id"] + "'"
            else:
                stringSQL = "UPDATE " + srcdb_info + " SET `error` = '" + error + "', `date` = '" + str(count_date)+ "' WHERE `id` = '" + v["id"] + "'"
            
            cur_db.execute(stringSQL)
            conn_db.commit()
        error_percentage = float(bad_bids_number)/bids_number
#         print "共有" + str(bids_number) + "个标."
#         print "其中有" + str(bids_number_unfull) + "个标未满."
#         print "该平台的数据错误率为" + error_percentage + "."
        error_str = ", ".join(getString(list(error_set)))
        #插入数据
        stringSQL="SELECT * FROM " + srcdb_daily_error + " WHERE `site_id` = '" + site_id + "' AND date = '" + this_date + "'"
        ret = cur_db.execute(stringSQL)
        if ret == 0:
            #先插入平台name和时间戳
            stringSQL="INSERT INTO " + srcdb_daily_error + " (`site_id`, `date`, `error`, `percentage`, `bids_number`, `unfull_bids_number`) VALUES('" + "', '".join([site_id, this_date, error_str, str(error_percentage), str(bids_number), str(bids_number_unfull)]) + "')"
            #print stringSQL
            cur_db.execute(stringSQL)
            conn_db.commit()
        else:
            stringSQL = "UPDATE " + srcdb_daily_error + " SET `error` = '" + error_str + "', `percentage` = '" + str(error_percentage) + "', `bids_number` = '" + str(bids_number) + "', `unfull_bids_number` = '" + str(bids_number_unfull) + "' WHERE `site_id` = '" + site_id + "' AND date = '" + this_date + "'"
            #print stringSQL
            cur_db.execute(stringSQL)
        conn_db.commit()
        
        #插入数据
        stringSQL="SELECT * FROM " + srcdb_daily_bids + " WHERE `site_id` = '" + site_id + "' AND date = '" + this_date + "'"
        ret = cur_db.execute(stringSQL)
        if ret == 0:
            #先插入平台name和时间戳
            stringSQL="INSERT INTO " + srcdb_daily_bids + " (`site_id`, `date`, `alive_bids_number`) VALUES('" + "', '".join([site_id, this_date, str(bids_number)]) + "')"
            #print stringSQL
            cur_db.execute(stringSQL)
        else:
            stringSQL = "UPDATE " + srcdb_daily_bids + " SET `alive_bids_number` = '" + str(bids_number) + "' WHERE `site_id` = '" + site_id + "' AND date = '" + this_date + "'"
            #print stringSQL
            cur_db.execute(stringSQL)
        conn_db.commit()
    
    closeCursors(cur_db)
    closeConns(conn_db)
