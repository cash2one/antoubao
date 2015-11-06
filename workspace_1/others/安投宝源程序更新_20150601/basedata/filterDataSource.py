#!/use/bin/python
#coding=utf-8

import sys
import string
import MySQLdb
from header import *

if __name__ == "__main__":
    conn=MySQLdb.connect(host=HOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    cur=conn.cursor()
    aCur=conn.cursor()
    bCur=conn.cursor()
    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    SRCDB = "platform_quantitative_data_E1"
    DSTDB = "platform_quantitative_data_E1"
    PRODB = "platform_problem_record_Y"
    FDB = "platform_qualitative_F"

    stringSQL = "SELECT DISTINCT date FROM "+SRCDB+" ORDER BY date ASC"
    cur.execute(stringSQL)
    dates = cur.fetchall()

    start = len(dates)-1
    if (len(sys.argv) == 2):
        if (sys.argv[1] == "reset"):
            start = 0

    for date_index in range(start, len(dates)):
        date = str(dates[date_index][0])
       
        #获取当前时间前所有坏站的status状态
        pro = {}
        stringSQL = "SELECT platform_id, status FROM "+PRODB+" WHERE `date` <= '"+str(date)+"' ORDER BY `date` DESC"
        cur.execute(stringSQL)
        for platId, status in cur.fetchall():
            if platId not in pro:
                pro[platId] = status
        '''
        #获取本周坏站的status
        stringSQL = "SELECT DISTINCT platform_id, date, status FROM "+PRODB
        cur.execute(stringSQL)
        pro = []
        for proId, proDate, status in cur.fetchall():
            if int(proDate) <= int(date) and int(proDate) >= int(date)-(7*24*3600) and status < 0.89:
                pro.append(proId)
        '''
        weekly_lending_arr = []
        weekly_new_investor_arr = []
        weekly_total_investor_arr = []
        weekly_total_borrower_arr = []
        stringSQL = "SELECT platform_id, weekly_lending, weekly_new_investor, weekly_total_investor, weekly_total_borrower FROM "+SRCDB+" WHERE `date` = '"+date+"'"
        aCur.execute(stringSQL)
        for platId, weekly_lending, weekly_new_investor, weekly_total_investor, weekly_total_borrower in aCur.fetchall():
            stringSQL = "SELECT weekly_lending, weekly_new_investor, weekly_total_investor, weekly_total_borrower FROM "+SRCDB+" WHERE `platform_id` = '"+platId+"' AND `date` < '"+date+"' ORDER BY `date` DESC LIMIT 1"
            ret = bCur.execute(stringSQL)
            if ret == 0:
                continue
            prev_weekly_lending, prev_weekly_new_investor, prev_weekly_total_investor, prev_weekly_total_borrower = bCur.fetchone()
            if prev_weekly_lending != 0:
                weekly_lending_arr.append((weekly_lending-prev_weekly_lending)/prev_weekly_lending)
            if prev_weekly_new_investor != 0:
                weekly_new_investor_arr.append((weekly_new_investor-prev_weekly_new_investor)/prev_weekly_new_investor)
            if prev_weekly_total_investor != 0:
                weekly_total_investor_arr.append((weekly_total_investor-prev_weekly_total_investor)/prev_weekly_total_investor)
            if prev_weekly_total_borrower != 0:
                weekly_total_borrower_arr.append((weekly_total_borrower-prev_weekly_total_borrower)/prev_weekly_total_borrower)
        #第一周数据不参与
        if len(weekly_lending_arr) == 0 or len(weekly_new_investor_arr) == 0 or len(weekly_total_investor_arr) == 0 or len(weekly_total_borrower_arr) == 0:
            continue
        weekly_lending_ave = sum(weekly_lending_arr)/len(weekly_lending_arr)
        weekly_new_investor_ave = sum(weekly_new_investor_arr)/len(weekly_new_investor_arr)
        weekly_total_investor_ave = sum(weekly_total_investor_arr)/len(weekly_total_investor_arr)
        weekly_total_borrower_ave = sum(weekly_total_borrower_arr)/len(weekly_total_borrower_arr)

        stringSQL = "SELECT platform_id, platform_name, latest4week_lending, weekly_lending, weekly_new_investor, weekly_total_investor, weekly_total_borrower FROM "+SRCDB+" WHERE `date` = '"+date+"'"
        cur.execute(stringSQL)
        for platId, platName, latest4week_lending, weekly_lending, weekly_new_investor, weekly_total_investor, weekly_total_borrower in cur.fetchall():
            in_and_out = 0

            stringSQL = "SELECT registered_cap FROM "+FDB+" WHERE `platform_name` = '"+platName+"'"
            ret = aCur.execute(stringSQL)
            if ret == 0 :
                registered_cap = 0
            else: 
                registered_cap = aCur.fetchone()[0]
            black = ""
            if weekly_lending == 0:
                black += "#B1#"
            if weekly_total_borrower == 0:
                black += "#B2#"
            if weekly_total_investor == 0:
                black += "#B3#"
            if registered_cap == 0:
                black += "#B4#"
            if platId in pro and pro[platId] < 0.89:
                black += "#P#"
            if black == "" and latest4week_lending < 770:
                #if platId in pro:
                #    black += "#P#"
                #else:
                stringSQL = "SELECT in_and_out FROM "+DSTDB+" WHERE `date` < '"+date+"' AND `black` NOT LIKE '%#B%' AND `platform_id` = '"+platId+"' ORDER BY `date` DESC LIMIT 1"
                ret = aCur.execute(stringSQL)
                if ret == 0:
                    black += "#B5#"
                else:
                    in_and_out = aCur.fetchone()[0]
                    in_and_out += 1            

            stringSQL = "UPDATE "+SRCDB+" SET `in_and_out` = '"+str(in_and_out)+"', `black` = '"+black+"' WHERE `platform_id` = '"+platId+"' AND `date` = '"+date+"'"
            aCur.execute(stringSQL)
            conn.commit()
