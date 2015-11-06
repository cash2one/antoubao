# /usr/bin/python
# encoding=utf8

import sys
from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.paymentTools import *
from atbtools.computeTools import *

if __name__ == '__main__':
    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    
    #组装还款方式
    (one_time_principal_by_day_Name, monthly_first_interest_Name, ave_capital_plus_interest_Name, quarterly_first_interest_Name, monthly_interest_quarter_onefouth_capital_Name, once_Interest_once_principal_by_day_Name, quarterly_ave_capital_plus_interest_Name, yearly_first_interest_Name) = getPaymentMethodName()
    day_payment_method_list = one_time_principal_by_day_Name
    monthly_payment_method_list = monthly_first_interest_Name + ave_capital_plus_interest_Name
    quarter_payment_method_list = quarterly_first_interest_Name
    month_quarter_payment_method_list = monthly_interest_quarter_onefouth_capital_Name
    once_Interest_once_principal_list = once_Interest_once_principal_by_day_Name
    yearly_first_interest_list = yearly_first_interest_Name
    payment_method_list = monthly_payment_method_list + day_payment_method_list + quarter_payment_method_list + month_quarter_payment_method_list + once_Interest_once_principal_list
    payment_method_dict={}.fromkeys(one_time_principal_by_day_Name, "按天一次性本息")
    payment_method_dict.update({}.fromkeys(monthly_first_interest_Name, "按月付息,到期还本"))
    payment_method_dict.update({}.fromkeys(ave_capital_plus_interest_Name, "按月等额本息"))
    payment_method_dict.update({}.fromkeys(quarterly_first_interest_Name, "按季分期"))
    payment_method_dict.update({}.fromkeys(monthly_interest_quarter_onefouth_capital_Name, "按月还息，季还1/4本金"))
    payment_method_dict.update({}.fromkeys(once_Interest_once_principal_by_day_Name, "一次付息，到期还本"))
    payment_method_dict.update({}.fromkeys(quarterly_ave_capital_plus_interest_Name, "按季等额本金"))
    payment_method_dict.update({}.fromkeys(yearly_first_interest_list, "按年付息到期还本"))
    
    #暂时无法修正
#     platform_id_del_list = getPlatformIdList("del_platform_id.txt")
    
    #查找project_info中所有未涉及到的还款方式
    neglect_payment_method_list = ["",None,"无","无担保"]
    OOKK = 1
    for project_info_initial in "abcdefghijklmnopqrstuvwxyz0":
        table_name = "project_info" + "_" + project_info_initial
        print "正在检查'" + table_name + "'表格..."
        stringSQL = "SELECT DISTINCT payment_method FROM " + table_name
        cur_db.execute(stringSQL)
        count = 0
        OK = 1
        for field_temp in cur_db.fetchall():
            _field = changePaymentMethod(field_temp[0])
            if _field not in neglect_payment_method_list and _field not in payment_method_dict.keys() and "项目描述 借款人基本信息 担保机构 资料图片" not in _field and "项目描述 活动细则 担保机构" not in _field and "本期专享奖品" not in _field: # and "2015-" not in _field:
                count += 1
                OOKK = 0
                OK = 0
                print str(count) + ": '" + _field + "' is not in our payment_methods."
                print "UTF-8编码: " + repr(_field)
                print 
        if OK == 1:
            print "所有还款方式都已经备案."
        else:
            print "共有" + str(count) + "个还款方式不在我们的记录中."
        print
    if OOKK == 0:
        exit(1)
    else:
        print 
        print "恭喜恭喜."    
    closeCursors(cur_db)
    closeConns(conn_db)