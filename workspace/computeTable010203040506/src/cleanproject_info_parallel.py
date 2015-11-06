# /usr/bin/python
# encoding=utf8
# 将project_info中的脏数据去掉，方便后续处理

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from atbtools.xmlTools import *
from atbtools.paymentTools import *
from math import floor
from processing import Process
import time  

def readSQLReturn(_args):
    v={}
    [row_start, row_end, cur_db] = _args
    print row_start, row_end, cur_db
    for row in rows[row_start:row_end]:
        for i in range(fields_number):
            v[fields_list[i]] = row[i]
        #借款人列表以及相应的满标时间，发标时间
        v["investor"] = v["investor"].strip()
        if 0 == len(v["investor"]):
            bad_bids_number += 1
            print str(v["id"]) +": " + "investor is blank."
            fp.write("investor is blank : " + str(v["id"]))
            fp.write("\n")
            continue
        #删除investor中的可能重复字段
        if v["site_id"] not in platform_id_white_list:
            investor = v["investor"]
            investor_set = set()
            investor_list = investor.split("|")
            if len(investor_list) < 3:
                bad_bids_number += 1
                print str(v["id"]) +": " + "investor is blank."
                fp.write("investor is blank : " + str(v["id"]))
                fp.write("\n")
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
            print str(v["id"]) +": " + "full_time is invalid"
            fp.write("full_time is invalid : " + str(v["id"]))
            fp.write("\n")
            continue
        count_date = getTimestampZero(full_time, 0, 0) + SECONDSPERWEEK
        v["end_time"] = full_time #满标时间
        first_time = getFirstDate(0, v["investor"])[0]  # 初次被投资时间
        if first_time <= 0:
            print str(v["id"]) +": " + "first_time is invalid"
            fp.write("first_time is invalid : " + str(v["id"]))
            fp.write("\n")
            continue
        try: 
            v["release_time"] = int(v["release_time"])
        except:
            v["release_time"] = 0
        if v["release_time"] <= 0:
            v["release_time"] = first_time
        else:
            v["release_time"] = min(v["release_time"], first_time) #放标时间
        #和还款方式有关
        v["payment_method"] = v["payment_method"].strip()
        if v["payment_method"] in neglect_payment_method_list:
            print str(v["id"]) +": " + "payment_method is blank."
            fp.write("payment_method is blank : " + str(v["id"]))
            fp.write("\n")
            continue
        try:
            v["annulized_rating"] = float(v["annulized_rating"])
        except:
            print str(v["id"]) +": " + "annulized_rating is wrong."
            fp.write("annulized_rating is wrong : " + str(v["id"]))
            fp.write("\n")
            continue
        if v["annulized_rating"] <= 1E-6:
            print str(v["id"]) +": " + "annulized_rating is zero."
            fp.write("annulized_rating is wrong : " + str(v["id"]))
            fp.write("\n")
            continue
        try: 
            v["loan_period"] = int(v["loan_period"])
        except:
            print str(v["id"]) +": " + "loan_period is not integer."
            fp.write("loan_period is wrong : " + str(v["id"]))
            fp.write("\n")
            continue
        v["invested_amount"] = countGross(v["investor"], 3)
        if v["invested_amount"] <= money_error:
            print str(v["id"]) +": " + "invested_amount is too small"
            fp.write("invested_amount is too small : " + str(v["id"]))
            fp.write("\n")
            continue
        v["borrowing_amount"] = float(v["borrowing_amount"])
        if v["invested_amount"] < FULLBIDPERCENT * v["borrowing_amount"]: #满标策略
            print str(v["id"]) +": " + "bid is not full"
            fp.write("bid is not full : " + str(v["id"]))
            fp.write("\n")
            continue
        v["borrowing_amount"] = v["invested_amount"]  # 暂时取投资额作为借款额，因为这里认为已经满标
        #对还款方式的调整
        v["payment_method"] = changePaymentMethod(v["payment_method"])
        #对还款时间的调整
        v["loan_period"] = changeLoanPeriod(v["payment_method"], v["loan_period"], monthly_interest_quarter_onefouth_capital_Name) 
        #与天有关的付息手段
        if v["loan_period"] < 28 or v["payment_method"] in day_payment_method_list:
            v["payment_method"] = payment_method_dict[one_time_principal_by_day_Name[0]]   
        #与月有关的付息手段
        elif v["payment_method"] in ave_capital_plus_interest_Name: #等额本息
            v["loan_period"] = int(round(float(v["loan_period"]) / DAYSPERMONTH)) * DAYSPERMONTH
            v["payment_method"] = payment_method_dict[ave_capital_plus_interest_Name[0]]
        else:
            v["payment_method"] = payment_method_dict[v["payment_method"]]
        #插入到project_info_clean_temp表中
        if count_date > clean_date_thistime: #只保留上周之前的标
            continue
        fields_list_new = []
        value_str = []
        for _field in fields_list:
            if _field != "id":
                fields_list_new.append(str(_field))
                value_str.append(str(v[_field]).replace("'","''"))
        fields_list_new.append("date")
        value_str.append(str(count_date))
        stringSQL = "INSERT INTO " + dstdb_info + "(`" + "`,`".join(fields_list_new) + "`) VALUES('" + "','".join(value_str) + "')"
        cur_db.execute(stringSQL)
        conn_db.commit()
        platform_id_set.add(v["site_id"])  
    
