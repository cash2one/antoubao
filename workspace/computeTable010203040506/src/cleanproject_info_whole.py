# /usr/bin/python
# encoding=utf8
# 将project_info中的脏数据去掉，方便后续处理

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from atbtools.xmlTools import *
from atbtools.paymentTools import *
from math import floor

if __name__ == '__main__':
    
#清理数据的时间为每周一次，且每次只保留上一周满标的数据
    clean_date_now = int(time.time())
    clean_date_lasttime=int(getValue("./clean_date.xml","clean_date_lasttime"))
    if clean_date_now - clean_date_lasttime < SECONDSPERWEEK:
        print "上一周的数据已经清理过了，不需要再清理"
        exit(0)
    else:
        clean_date_thistime = getTimestampZero(clean_date_now, 0, 0)
    # 确定金钱的误差0.01元
    money_error = 0.01 / MONEYUNIT
    # 获取连接    
    srcdb_info = "project_info"
    dstdb_info = "project_info_clean"
    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db1, cur_db2 = getCursors(conn_db, 2)
    initializeCursors(cur_db1, cur_db2)
    #payment的统一化调整
    (one_time_principal_by_day_Name, monthly_first_interest_Name, ave_capital_plus_interest_Name, quarterly_first_interest_Name, monthly_interest_quarter_onefouth_capital_Name, once_Interest_once_principal_by_day_Name, quarterly_ave_capital_plus_interest_Name) = getPaymentMethodName()
    day_payment_method_list = one_time_principal_by_day_Name
    monthly_payment_method_list = monthly_first_interest_Name + ave_capital_plus_interest_Name
    quarter_payment_method_list = quarterly_first_interest_Name
    month_quarter_payment_method_list = monthly_interest_quarter_onefouth_capital_Name
    once_Interest_once_principal_list = once_Interest_once_principal_by_day_Name
    payment_method_list = monthly_payment_method_list + day_payment_method_list + quarter_payment_method_list + month_quarter_payment_method_list + once_Interest_once_principal_list
    payment_method_dict={}.fromkeys(one_time_principal_by_day_Name, "按天一次性本息")
    payment_method_dict.update({}.fromkeys(monthly_first_interest_Name, "按月付息,到期还本"))
    payment_method_dict.update({}.fromkeys(ave_capital_plus_interest_Name, "按月等额本息"))
    payment_method_dict.update({}.fromkeys(quarterly_first_interest_Name, "按季分期"))
    payment_method_dict.update({}.fromkeys(monthly_interest_quarter_onefouth_capital_Name, "按月还息，季还1/4本金"))
    payment_method_dict.update({}.fromkeys(once_Interest_once_principal_by_day_Name, "一次付息，到期还本"))
    payment_method_dict.update({}.fromkeys(quarterly_ave_capital_plus_interest_Name, "按季等额本金"))
    
    neglect_payment_method_list = ["",None,"无","无担保"]


    
    
    
    
    
    #重复白名单
    platform_id_white_list = getPlatformIdList("repeatwhiteplatform_id.txt")
    #获得所有字段
    fields_list = getAllColumnsFromTable(cur_db1, srcdb_info)
    fields_number = len(fields_list)
    stringSQL = "SELECT `" +"`,`".join(fields_list) + "` FROM "+ srcdb_info
