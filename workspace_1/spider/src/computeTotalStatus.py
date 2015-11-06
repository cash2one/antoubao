#!/use/bin/python
#coding=utf-8

import time
from atbtools.header import *
from atbtools.computeTools import *
from math import ceil
if __name__ == "__main__":
    
    startTime = time.time()
    
    #获得连接
    conn_db = getConn(DBHOST_OUT, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
            
    conn = getConn("127.0.0.1", "xiebo", "123456", "antoubao", 3306)
    cur = getCursors(conn)
    initializeCursors(cur)
    
    Y = "total_status"
    Y_new = "wd_date_platform_bad_info"

    stringSQL = "TRUNCATE " + Y_new
    cur.execute(stringSQL)
    conn.commit()
    
    status_dict = {}
    status_dict["平台涉案"] = ["法人被捕", "立案侦查", "非法集资", "平台诈骗", "法人失联", "平台涉案"]
    status_dict["平台倒闭"] = ["平台跑路", "平台失联", "停止运营", "网站关闭", "宣布破产", "平台清盘", "平台倒闭"]
    status_dict["提现困难"] = ["停止提现", "限额提现", "限制提现", "提现困难"]
    status_dict["运营不善"] = ["强迫续投", "强制收费", "疑似跑路", "疑似限提", "逾期提现", "经营不善", "拖欠工资", "平台重启", "暂停营运", "曾限提现", "个别逾期", "运营不善"]
    status_list = status_dict.keys()
    
    total_number = 40
    field_list = getAllColumnsFromTable(cur, Y_new, del_list = ["Id"])
    description_index = field_list.index("description")
    field_number = len(field_list)
    stringSQL = "SELECT `"+"`, `".join(field_list)+"` FROM " +  Y + " ORDER BY `date` DESC"
    cur_db.execute(stringSQL)
    rows = cur_db.fetchall()
    count = 0
    for row in rows:
        value_list = getString(row)
        description = value_list[description_index]
        for status in status_list:
            if description in status_dict[status]:
                count += 1
                value_list[description_index] = status
                stringSQL = "INSERT INTO " + Y_new + " (`" + "`, `".join(field_list) + "`) VALUES('" + "', '".join(value_list) + "')"
                cur.execute(stringSQL)
                conn.commit()
                break
        if count == total_number:
            break
                
    closeCursors(cur)
    closeConns(conn)        
    print ""
    print "finished"
    endTime = time.time()
    print "The whole program costs " + str(endTime - startTime) + " seconds."        