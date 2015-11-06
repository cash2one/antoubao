# /usr/bin/python
# encoding=utf8
# 比较两个数据表的差别，所有因素取交集，同时取B/A的值

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from atbtools.paymentTools import *
from math import floor
import time
import hashlib

if __name__ == '__main__':
    
    conn_db = getConn(DBHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    
    E1 = "platform_quantitative_data_E1"
    A = "platform_quantitative_wdzj_weekly_A"
    B = "platform_quantitative_dcq_weekly_B"
    C = "platform_quantitative_jlsj_weekly_C"
    T06 = "Table_06_parameter_quantitative"
    
    table_dict = {}
    table_dict[E1] = "E1"
    table_dict[A] = "A"
    table_dict[B] = "B"
    table_dict[C] = "C"
    table_dict[T06] = "06"
    
    table_A_list = [E1, A, A, B]
    table_B_list = [T06, B, T06, T06]
#     table_A_list = [A, B]
#     table_B_list = [C, C]
    assert len(table_A_list) == len(table_B_list)
    table_pair_number = len(table_A_list)
    
    del_list = ["id", "platform_id", "platform_name", "date", "black"]
    merge_list = ["ave_annualized_return", "future4week_maturity", "weekly_outstanding_loan", "weekly_top10_lending", "weekly_top5_lending", "weekly_top10_investment", "weekly_top5_investment", "top10_ratio_loan", "top5_ratio_loan", "top10_ratio_investment", "top5_ratio_investment", "cash_flow_in", "weekly_total_investor", "weekly_total_borrower", "weekly_lending", "weekly_loan_period", "weekly_ave_investment_per_bid", "weekly_ave_lending_per_bid", "weekly_ave_bid_close_time", "investor_HHI", "borrower_HHI", "weekly_ave_investment_old", "weekly_new_investor", "weekly_ratio_new_old", "weekly_ave_investment", "borrower_growth", "investor_growth", "money_growth", "latest4week_lending", "outstanding_loan", "short_term_debt_ratio", "turnover_registered", "not_returned_yet", "turnover_period", "weekly_ave_lending_per_borrower", "market_share_growth"]
    
    for i in range(table_pair_number):
        table_A = table_A_list[i]
        table_B = table_B_list[i]
        table_name = "compare_" + table_dict[table_A] + "_" + table_dict[table_B]
        
        #确定两个表的交集（时间、字段）
        field_list_A = getAllColumnsFromTable(cur_db, table_A, del_list, merge_list)
        field_list_B = getAllColumnsFromTable(cur_db, table_B, del_list, merge_list)
        field_list = list(set(field_list_A) & set(field_list_B))
        date_list_A = getDifferentFieldlist(table_A, cur_db, "date")
        date_list_B = getDifferentFieldlist(table_B, cur_db, "date")
        date_list = sorted(list(set(date_list_A) & set(date_list_B)))
#         date_list = [1444492800]
        #新建表
        stringSQL = "DROP TABLE IF EXISTS " + table_name
        cur_db.execute(stringSQL)
        conn_db.commit()
        stringSQL = "CREATE TABLE " + table_name + "(id INT(11) PRIMARY KEY AUTO_INCREMENT, date BIGINT(20) DEFAULT NULL, platform_id VARCHAR(255) DEFAULT NULL, platform_name VARCHAR(255) DEFAULT NULL);"
        cur_db.execute(stringSQL)
        conn_db.commit()
        for field in field_list:
            insertField(conn_db, cur_db, table_name, field, "DOUBLE DEFAULT NULL")
        
        hasE1 = 0
        if "E1" in table_name:
            hasE1 = 1
            insertField(conn_db, cur_db, table_name, "source", "VARCHAR(255) DEFAULT NULL")
        #逐一计算    
        for date in date_list:
            print date
            platform_name_list_A = getDifferentFieldlistByDate(table_A, cur_db, "platform_name", date)
            platform_name_list_B = getDifferentFieldlistByDate(table_B, cur_db, "platform_name", date)
            platform_name_list = list(set(platform_name_list_A) & set(platform_name_list_B))
            for platform_name in platform_name_list:
                platform_id = hashlib.md5(platform_name).hexdigest()[0:10]
                value_list_A = getFieldsListFromTableByNameByDate(cur_db, table_A, platform_name, date, field_list)
                value_list_B = getFieldsListFromTableByNameByDate(cur_db, table_B, platform_name, date, field_list)
                value_list = divList(value_list_A, value_list_B) #B/A
                value_list_new = getString(value_list + [date, platform_name, platform_id])
                field_list_new = field_list + ["date", "platform_name", "platform_id"]
                if hasE1 == 1:
                    stringSQL = "SELECT `source` FROM " + E1 + " WHERE `date` = '" + str(date) + "' AND `platform_name` = '" + str(platform_name) + "'"
                    if cur_db.execute(stringSQL) != 0:
                        source = cur_db.fetchone()[0]
                        field_list_new = field_list_new + ["source"]
                        value_list_new = value_list_new + [source]
                stringSQL = "INSERT INTO " + table_name + "(`" + "`,`".join(field_list_new) + "`) VALUES('" + "','".join(value_list_new) + "')"
                cur_db.execute(stringSQL)
                conn_db.commit()
        print table_name + "对比完毕."
        print 
    closeCursors(cur_db)
    closeConns(conn_db)