#     stringSQL = stringSQL + " WHERE `id` >= '262542'"
    print "正在从数据库传输数据回本地..."
    bids_number = cur_db1.execute(stringSQL)
    bidsPercentList = [floor(float(x) * bids_number / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)] 
    bad_bids_number = 0
    rows = cur_db1.fetchall()
    counter = 0
    fp = open("error_summary.txt","w")
    v={}
    platform_list = getDifferentFieldlist(srcdb_info, cur_db1, "site_id")
    errorplatform_dict = {}
    for platform in platform_list:
        errorplatform_dict[platform] = [0,0]
    print "cleaning: 0%"
    for row in rows:
        counter += 1
        if counter in bidsPercentList:
            print "cleaning: " + str((1 + bidsPercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
        for i in range(fields_number):
            v[fields_list[i]] = row[i]
        site_id = str(v["site_id"])
        errorplatform_dict[site_id][1] += 1
        #和还款方式有关
        v["payment_method"] = v["payment_method"].strip()
        if "项目描述 借款人基本信息 担保机构 资料图片" in v["payment_method"]:
            continue
        if v["payment_method"] in neglect_payment_method_list:
            bad_bids_number += 1
            errorplatform_dict[site_id][0] += 1
            print str(v["site_id"]) + "(" + str(v["project_id"]) + ")" +": " + "payment_method is blank."
            #continue
        try:
            v["annulized_rating"] = float(v["annulized_rating"])
        except:
            print str(v["site_id"]) + "(" + str(v["project_id"]) + ")" +": " + "annulized_rating is wrong."
            errorplatform_dict[site_id][0] += 1
            #continue
        if v["annulized_rating"] <= 1E-6:
            bad_bids_number += 1
            errorplatform_dict[site_id][0] += 1
            print str(v["site_id"]) + "(" + str(v["project_id"]) + ")" +": " + "annulized_rating is zero."
            #continue
        try: 
            v["loan_period"] = int(v["loan_period"])
        except:
            print str(v["site_id"]) + "(" + str(v["project_id"]) + ")" +": " + "loan_period is not integer."
            #continue
        #借款人列表以及相应的满标时间，发标时间
        v["investor"] = v["investor"].strip()
        if 0 == len(v["investor"]):
            bad_bids_number += 1
            errorplatform_dict[site_id][0] += 1
            print str(v["site_id"]) + "(" + str(v["project_id"]) + ")" +": " + "investor is blank."
            continue
        #删除investor中的可能重复字段
        if v["site_id"] not in platform_id_white_list:
            investor = v["investor"]
            investor_set = set()
            investor_list = investor.split("|")
            if len(investor_list) < 3:
                bad_bids_number += 1
                errorplatform_dict[site_id][0] += 1
                print str(v["site_id"]) + "(" + str(v["project_id"]) + ")" +": " + "investor is blank."
                continue
            investor_number = len(investor_list) / 3
            for i in range(investor_number):
                investor_str = investor_list[i * 3:(i + 1) * 3]
                investor_set.add("|".join(investor_str))
            investor_set_number = len(investor_set)
            repeat_time = investor_number / investor_set_number
            if repeat_time != 1:
                investor = "|".join(investor_set)
            v["investor"] = investor
        full_time= getInterestDate(0, 0, 0, v["investor"])[0] #计息时间
        if full_time <= 0:
            bad_bids_number += 1
            errorplatform_dict[site_id][0] += 1
            print str(v["site_id"]) + "(" + str(v["project_id"]) + ")" +": " + "full_time is invalid"
            #continue
#         count_date = getTimestampZero(full_time, 0, 0) + SECONDSPERWEEK
#         v["end_time"] = full_time #满标时间
#         first_time = getFirstDate(0, v["investor"])[0]  # 初次被投资时间
#         if first_time <= 0:
#             bad_bids_number += 1
#             errorplatform_dict[site_id][0] += 1
#             print str(v["site_id"]) + "(" + str(v["project_id"]) + ")" +": " + "first_time is invalid"
#             #continue
#         try: 
#             v["release_time"] = int(v["release_time"])
#         except:
#             v["release_time"] = 0
#         if v["release_time"] <= 0:
#             v["release_time"] = first_time
#         else:
#             v["release_time"] = min(v["release_time"], first_time) #放标时间
#         v["invested_amount"] = countGross(v["investor"], 3)
#         if v["invested_amount"] <= money_error:
#             bad_bids_number += 1
#             errorplatform_dict[site_id][0] += 1
#             print str(v["site_id"]) + "(" + str(v["project_id"]) + ")" +": " + "invested_amount is too small"
#             #continue
#         v["borrowing_amount"] = float(v["borrowing_amount"])
#         if v["invested_amount"] < FULLBIDPERCENT * v["borrowing_amount"]: #满标策略
#             bad_bids_number += 1
#             #print str(v["site_id"]) + "(" + str(v["project_id"]) + ")" +": " + "bid is not full"
#             #continue
#         v["borrowing_amount"] = v["invested_amount"]  # 暂时取投资额作为借款额，因为这里认为已经满标
#         #对还款方式的调整
#         v["payment_method"] = changePaymentMethod(v["payment_method"])
#         #对还款时间的调整
#         v["loan_period"] = changeLoanPeriod(v["payment_method"], v["loan_period"], monthly_interest_quarter_onefouth_capital_Name)   
#         #与天有关的付息手段
#         if v["loan_period"] < 28 or v["payment_method"] in day_payment_method_list:
#             v["payment_method"] = payment_method_dict[one_time_principal_by_day_Name[0]]   
#         #与月有关的付息手段
#         elif v["payment_method"] in ave_capital_plus_interest_Name: #等额本息
#             v["loan_period"] = int(round(float(v["loan_period"]) / DAYSPERMONTH)) * DAYSPERMONTH
#             v["payment_method"] = payment_method_dict[ave_capital_plus_interest_Name[0]]
#         else:
#             v["payment_method"] = payment_method_dict[v["payment_method"]]
#         #插入到project_info_clean_temp表中
#         if count_date > clean_date_thistime: #只保留上周之前的标
#             continue
#         fields_list_new = []
#         value_str = []
#         for _field in fields_list:
#             if _field != "id":
#                 fields_list_new.append(str(_field))
#                 value_str.append(str(v[_field]).replace("'","''"))
#         fields_list_new.append("date")
#         value_str.append(str(count_date))
#         stringSQL = "INSERT INTO " + dstdb_info + "(`" + "`,`".join(fields_list_new) + "`) VALUES('" + "','".join(value_str) + "')"
#         cur_db2.execute(stringSQL)
#         conn_db.commit()
    print "在满额限制为"+ str(FULLBIDPERCENT) + "的情况下, 只有" + "%.2f" % (100 * (1-float(bad_bids_number)/bids_number)) + "%的数据是可用的."
    print "共有" + str(bids_number - bad_bids_number) + "个标."
    (platform_id_list_sorted, repeat_value_list) = sortDictByValue(errorplatform_dict, columnIndex=0)
    fp = open("platform_id_list_sorted.txt", "w")
    for i in range(len(platform_id_list_sorted)):
        platform_id = platform_id_list_sorted[i]
        repeat_value = float(repeat_value_list[i]) / errorplatform_dict[platform_id][1]
        fp.write(platform_id + ": " + "%.4f" % float(repeat_value) + "\n")
    fp.close()
    #changeValue("./clean_date.xml","clean_date_lasttime",clean_date_thistime)
    closeCursors(cur_db1, cur_db2)
    closeConns(conn_db)