if __name__ == '__main__':
    # 确定金钱的误差0.01元
    money_error = 0.01 / MONEYUNIT
    # 获取连接    
    srcdb_info = "project_info"
    dstdb_info = "project_info_clean"
    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    #清理数据的时间为每周一次，且每次只保留上一周满标的数据
    clean_date_now = int(time.time())
    clean_date_lasttime=int(getValue("./clean_date.xml","clean_date_lasttime"))
    if clean_date_now - clean_date_lasttime < SECONDSPERWEEK:
        print "上一周的数据已经清理过了，不需要再清理"
        exit(0)
    else:
        clean_date_thistime = getTimestampZero(clean_date_now, 0, 0) - SECONDSPERWEEK
        cur_db.execute("TRUNCATE " + dstdb_info)
        conn_db.commit()
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
    
    #查找project_info中所有未涉及到的还款方式
    neglect_payment_method_list = ["",None,"无","无担保"]
    stringSQL = "SELECT DISTINCT payment_method FROM " + srcdb_info
    cur_db.execute(stringSQL)
    for field_temp in cur_db.fetchall():
        _field = field_temp[0]
        if "按月结算收益" in str(_field):
            _field = "按月结算收益"
        if "等额本息" in str(_field):
            _field = "等额本息"
        if "天标" in str(_field):
            _field = "天标"
        if "每月付息到期还本" in str(_field):
            _field = "每月付息到期还本"
        if "复投" in str(_field):
            _field = "每月付息到期还本"    
        if "到期还本息" in str(_field):
            _field = "每月付息到期还本"    
        if "到期还本付息" in str(_field):
            _field = "到期还本付息"    
        if "到期还款" in str(_field):
            _field = "到期还本付息"  
        if "每日付息" in str(_field):
            _field = "到期还本付息"  
        if "日息转本金" in str(_field):
            _field = "到期还本付息"     
        if _field not in neglect_payment_method_list and _field not in payment_method_dict.keys():
            print "'" + _field + "' is not in our payment_methods."
            exit(1)
    print "所有还款方式都已经备案."

    #获得所有字段
    fields_list = getAllColumnsFromTable(cur_db, srcdb_info)
    fields_number = len(fields_list)
    stringSQL = "SELECT `" +"`,`".join(fields_list) + "` FROM "+ srcdb_info
    stringSQL = stringSQL + " WHERE `id` < '100'"
    print "正在从数据库传输数据回本地..."
    bids_number = cur_db.execute(stringSQL)
    bidsPercentList = [floor(float(x) * bids_number / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)] 
    bad_bids_number = 0
    rows = cur_db.fetchall()
    platform_id_set = set()
    fp = open("error_summary.txt","w")
    bad_bids_number = 0
    
    bids_number_pertime = bids_number / PLATFORMDIVISION
    bids_number_reminder = bids_number - bids_number_pertime * PLATFORMDIVISION 
    start_index = []
    end_index = []
    start = 0
    end = 0
    for i in range(PLATFORMDIVISION): 
        start_index.append(start)
        end = start + bids_number_pertime
        if bids_number_reminder > 0:
            end += 1
            bids_number_reminder -= 1
        end_index.append(end)
        start = end
    cur_db_list = getCursors(conn_db, n=PLATFORMDIVISION)
    print cur_db_list
    #重复白名单
    platform_id_white_list = getPlatformIdList("repeatwhiteplatform_id.txt")
    for i in range(PLATFORMDIVISION):
        j=Process(target=readSQLReturn,args=[[start_index[i], end_index[i], cur_db_list[i]]])  
        j.start()
    j.join() 
    print "共有" + str(bids_number) + "个标."
    stringSQL = "SELECT count(*) FROM " + dstdb_info
    cur_db.execute(stringSQL)
    good_number = cur_db.fetchone()[0]
    print "在满额限制为"+ str(FULLBIDPERCENT) + "的情况下, 只有" + "%.2f" % (100 * (float(good_number)/bids_number)) + "%的数据是可用的."
    #changeValue("./clean_date.xml","clean_date_lasttime",clean_date_thistime)
    fp.close()
    #将所有的platform_id输出到文件
    fp = open("platform_id_list_info.txt","w")
    for platform_id in platform_id_set:
        fp.write(str(platform_id))
        fp.write("\n")
    fp.close()
    closeCursors(cur_db)
    closeConns(conn_db)