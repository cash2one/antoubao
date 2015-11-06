# /usr/bin/python
# encoding=utf8
# 从project_info中读取数据来更新E1，注意是新站的全量

import sys
from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from atbtools.paymentTools import *
from math import floor
import time
import hashlib
# from meliae import scanner,loader

if __name__ == '__main__':
    if (len(sys.argv) == 1):
        print "'computeMarketShareGrowth'程序必须指定对应的表格名称."
        exit(1)
    else:
        _table = str(sys.argv[1])
            
    # 获取连接    
    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    
    platform_id_list = getDifferentFieldlist(_table, cur_db, "platform_id")
    date_list = getDifferentFieldlist(_table, cur_db, "date")
    dates_number = len(date_list)
    total_market = [0] * dates_number
    for i in range(dates_number):
        _date = date_list[i]
        stringSQL = "SELECT SUM(weekly_lending) FROM " + _table + " WHERE `date` = '" + str(_date) + "'"
        cur_db.execute(stringSQL)
        total_market[i] = cur_db.fetchone()[0]
    for platform_id in platform_id_list:
        market_share = [0] * dates_number 
        for i in range(dates_number):
            if total_market[i] == 0:
                continue
            else:
                _date = date_list[i]
                stringSQL = "SELECT weekly_lending FROM " + _table + " WHERE `date` = '" + str(_date) + "' AND `platform_id` = '" + platform_id + "'"
                ret = cur_db.execute(stringSQL)
                if ret == 0:
                    continue
                else:
                    market_share[i] = cur_db.fetchone()[0] / total_market[i]
                if i >= LASTLENDINGWEEKS:
                    _this_week = market_share[i - LASTLENDINGWEEKS + 1:i + 1][::-1]
                    _last_week = market_share[i - LASTLENDINGWEEKS:i][::-1]
                    temp = getWeightedMean(delZeroValue(_last_week))
                    market_share_growth = 0 if temp == 0 else getWeightedMean(delZeroValue(_this_week)) / temp
                    if market_share_growth != 0:
                        stringSQL = "UPDATE " + _table + " SET `market_share_growth` = '" + str(market_share_growth) + "' WHERE `platform_id` = '" + platform_id + "' AND `date` = '" + str(_date) + "'"   
                        cur_db.execute(stringSQL)
                        conn_db.commit() 
    
    closeCursors(cur_db)
    closeConns(conn_db)  