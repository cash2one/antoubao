# /usr/bin/python
# encoding=utf8
# 将project_info中的脏数据去掉，方便后续处理

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.paymentTools import *
from atbtools.computeTools import * 
from math import floor
import time
import hashlib

if __name__ == '__main__':
    # 获取连接    
    srcdb_info_F = "platform_qualitative_F"
    dstdb_info = "project_info_clean_temp"
    conn_db = getConn(DBHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    
    #设定各个字段的默认值
    field_default_dict = {}
    stringSQL = "select column_name,data_type from information_schema.columns where `table_schema` = 'antoubao' and `table_name` = 'project_info_clean_whole' order by table_name,ordinal_position"
    cur_db.execute(stringSQL)
    for field, data_type in cur_db.fetchall():
        if field == "id":
            continue
        if data_type == "varchar":
            field_default_dict[field] = ""
        else:
            field_default_dict[field] = -1
    this_date = time.strftime("%Y%m%d")
    
    #获得所有字段
    fields_list = ["id", "project_id", "project_name", "site_id", "borrower", "investor", "payment_method", "loan_period", "annulized_rating", "borrowing_amount", "release_time", "end_time", "state"]
    fields_number = len(fields_list)
    
    #从文件中获得坏站platform_id
    platform_id_list = getListByTxt("badplatform_id.txt")
    for site_id in platform_id_list:
        print site_id
        #初始值设置
        stringSQL = "SELECT platform_name FROM " + srcdb_info_F + " WHERE `platform_id` ='" + site_id + "' LIMIT 1"
        ret = cur_db.execute(stringSQL)
        if ret == 0:
            platform_name = site_id
        else:
            platform_name = cur_db.fetchone()[0]
        platform_id = hashlib.md5(platform_name).hexdigest()[0:10]
        
        srcdb_info = getProjectInfo("project_info", site_id)
        stringSQL = "SELECT `" +"`,`".join(fields_list) + "` FROM "+ srcdb_info + " WHERE `site_id` = '" + site_id + "'"
#         print "正在从数据库传输数据回本地..."
        bids_number = cur_db.execute(stringSQL)
        bidsPercentList = [floor(float(x) * bids_number / BUFFERNUMBER) for x in range(1, BUFFERNUMBER + 1)] 
        bad_bids_number = 0
        rows = cur_db.fetchall()
        counter = 0
        print "cleaning: 0%"
        for row in rows:
            counter += 1
            if counter in bidsPercentList:
                print "cleaning: " + str((1 + bidsPercentList.index(counter)) * 100 / BUFFERNUMBER) + "%"
            v={}
            for field in field_default_dict:
                v[field] = field_default_dict[field]
            for i in range(fields_number):
                v[fields_list[i]] = row[i]
            v["pid"] = v["id"]
            del v["id"]
            v["platform_name"] = platform_name
            v["platform_id"] = platform_id
            
            v = cleanProjectInfoPerBid(v)
            
            if v["error"] != "":
                bad_bids_number += 1
#                 continue
#             else:
#                 v["release_time"] = v["first_time"]
#                 v["end_time"] = v["last_time"]
            field_list_temp = field_default_dict.keys()
            value_list_temp = []
            for field in field_list_temp:
                value_list_temp.append(str(v[field]))
            stringSQL = "INSERT INTO " + dstdb_info + "(`" + "`,`".join(field_list_temp) + "`) VALUES('" + "','".join(value_list_temp) + "')"
#                 print stringSQL
            cur_db.execute(stringSQL)
            conn_db.commit()
                
        print "共有" + str(bids_number) + "个标."
        print "在满额限制为"+ str(FULLBIDPERCENT) + "的情况下, 只有" + "%.2f" % (100 * (1-float(bad_bids_number)/bids_number)) + "%的数据是可用的."
    closeCursors(cur_db)
    closeConns(conn_db)  
