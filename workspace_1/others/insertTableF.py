#!/use/bin/python
# coding=utf-8

import xlrd
from header import *
from computeTools import *
from mysqlTools import *
import re
import sys

if __name__ == "__main__":
    # 预处理
    reload(sys)
    sys.setdefaultencoding("utf-8")
    startTime = time.time()
    conn = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur = getCursors(conn)
    initializeCursors(cur)
    SRCDB = "platform_qualitative_F"   

    # 得到表F的所有字段
    stringSQL = "SHOW FULL COLUMNS FROM " + SRCDB
    cur.execute(stringSQL)
    arrKeys = []
    for col in cur.fetchall():
        if (col[0] == "id"):
            continue
        arrKeys.append(col[0])
    compensation_dict = {}
    compensation_dict["全体垫付本息"] = 1
    compensation_dict["VIP或部分会员垫付本息"] = 0.8
    compensation_dict["垫付全部本金"] = 0.8
    compensation_dict["垫付80%-99%本金"] = 0.7
    compensation_dict["垫付50%-79%本金"] = 0.5
    compensation_dict["其他垫付手段"] = 0.3
    compensation_dict["不清楚"] = 0.3
    compensation_dict["不垫付"] = 0
    compensation_list = compensation_dict.keys()
    # 顶级域名的正则表达式
    pattern_str = "^https?:\/\/(?:www\.)?([^.]+).*$"
    domain_name_pattern = re.compile(pattern_str, re.IGNORECASE)
    # 操作excel表
    excel_filename_list = ["Fforfutherupdate1.xlsx", "Fforfutherupdate2.xlsx"]
    for excel_filename in excel_filename_list:
        bk = xlrd.open_workbook(excel_filename, 'r')
        try:
            sheet = bk.sheet_by_index(0)  # 通过sheet索引获得sheet对象
            # sheet = bk.sheet_by_name("Sheet1") #通过sheet名字来获取，
        except:
            print "no sheet in %s named Sheet1" % excel_filename
        
        # 整合excel表中所有数据
        nrows = sheet.nrows  # 行总数  
        ncols = sheet.ncols  # 列总数 
        titles = sheet.row_values(0)
        platform_name_position = titles.index('platform_name')
        advanced_repayment_position = titles.index('advanced_repayment')
        platform_names = sheet.col_values(platform_name_position)[1:]
        platform_number = len(platform_names)
        F_dict = {}
        for platform_name in platform_names:
            F_dict[platform_name] = {}
        for i in range(0, ncols): 
            key = sheet.cell_value(0, i)
            if key in arrKeys:
                row_datas = sheet.col_values(i)
                for j in range(1, platform_number + 1):
                    value = row_datas[j]
                    if "" == value:
                        continue
                    platform_name = sheet.cell_value(j, platform_name_position)
                    F_dict[platform_name][key] = value
                    # 特殊值处理
                    if key == "website" :
                        F_dict[platform_name]["platform_id"] = domain_name_pattern.findall(value)[0]
                    if key =="established_date":
                        print str(value)
                        if str(value) == "未登记":
                            F_dict[platform_name]["established_date"] = "未登记"
                        else:
                            date_tuple = xlrd.xldate_as_tuple(value, 0)
                            date_list = [str(date_tuple[i]) for i in range(0,3)]
                            F_dict[platform_name]["established_date"] = "-".join(date_list) 
                    advanced_repayment = sheet.cell_value(j, advanced_repayment_position)
                    if key == "advanced_repayment":
                        compensation = advanced_repayment.strip()
                        if compensation not in compensation_list:
                            F_dict[platform_name]["compensation"] = 0
                        else:
                            F_dict[platform_name]["compensation"] = compensation_dict[str(compensation)]
        # 写入F表，已有的更新，未有的插入
        for platform_name in F_dict:
            platform_id = F_dict[platform_name]["platform_id"]
            stringSQL = "SELECT count(*) FROM " + SRCDB + " WHERE `platform_id` = '" + platform_id + "' OR `platform_name` = '" + platform_name + "'"               
            cur.execute(stringSQL)
            row = cur.fetchone()[0]
            key_str = []
            value_str = []
            # 插入
            if None == row or 0 == row:
                for key in F_dict[platform_name]:
                    key_str.append(str(key))
                    value_str.append(str(F_dict[platform_name][key]))
                stringSQL = "INSERT INTO " + SRCDB + "(`" + "`,`".join(key_str) + "`) VALUES('" + "','".join(value_str) + "')"
                print stringSQL
                cur.execute(stringSQL)
                conn.commit() 
            # 更新
            else:
                key_value_str = []
                for key in F_dict[platform_name]:
                    key_value_str.append("`" + str(key) + "` = '" + str(F_dict[platform_name][key]) + "'")
                stringSQL = "UPDATE " + SRCDB + " SET " + ",".join(key_value_str) + " WHERE `platform_id` = '" + platform_id + "' OR `platform_name` = '" + platform_name + "'"   
                print stringSQL
                cur.execute(stringSQL)
                conn.commit() 
