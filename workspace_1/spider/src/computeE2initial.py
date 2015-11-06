#!/use/bin/python
#coding=utf-8

import time
from atbtools.header import *
from atbtools.computeTools import *
from math import ceil
if __name__ == "__main__":
    
    startTime = time.time()
    white_platform_list = ["宜人贷"]
    change_name_dict = {}
    change_name_dict["前海理想"] = "前海理想金融"
    white_field_list = ["weekly_total_investor_new", "weekly_total_investor_old"]
    field_team_list = ["weekly_total_investor_new", "weekly_total_investor"]
    last_weeks = 10
    zero_number_max = last_weeks - 2
    r_min = 0.8
    r_max = 1.2
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
    field_list = field_dict.keys()
    field_number = len(field_list)
    integer_field_list = ["weekly_total_borrower", "weekly_total_investor", "weekly_total_investor_new", "weekly_total_investor_old"]
    max1_field_list = ["weekly_top10_borrower_ratio", "weekly_top10_investor_ratio"]
    E2 = "e2_quantitative_data"
    E2_new = "wd_shujuinfo"
    V = "v_view"
    
    #获得连接        
    conn = getConn("127.0.0.1", "xiebo", "123456", "antoubao", 3306)
    cur = getCursors(conn)
    initializeCursors(cur)
    
    stringSQL = "TRUNCATE " + E2_new
    cur.execute(stringSQL)
    conn.commit()
    
    for field in field_list:
        field = field_dict[field]
        if field in integer_field_list:
            insertField(conn, cur, E2_new, field, "INT(11) DEFAULT NULL")
        else:
            insertField(conn, cur, E2_new, field, "DOUBLE DEFAULT NULL")
    insertField(conn, cur, E2_new, "level", "VARCHAR(255) DEFAULT NULL")
    
    insertField(conn, cur, E2_new, "weekly_total_investor_old", "INT(11) DEFAULT NULL")
    weekly_new_investor_index = field_list.index("weekly_new_investor")
    weekly_total_investor_index = field_list.index("weekly_total_investor")
    
    date_list = getInteger(getDifferentFieldlist(E2, cur, "date"))
    date_list.sort(reverse = True)
    date_list = date_list[:last_weeks] #从大到小
    date_number = len(date_list)
    
    value_dict = {}
    platform_name_list_E2 = getDifferentFieldlist(E2, cur, "platform_name")
    platform_name_list_V = getDifferentFieldlistByDate(V, cur, "platform_name", max(date_list))
    for platform_name in change_name_dict:
        if platform_name in platform_name_list_V:
            platform_name_list_V.remove(platform_name)
            platform_name_new = change_name_dict[platform_name]
            platform_name_list_V.append(change_name_dict[platform_name])
            stringSQL="UPDATE " + V + " SET `platform_name` = '"+str(platform_name_new)+"' WHERE `platform_name` = '" + platform_name + "'"
            cur.execute(stringSQL)
            conn.commit()
    
    platform_name_list = list(set(platform_name_list_E2) & set(platform_name_list_V))
    print len(platform_name_list)
    for platform_name in platform_name_list:
        value_dict[platform_name] = {}
        for field in field_list:
            value_dict[platform_name][field_dict[field]] = [0] * date_number
        value_dict[platform_name]["weekly_total_investor_old"] = [0] * date_number
    stringSQL = "SELECT `platform_name`, `date`, `" + "`, `".join(field_list) + "` FROM " + E2
    print "正在从数据库传输数据回本地..."
    cur.execute(stringSQL)
    rows = cur.fetchall()
    for row in rows:
        date = int(row[1])
        platform_name = row[0]
        if date in date_list and platform_name in platform_name_list:
            date_index = date_list.index(date)
            value_list = list(row[2:])
            weekly_total_investor_old = value_list[weekly_total_investor_index] - value_list[weekly_new_investor_index]
            for i in range(field_number):
                value_dict[platform_name][field_dict[field_list[i]]][date_index] = value_list[i]
            value_dict[platform_name]["weekly_total_investor_old"][date_index] = weekly_total_investor_old
    platform_number_initial = len(value_dict)
    print "初始一共有" + str(platform_number_initial) + "个平台."
    field_list = field_list + ["weekly_total_investor_old"]
    field_dict["weekly_total_investor_old"] = "weekly_total_investor_old"
    field_list = field_dict.values()
    weekly_new_investor_index = field_list.index("weekly_total_investor_new")
    weekly_total_investor_index = field_list.index("weekly_total_investor")
    weekly_old_investor_index = field_list.index("weekly_total_investor_old")
    
    bad_platform_list = []
    for platform_name in value_dict:
        if platform_name in white_platform_list:
            continue
        for field in field_list:
            if field in white_field_list:
                continue
            zero_number = checkZeroNumber(value_dict[platform_name][field])[0]
            if zero_number > zero_number_max:
                bad_platform_list.append(platform_name)
                break
    for platform_name in bad_platform_list:
        del value_dict[platform_name]
    platform_number = len(value_dict)
    print "筛选后一共有" + str(platform_number) + "个平台，百分比为" + str(float(platform_number)/platform_number_initial)
    for platform_name in value_dict:
        r_1 = r(r_min, r_max)
        for field in field_list:
            value_list = value_dict[platform_name][field]
            #线性填充
            zero_number, zero_position = checkZeroNumber(value_list)
            if platform_name not in white_platform_list and field not in white_field_list:
                while zero_number != 0:
                    index = zero_position[0]
                    point_list = []
                    for i in range(date_number):
                        small = index - i
                        big = index + i
                        if small >= 0:
                            if value_list[small] != 0:
                                point_list.append(small)
                        if big < date_number:
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
                value_list = [ceil(x) for x in value_list]
            if field in max1_field_list:
                value_list = [min(1.0, x) * 100 for x in value_list]
            value_dict[platform_name][field] = value_list
        #处理老投资人数
        for i in range(date_number):
            weekly_total_investor = value_dict[platform_name][field_list[weekly_total_investor_index]][i]
            weekly_new_investor = value_dict[platform_name][field_list[weekly_new_investor_index]][i]
            weekly_old_investor = weekly_total_investor - weekly_new_investor
            value_dict[platform_name][field_list[weekly_old_investor_index]][i] = weekly_old_investor
    #插入数据
    field_list_new = ["date", "platform_name"] + field_list
    for i in range(date_number):
        date = date_list[i]
        for platform_name in value_dict:
            value_list_new = [str(date), platform_name]
            for field in field_list:
                value_list_new.append(str(value_dict[platform_name][field][i]))
            stringSQL = "INSERT INTO " + E2_new + " (`" + "`, `".join(field_list_new) + "`) VALUES('" + "', '".join(value_list_new) + "')"
            cur.execute(stringSQL)
            conn.commit()
    closeCursors(cur)
    closeConns(conn)        
    print ""
    print "finished"
    endTime = time.time()
    print "The whole program costs " + str(endTime - startTime) + " seconds."        