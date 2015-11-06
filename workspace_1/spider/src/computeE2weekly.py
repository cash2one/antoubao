#!/use/bin/python
#coding=utf-8

"""
E2：历史（A）不动，A + B = A，每个站都历史数据完整（只展示最近10周的数据）
1.将新E2所有的历史平台A用最近四周的数据线性插值*r(0.8, 1.2)算出最新的一周；
2.对于所有的历史平台，如果在老E2中有本周数据（不为零或None），那么再*r(0.8, 1.2)重新填一遍
3.取老E2和A的差集，找到差集中所有最近（10+N）周内有（8+N）周有数据的站B；
4.对于B，按照r(0.8, 1.2)原则和线性插值来新增（10+N）周的数据；
5.取出最近10周的数据进入数据库。

"""
import time
from atbtools.header import *
from atbtools.computeTools import *
from math import ceil
if __name__ == "__main__":
    
    startTime = time.time()
    
    #数据库定义
    V = "V_view" #ddpt-data
    VIEW_MOBILE = "view_mobile" #dev-x1
    Y = "total_status" #db-x1
    E2_old = "E2_quantitative_data" #dev-x1
    E2_new = "wd_shujuinfo_history" #local
    E2_online = "wd_shujuinfo" #local
    T = "wd_data_platform_score_history" #local
    T_online = "wd_data_platform_score" #local
    
    #设置连接
    conn_db = getConn(DBHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    conn_ddpt = getConn(DDPT_DATAHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_ddpt = getCursors(conn_ddpt)
    conn_dev = getConn(DEVHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_dev = getCursors(conn_dev)
    conn_local = getConn("127.0.0.1", "xiebo", "123456", "antoubao", 3306)
    cur_local = getCursors(conn_local)
    initializeCursors(cur_db, cur_ddpt, cur_dev, cur_local)
    
    #所有数据的起始位点：2015/6/7 0:0:0
    initial_date = 1433606400
    #不需要经过非零个数检查的平台
    white_platform_list = ["宜人贷"]
    #平台名称更正
    change_name_dict = {}
    change_name_dict["前海理想"] = "前海理想金融"
    #不检查非零个数的字段
    white_field_list = ["weekly_total_investor_new", "weekly_total_investor_old"]
    #同时乘以相同的随机数
    field_team_list = ["weekly_total_investor_new", "weekly_total_investor"]
    
    initial_weeks = 10
    date_list = []
    stringSQL = "SELECT DISTINCT `date` FROM " + V + " ORDER BY `date` DESC"
    cur_ddpt.execute(stringSQL)
    for field_temp in cur_ddpt.fetchall():
        date_list.append(field_temp[0])
    this_date = int(date_list[0]) #本周
    last_date = int(date_list[1]) #上一周
    last4_week_list = getInteger(date_list[1 : 5])[::-1] #过去四周
    #相比历史起点的当前周数
    last_weeks = (this_date - initial_date) / SECONDSPERWEEK + 1
    last10_date = date_list[:10][-1]
    date_list = date_list[:last_weeks][::-1]
    #设置有效数据的时候为零项个数的最大值（与周数有关）
    zero_number_max = last_weeks - 2
    #随机数的最大值和最小值
    r_min = 0.8
    r_max = 1.2
    #字段的名称转化
    field_dict = {}
    field_dict["weekly_lending"] = "weekly_lending"
    field_dict["weekly_total_borrower"] = "weekly_total_borrower"
    field_dict["weekly_total_investor"] = "weekly_total_investor"
    field_dict["weekly_new_investor"] = "weekly_total_investor_new"
    field_dict["ave_annualized_return"] = "ave_annualized_return"
    field_dict["weekly_loan_period"] = "weekly_loan_period"
#     field_dict["investor_HHI"] = "investor_HHI"
#     field_dict["borrower_HHI"] = "borrower_HHI"
    field_dict["top10_ratio_investment"] = "weekly_top10_borrower_ratio"
    field_dict["top10_ratio_loan"] = "weekly_top10_investor_ratio"
    field_dict["weekly_outstanding_loan"] = "weekly_outstanding_loan"
    field_dict["weekly_ave_bid_close_time"] = "weekly_ave_bid_close_time"
    field_dict["weekly_ave_lending_per_borrower"] = "weekly_ave_lending_per_borrower"
    field_dict["weekly_ave_investment"] = "weekly_ave_investment_per_investor"
    field_dict["weekly_ave_lending_per_bid"] = "weekly_ave_lending_per_bid"
    field_dict["weekly_ave_investment_per_bid"] = "weekly_ave_investment_per_bid"
    field_list_old = field_dict.keys()
    weekly_new_investor_index_old = field_list_old.index("weekly_new_investor")
    weekly_total_investor_index_old = field_list_old.index("weekly_total_investor")
    field_number = len(field_list_old)
    field_list_new = field_dict.values()
    weekly_new_investor_index = field_list_new.index("weekly_total_investor_new")
    weekly_total_investor_index = field_list_new.index("weekly_total_investor")
    field_list_total = field_list_new + ["weekly_total_investor_old"]
    weekly_new_investor_index_new = field_list_new.index("weekly_total_investor_new")
    weekly_total_investor_index_new = field_list_new.index("weekly_total_investor")
    weekly_old_investor_index_new = field_list_total.index("weekly_total_investor_old")
    field_number_total = len(field_list_total)
    #整数的字段
    integer_field_list = ["weekly_total_borrower", "weekly_total_investor", "weekly_total_investor_new", "weekly_total_investor_old"]
    #最大值为1的字段
    max1_field_list = ["weekly_top10_borrower_ratio", "weekly_top10_investor_ratio"]
    #删除本周数据，后面会重新填充
    stringSQL = "DELETE FROM " + E2_new + " WHERE `date` = '" + str(this_date) + "'"
    print stringSQL
    ret = cur_local.execute(stringSQL)
    if ret != 0 :
        print "会从E2_history中删除数据，请谨慎操作."
        #exit(0)
    conn_local.commit()

    #插入字段，一般情况下不用
#     for field in field_list_total:
#         field = field_dict[field]
#         if field in integer_field_list:
#             insertField(conn_local, cur_local, E2_new, field, "INT(11) DEFAULT NULL")
#         else:
#             insertField(conn_local, cur_local, E2_new, field, "DOUBLE DEFAULT NULL")
#     insertField(conn_local, cur_local, E2_new, "level", "VARCHAR(255) DEFAULT NULL")
    
    #1.将新E2所有的历史平台A用最近四周的数据线性插值出最新的一周；
    stringSQL = "SELECT `date`, `platform_name`, `" +"`,`".join(field_list_new) + "` FROM "+ E2_new + " WHERE `date` <= '" + str(last_date) + "' AND `date` >= '" + str(last_date - 3 * SECONDSPERWEEK) + "'"
    ret = cur_local.execute(stringSQL)
    rows = cur_local.fetchall()
    last4_dict = {}
    for row in rows:
        date = int(row[0])
        date_index = last4_week_list.index(date)
        platform_name = str(row[1])
        if platform_name not in last4_dict:
            last4_dict[platform_name] = {}
            for field in field_list_new:
                last4_dict[platform_name][field] = [0] * 4
        value_list = getFloat(row[2:])
        for i in range(field_number):
            last4_dict[platform_name][field_list_new[i]][date_index] = value_list[i]
    for platform_name in last4_dict:
        r_1 = r(r_min, r_max)
        value_list = []
        for field in field_list_new:
            value = abs(forecastLinearValue(last4_dict[platform_name][field])[3] * r(r_min, r_max))
            if field in field_team_list:
                value *= r_1
            else:
                value *= r(r_min, r_max)
            if field in integer_field_list:
                value = int(ceil(value))
            if field in max1_field_list:
                value = min(100, value)
            value_list.append(value)
        value_list[weekly_new_investor_index] = min(value_list[weekly_new_investor_index], value_list[weekly_total_investor_index])
        value_list[weekly_new_investor_index] = max(value_list[weekly_new_investor_index], 0)
        weekly_total_investor_old = value_list[weekly_total_investor_index] - value_list[weekly_new_investor_index]
        value_list = getString(value_list)
        stringSQL = "INSERT INTO " + E2_new + "(`" + "`,`".join(field_list_new + ['date', 'platform_name', 'weekly_total_investor_old']) + "`) VALUES('" + "','".join(value_list + [str(this_date), platform_name, str(weekly_total_investor_old)]) + "')"
        cur_local.execute(stringSQL)
        conn_local.commit()
    platform_name_A_list = getDifferentFieldlist(E2_new, cur_local, "platform_name")
    print "数据库原有" + str(len(platform_name_A_list)) + "个平台."

    #2.对于所有的历史平台，如果在老E2中有本周数据（不为零或None），那么再*r(0.8, 1.2)重新填一遍
    for platform_name in platform_name_A_list:
        stringSQL = "SELECT `" +"`,`".join(field_list_old) + "` FROM "+ E2_old + " WHERE `date` = '" + str(this_date) + "' AND `platform_name` = '" + platform_name + "'"
        ret = cur_dev.execute(stringSQL)
        r_1 = r(r_min, r_max)
        if ret != 0:
            key_value_str = []
            row = cur_dev.fetchone()
            for i in range(field_number):
                value = row[i]
                if value == 0 or value == None:
                    continue
                field = field_dict[field_list_old[i]]
                if field in field_team_list:
                    value *= r_1
                else:
                    value *= r(r_min, r_max)
                if field in integer_field_list:
                    value = int(ceil(value))
                if field in max1_field_list:
                    value = min(1.0, value) * 100
                key_value_str.append("`" + field + "` = '" + str(value) + "'")
            stringSQL = "UPDATE " + E2_new + " SET " + ",".join(key_value_str) + " WHERE `platform_name` = '" + platform_name + "' AND `date` = '" + str(this_date) + "'"    
#             print stringSQL
            cur_local.execute(stringSQL)
            conn_local.commit()
            stringSQL = "UPDATE " + E2_new + " SET `weekly_total_investor_old` = `weekly_total_investor` - `weekly_total_investor_new` WHERE `platform_name` = '" + platform_name + "' AND `date` = '" + str(this_date) + "'"    
            cur_local.execute(stringSQL)
            conn_local.commit()
    
    #3.取老E2和A的差集，找到差集中所有最近（10+N）周内有（8+N）周有数据的站B；
    platform_name_E2_list = getDifferentFieldlist(E2_old, cur_dev, "platform_name")
    for platform_name in change_name_dict:
        if platform_name in platform_name_A_list:
            platform_name_A_list.remove(platform_name)
            platform_name_A_list.append(change_name_dict[platform_name])
    platform_name_add_list = list(set(platform_name_E2_list) - set(platform_name_A_list))
    value_dict = {}
    for platform_name in platform_name_add_list:
        value_dict[platform_name] = {}
        for field in field_list_old:
            value_dict[platform_name][field_dict[field]] = [0] * last_weeks
        value_dict[platform_name]["weekly_total_investor_old"] = [0] * last_weeks

    stringSQL = "SELECT `platform_name`, `date`, `" + "`, `".join(field_list_old) + "` FROM " + E2_old
    print "正在从数据库传输数据回本地..."
    cur_dev.execute(stringSQL)
    rows = cur_dev.fetchall()
    for row in rows:
        platform_name = row[0]
        date = int(row[1])
        if date in date_list and platform_name in platform_name_add_list:
            date_index = date_list.index(date)
            value_list = list(row[2:])
            weekly_total_investor_old = value_list[weekly_total_investor_index_old] - value_list[weekly_new_investor_index_old]
            for i in range(field_number):
                value_dict[platform_name][field_dict[field_list_old[i]]][date_index] = value_list[i]
            value_dict[platform_name]["weekly_total_investor_old"][date_index] = weekly_total_investor_old
    platform_number_initial = len(value_dict)
    print "初始一共有" + str(platform_number_initial) + "个等待添加平台."
    
    bad_platform_list = []
    for platform_name in value_dict:
        if platform_name in white_platform_list:
            continue
        for field in field_list_total:
            if field in white_field_list:
                continue
            zero_number = checkZeroNumber(value_dict[platform_name][field])[0]
            if zero_number > zero_number_max:
                bad_platform_list.append(platform_name)
                break
    for platform_name in bad_platform_list:
        del value_dict[platform_name]
    platform_number = len(value_dict)
    print "筛选后一共有" + str(platform_number) + "个平台，比例为" + str(float(platform_number)/platform_number_initial)
    
    #4.对于B，按照r(0.8, 1.2)原则新增（10+N）周的数据；
    for platform_name in value_dict:
        r_1 = r(r_min, r_max)
        for field in field_list_total:
            value_list = value_dict[platform_name][field]
            #线性填充
            zero_number, zero_position = checkZeroNumber(value_list)
            if platform_name not in white_platform_list and field not in white_field_list:
                while zero_number != 0:
                    index = zero_position[0]
                    point_list = []
                    for i in range(last_weeks):
                        small = index - i
                        big = index + i
                        if small >= 0:
                            if value_list[small] != 0:
                                point_list.append(small)
                        if big < last_weeks:
                            if value_list[big] != 0:
                                point_list.append(big)
                    point_list_number = len(point_list)
                    value = calculateLinearValue(index,value_list,point_list[0],point_list[1])
                    if value_list[index] <= 0 :
                        for j in range(1, point_list_number - 1):
                            value = calculateLinearValue(index,value_list,point_list[j],point_list[j+1])
                            if value > 0 :
                                value_list[index] = value
                                break
                        else:
                            value_list[index] = getListAverage(value_list, 0)
                    else:
                        value_list[index] = value
                    zero_number, zero_position = checkZeroNumber(value_list)
            #随机填充
            if field in field_team_list:
                value_list = [x * r_1 for x in value_list]
            else:
                value_list = [x * r(r_min, r_max) for x in value_list]
            #特殊处理
            if field in integer_field_list:
                value_list = [int(ceil(x)) for x in value_list]
            if field in max1_field_list:
                value_list = [min(1.0, x) * 100 for x in value_list]
            value_dict[platform_name][field] = value_list
        #处理老投资人数
        for i in range(last_weeks):
            weekly_total_investor = value_dict[platform_name][field_list_total[weekly_total_investor_index_new]][i]
            weekly_new_investor = value_dict[platform_name][field_list_total[weekly_new_investor_index_new]][i]
            weekly_old_investor = weekly_total_investor - weekly_new_investor
            value_dict[platform_name][field_list_total[weekly_old_investor_index_new]][i] = weekly_old_investor
    
    for platform_name in change_name_dict:
        if platform_name in value_dict:
            value_dict[change_name_dict[platform_name]] = value_dict[platform_name]
            del value_dict[platform_name]
    #插入数据
    field_list_new = ["date", "platform_name"] + field_list_total
    for i in range(last_weeks):
        date = date_list[i]
        for platform_name in value_dict:
            value_list_new = [str(date), platform_name]
            for field in field_list_total:
                value_list_new.append(str(value_dict[platform_name][field][i]))
            stringSQL = "INSERT INTO " + E2_new + " (`" + "`, `".join(field_list_new) + "`) VALUES('" + "', '".join(value_list_new) + "')"
            cur_local.execute(stringSQL)
            conn_local.commit()
    
#     #5.取出最近10周的数据进入数据库。
#     stringSQL = "DELETE FROM " + E2_online
#     cur_local.execute(stringSQL)
#     conn_local.commit()
#     
#     this_date = date_list[-1]
#     field_list_total = getAllColumnsFromTable(cur_local, E2_new, del_list = ["Id"])
#     stringSQL = "SELECT `"+"`, `".join(field_list_total) + "` FROM " +  E2_new + " WHERE `date` >= '" + str(last10_date) + "'"
#     ret = cur_local.execute(stringSQL)
#     print ret
#     rows = cur_local.fetchall()
#     for row in rows:
#         value_list = getString(row)
#         stringSQL = "INSERT INTO " + E2_online + " (`" + "`, `".join(field_list_total) + "`) VALUES('" + "', '".join(value_list) + "')"
# #         print stringSQL
#         cur_local.execute(stringSQL)
#         conn_local.commit()
                
    closeCursors(cur_db, cur_ddpt, cur_dev, cur_local)
    closeConns(conn_db, conn_ddpt, cur_dev, cur_local)        
    print ""
    print "finished"
    endTime = time.time()
    print "The whole program costs " + str(endTime - startTime) + " seconds."        