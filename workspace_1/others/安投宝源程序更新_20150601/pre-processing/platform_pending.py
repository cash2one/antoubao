#/usr/bin/python
#coding=utf-8

import sys
import time
import MySQLdb
from header import *

if __name__ == '__main__':
    conn=MySQLdb.connect(host=HOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    cur=conn.cursor()
    aCur=conn.cursor()

    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    timestamp = int(time.time())
    start_date=timestamp-(timestamp-1357488000)%(86400*7)
    end_date=timestamp-(timestamp-1357401600)%(86400*7)
    if (len(sys.argv) == 2):
        if (sys.argv[1] == "reset"):
            start_date = 0

    SRCDB="project_info"
    DSTDB="Table_05_pending_bill"

    amount_dict = {}
    borrower_dict = {}
    investor_dict = {}
    isnew_list = []
    stringSQL = "SELECT site_id, borrower, investor, borrowing_amount, release_time, payment_method, loan_period  FROM "+SRCDB+" WHERE `borrowing_amount` = `invested_amount` AND `release_time` > '"+str(start_date)+"' AND `release_time` < '"+str(end_date)+"'"
    cur.execute(stringSQL)
    for site_id, borrower, investor, borrowing_amount, release_time, payment_method, loan_period in cur.fetchall():
        release_time = int(release_time)
        date = (release_time%86400 > 57600) and release_time-(release_time%86400-57600) or release_time-(release_time%86400+28800)
        return_time = int(loan_period*3600*24+date)
        if site_id not in amount_dict.keys():
            amount_dict[site_id] = {}
            borrower_dict[site_id] = {}
            investor_dict[site_id] = {}
        
        if return_time not in amount_dict[site_id].keys():    
            stringSQL = "SELECT amount, borrower, investor FROM "+DSTDB+" WHERE `date` = '"+str(return_time)+"' AND `platform_id` = '"+site_id+"'"
            ret = aCur.execute(stringSQL)
            if ret == 0:
                amount_dict[site_id][return_time] = 0
                borrower_dict[site_id][return_time] = ""
                investor_dict[site_id][return_time] = ""
                isnew_list.append(site_id)
            else:
                amount_dict[site_id][return_time], borrower_dict[site_id][return_time], investor_dict[site_id][return_time] = aCur.fetchone()

        amount_dict[site_id][return_time] += borrowing_amount
        borrower_dict[site_id][return_time] += borrower+"|"+str(borrowing_amount)+","
        investorArr = investor.split("|")
        investorStr = ""
        for i in range(0, len(investorArr)):
            if i%3 == 0:
                continue
            elif i%3 == 1:
                investorStr += investorArr[i]+"|"
            else:
                investorStr += investorArr[i]+","
        investor_dict[site_id][return_time] += investorStr
    print amount_dict
    print borrower_dict
    print investor_dict
