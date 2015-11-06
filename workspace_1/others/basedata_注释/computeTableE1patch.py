#!/use/bin/python
#coding=utf-8

import sys
import string
import MySQLdb
import random
from math import log
import numpy as np
from header import *

def r3():
    return random.uniform(-0.02, 0.02)+1

if __name__ == "__main__":
    conn=MySQLdb.connect(host=HOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    cur=conn.cursor()
    inlineCur=conn.cursor()

    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    TableE1 = "data_E1"
    #取出时间列表
    stringSQL = "SELECT DISTINCT date FROM platform_quantitative_"+TableE1+" ORDER BY date ASC"
    cur.execute(stringSQL)
    dates = cur.fetchall()

    start = len(dates)-1
    if (len(sys.argv) == 2):
        if (sys.argv[1] == "reset"):
            start = 0

    for date_index in range(start, len(dates)):
        date = str(dates[date_index][0])

        #翼龙贷数据补全
        platId = "4de3888a61"
        top40 = {}
        v = {}
        stringSQL = "SELECT weekly_lending, weekly_total_investor, weekly_total_borrower, weekly_ave_investment, weekly_loan_period FROM platform_quantitative_"+TableE1+" WHERE `date` = '"+date+"' AND `platform_id` = '"+platId+"'"
        ret = cur.execute(stringSQL)
        if ret != 0:
            weekly_lending, weekly_total_investor, weekly_total_borrower, weekly_ave_investment, weekly_loan_period = cur.fetchone()

            for key in ["weekly_ratio_new_old", "weekly_ave_investment_old", "weekly_ave_investment", "weekly_ave_investment_per_bid", "weekly_ave_bid_close_time", "weekly_ave_lending_per_bid", "money_growth"]:
                top40[key] = []
                stringSQL = "SELECT "+key+" FROM platform_quantitative_"+TableE1+" WHERE `date` = '"+date+"' AND `platform_id` != 'da3911f3cd' AND `"+key+"` != '0' ORDER BY `weekly_lending` DESC LIMIT 39"
                cur.execute(stringSQL)
                for val in cur.fetchall():
                    if val[0] is None:
                        top40[key].append(0)
                    else:
                        top40[key].append(val[0])

            weekly_old_investor = weekly_total_investor/(1+np.mean(top40['weekly_ratio_new_old']))
            v['weekly_new_investor'] = weekly_total_investor - weekly_old_investor
            v['weekly_ratio_new_old'] = v['weekly_new_investor']/weekly_old_investor
            beta = np.mean(np.array(top40['weekly_ave_investment_old'])/np.array(top40['weekly_ave_investment']))
            v['weekly_ave_investment_old'] = beta*weekly_ave_investment
            v['weekly_ave_investment_per_bid'] = np.mean(top40['weekly_ave_investment_per_bid'])*r3()
            v['weekly_ave_bid_close_time'] = np.mean(top40['weekly_ave_bid_close_time'])*r3()
            v['weekly_ave_lending_per_bid'] = np.mean(top40['weekly_ave_lending_per_bid'])*r3()
            if date_index >= 3:
                stringSQL = "select sum(weekly_lending) from platform_quantitative_"+TableE1+" where `platform_id` = '"+platId+"' and (`date` = '"+str(dates[date_index][0])+"' or `date` = '"+str(dates[date_index-1][0])+"' or `date` = '"+str(dates[date_index-2][0])+"' or `date` = '"+str(dates[date_index-3][0])+"')"
                cur.execute(stringSQL)
                v['latest4week_lending'] = cur.fetchone()[0]
                tmp = (np.mean(top40['money_growth']))**weekly_loan_period
                if tmp != 0:
                    future4week_maturity = v['latest4week_lending']/tmp
                    if future4week_maturity != 0:
                        v['not_returned_yet'] = v['latest4week_lending']/future4week_maturity
                        if weekly_loan_period != 0:
                            v['money_growth'] = (v['latest4week_lending']/future4week_maturity)**(1/weekly_loan_period)

                if date_index >= 4:
                    stringSQL="SELECT weekly_total_borrower, weekly_total_investor FROM platform_quantitative_"+TableE1+" WHERE `platform_id` = '"+platId+"' AND `date` = '"+str(dates[date_index-4][0])+"'"
                    ret = cur.execute(stringSQL)
                    if ret != 0:
                        pro_weekly_total_borrower, pro_weekly_total_investor = cur.fetchone()
                        if pro_weekly_total_borrower != 0:
                            v['borrower_growth'] = weekly_total_borrower/pro_weekly_total_borrower
                        if pro_weekly_total_investor != 0:
                            v['investor_growth'] = weekly_total_investor/pro_weekly_total_investor
                
                    stringSQL = "SELECT sum(weekly_lending) FROM platform_quantitative_"+TableE1+" WHERE `weekly_lending` > 200 AND `date` = '"+str(dates[date_index-4][0])+"'"
                    ret = cur.execute(stringSQL)
                    if ret != 0:
                        pro_weekly_total_lending = cur.fetchone()[0]
                        if pro_weekly_total_lending != 0:
                            stringSQL = "SELECT weekly_lending FROM platform_quantitative_"+TableE1+" WHERE `platform_id` = '"+platId+"' AND `date` = '"+str(dates[date_index-4][0])+"'"
                            ret = cur.execute(stringSQL)
                            if ret != 0:
                                pro_weekly_lending = cur.fetchone()[0]
                                pro_market_share = pro_weekly_lending/pro_weekly_total_lending
                            else:
                                pro_market_share = 0

                    stringSQL = "SELECT sum(weekly_lending) FROM platform_quantitative_"+TableE1+" WHERE `weekly_lending` > 200 AND `date` = '"+str(dates[date_index][0])+"'"
                    ret = cur.execute(stringSQL)
                    if ret != 0:
                        weekly_total_lending = cur.fetchone()[0]
                        if weekly_total_lending != 0:
                            market_share = weekly_lending/weekly_total_lending

                    if (pro_market_share != 0):
                        v['market_share_growth'] = market_share/pro_market_share

            key = ""
            for _k,_v in v.items():
                key = key + "`"+_k+"` = '"+str(_v)+"',"
            stringSQL = "UPDATE platform_quantitative_"+TableE1+" SET "+key[:-1]+" WHERE `date` = '"+date+"' AND `platform_id` = '"+platId+"'"
            cur.execute(stringSQL)
            conn.commit()

	    #点融网数据补全
        platId = "411326053e"
        top40 = {}
        v = {}
        stringSQL = "SELECT weekly_lending, weekly_total_investor, weekly_total_borrower, weekly_ave_investment, weekly_loan_period FROM platform_quantitative_"+TableE1+" WHERE `date` = '"+date+"' AND `platform_id` = '"+platId+"'"
        ret = cur.execute(stringSQL)
        if ret != 0:
            weekly_lending, weekly_total_investor, weekly_total_borrower, weekly_ave_investment, weekly_loan_period = cur.fetchone()

            for key in ["weekly_ratio_new_old", "weekly_ave_investment_old", "weekly_ave_investment", "weekly_ave_investment_per_bid", "weekly_ave_bid_close_time", "weekly_ave_lending_per_bid", "money_growth"]:
                top40[key] = []
                stringSQL = "SELECT "+key+" FROM platform_quantitative_"+TableE1+" WHERE `date` = '"+date+"' AND `platform_id` != 'da3911f3cd' ORDER BY `weekly_lending` DESC LIMIT 39"
                cur.execute(stringSQL)
                for val in cur.fetchall():
                    if val[0] is None:
                        top40[key].append(0)
                    else:
                        top40[key].append(val[0])

            weekly_old_investor = weekly_total_investor/(1+np.mean(top40['weekly_ratio_new_old']))
            v['weekly_new_investor'] = weekly_total_investor - weekly_old_investor
            v['weekly_ratio_new_old'] = v['weekly_new_investor']/weekly_old_investor
            beta = np.mean(np.array(top40['weekly_ave_investment_old'])/np.array(top40['weekly_ave_investment']))
            v['weekly_ave_investment_old'] = beta*weekly_ave_investment
            v['weekly_ave_investment_per_bid'] = np.mean(top40['weekly_ave_investment_per_bid'])*r3()
            v['weekly_ave_bid_close_time'] = np.mean(top40['weekly_ave_bid_close_time'])*r3()
            v['weekly_ave_lending_per_bid'] = np.mean(top40['weekly_ave_lending_per_bid'])*r3()
            if date_index >= 3:
                stringSQL = "select sum(weekly_lending) from platform_quantitative_"+TableE1+" where `platform_id` = '"+platId+"' and (`date` = '"+str(dates[date_index][0])+"' or `date` = '"+str(dates[date_index-1][0])+"' or `date` = '"+str(dates[date_index-2][0])+"' or `date` = '"+str(dates[date_index-3][0])+"')"
                cur.execute(stringSQL)
                v['latest4week_lending'] = cur.fetchone()[0]
                tmp = (np.mean(top40['money_growth']))**weekly_loan_period
                if tmp != 0:
                    future4week_maturity = v['latest4week_lending']/tmp
                    if future4week_maturity != 0:
                        v['not_returned_yet'] = v['latest4week_lending']/future4week_maturity
                        if weekly_loan_period != 0:
                            v['money_growth'] = (v['latest4week_lending']/future4week_maturity)**(1/weekly_loan_period)

                if date_index >= 4:
                    stringSQL="SELECT weekly_total_borrower, weekly_total_investor FROM platform_quantitative_"+TableE1+" WHERE `platform_id` = '"+platId+"' AND `date` = '"+str(dates[date_index-4][0])+"'"
                    ret = cur.execute(stringSQL)
                    if ret != 0:
                        pro_weekly_total_borrower, pro_weekly_total_investor = cur.fetchone()
                        if pro_weekly_total_borrower != 0:
                            v['borrower_growth'] = weekly_total_borrower/pro_weekly_total_borrower
                        if pro_weekly_total_investor != 0:
                            v['investor_growth'] = weekly_total_investor/pro_weekly_total_investor
                
                    stringSQL = "SELECT sum(weekly_lending) FROM platform_quantitative_"+TableE1+" WHERE `weekly_lending` > 200 AND `date` = '"+str(dates[date_index-4][0])+"'"
                    ret = cur.execute(stringSQL)
                    if ret != 0:
                        pro_weekly_total_lending = cur.fetchone()[0]
                        if pro_weekly_total_lending != 0:
                            stringSQL = "SELECT weekly_lending FROM platform_quantitative_"+TableE1+" WHERE `platform_id` = '"+platId+"' AND `date` = '"+str(dates[date_index-4][0])+"'"
                            ret = cur.execute(stringSQL)
                            if ret != 0:
                                pro_weekly_lending = cur.fetchone()[0]
                                pro_market_share = pro_weekly_lending/pro_weekly_total_lending
                            else:
                                pro_market_share = 0

                    stringSQL = "SELECT sum(weekly_lending) FROM platform_quantitative_"+TableE1+" WHERE `weekly_lending` > 200 AND `date` = '"+str(dates[date_index][0])+"'"
                    ret = cur.execute(stringSQL)
                    if ret != 0:
                        weekly_total_lending = cur.fetchone()[0]
                        if weekly_total_lending != 0:
                            market_share = weekly_lending/weekly_total_lending

                    if (pro_market_share != 0):
                        v['market_share_growth'] = market_share/pro_market_share

            key = ""
            for _k,_v in v.items():
                key = key + "`"+_k+"` = '"+str(_v)+"',"
            stringSQL = "UPDATE platform_quantitative_"+TableE1+" SET "+key[:-1]+" WHERE `date` = '"+date+"' AND `platform_id` = '"+platId+"'"
            cur.execute(stringSQL)
            conn.commit()


        #陆金所数据补全
#        platId = "6372008a69"
#        top20 = {}
#        v = {}
#        stringSQL = "SELECT weekly_total_investor, weekly_total_borrower, weekly_ave_investment, weekly_loan_period, weekly_lending FROM platform_quantitative_"+TableE1+" WHERE `date` = '"+date+"' AND `platform_id` = '"+platId+"'"
#        ret = cur.execute(stringSQL)
#        if ret != 0:
#            weekly_total_investor, weekly_total_borrower, weekly_ave_investment, weekly_loan_period, weekly_lending = cur.fetchone()
#
#            v['weekly_total_investor'] = weekly_total_investor*20
#            v['weekly_ave_investment'] = weekly_ave_investment/20
#            weekly_old_investor = v['weekly_total_investor']/(1+1)
#            v['weekly_new_investor'] = v['weekly_total_investor'] - weekly_old_investor
#            v['weekly_ratio_new_old'] = v['weekly_new_investor']/weekly_old_investor
#            for key in ["weekly_ave_investment_old", "weekly_ave_investment", "weekly_ave_investment_per_bid", "weekly_ave_bid_close_time", "weekly_ave_lending_per_bid", "money_growth"]:
#                top20[key] = []
#                stringSQL = "SELECT "+key+" FROM platform_quantitative_"+TableE1+" WHERE `date` = '"+date+"' AND `platform_id` != 'da3911f3cd' ORDER BY `weekly_lending` DESC LIMIT 19"
#                cur.execute(stringSQL)
#                for val in cur.fetchall():
#                    top20[key].append(val[0])
#            beta = np.mean(np.array(top20['weekly_ave_investment_old'])/np.array(top20['weekly_ave_investment']))
#            v['weekly_ave_investment_old'] = beta*v['weekly_ave_investment']
#            v['weekly_ave_investment_per_bid'] = np.mean(top20['weekly_ave_investment_per_bid'])
#            v['weekly_ave_bid_close_time'] = np.mean(top20['weekly_ave_bid_close_time'])
#            v['weekly_ave_lending_per_bid'] = np.mean(top20['weekly_ave_lending_per_bid'])
#            g = np.mean(top20['money_growth'])
#            if g == 1 or g <= 0.2:
#                v['weekly_outstanding_loan'] = 0
#            else:
#                v['weekly_outstanding_loan'] = weekly_lending*(1-g**(-weekly_loan_period))/(log(g))
#
#            if date_index >= 3:
#                stringSQL = "select sum(weekly_lending) from platform_quantitative_"+TableE1+" where `platform_id` = '"+platId+"' and (`date` = '"+str(dates[date_index][0])+"' or `date` = '"+str(dates[date_index-1][0])+"' or `date` = '"+str(dates[date_index-2][0])+"' or `date` = '"+str(dates[date_index-3][0])+"')"
#                cur.execute(stringSQL)
#                v['latest4week_lending'] = cur.fetchone()[0]
#                future4week_maturity = v['latest4week_lending']*(np.mean(top20['money_growth']))**weekly_loan_period
#                if future4week_maturity != 0:
#                    v['not_returned_yet'] = v['latest4week_lending']/future4week_maturity
#                    if weekly_loan_period != 0:
#                        v['money_growth'] = (v['latest4week_lending']/future4week_maturity)**(1/weekly_loan_period)
#
#                if date_index >= 4:
#                    stringSQL="SELECT weekly_total_borrower, weekly_total_investor FROM platform_quantitative_"+TableE1+" WHERE `platform_id` = '"+platId+"' AND `date` = '"+str(dates[date_index-4][0])+"'"
#                    ret = cur.execute(stringSQL)
#                    if ret != 0:
#                        pro_weekly_total_borrower, pro_weekly_total_investor = cur.fetchone()
#                        if pro_weekly_total_borrower != 0:
#                            v['borrower_growth'] = weekly_total_borrower/pro_weekly_total_borrower
#                        if pro_weekly_total_investor != 0:
#                            v['investor_growth'] = weekly_total_investor/pro_weekly_total_investor
#                
#                    stringSQL = "SELECT sum(weekly_lending) FROM platform_quantitative_"+TableE1+" WHERE `weekly_lending` > 200 AND `date` = '"+str(dates[date_index-4][0])+"'"
#                    ret = cur.execute(stringSQL)
#                    if ret != 0:
#                        pro_weekly_total_lending = cur.fetchone()[0]
#                        if pro_weekly_total_lending != 0:
#                            stringSQL = "SELECT weekly_lending FROM platform_quantitative_"+TableE1+" WHERE `platform_id` = '"+platId+"' AND `date` = '"+str(dates[date_index-4][0])+"'"
#                            cur.execute(stringSQL)
#                            pro_weekly_lending = cur.fetchone()[0]
#                            pro_market_share = pro_weekly_lending/pro_weekly_total_lending
#
#                    stringSQL = "SELECT sum(weekly_lending) FROM platform_quantitative_"+TableE1+" WHERE `weekly_lending` > 200 AND `date` = '"+str(dates[date_index][0])+"'"
#                    ret = cur.execute(stringSQL)
#                    if ret != 0:
#                        weekly_total_lending = cur.fetchone()[0]
#                        if weekly_total_lending != 0:
#                            market_share = weekly_lending/weekly_total_lending
#
#                    if (pro_market_share != 0):
#                        v['market_share_growth'] = market_share/pro_market_share
#
#            key = ""
#            for _k,_v in v.items():
#                key = key + "`"+_k+"` = '"+str(_v)+"',"
#            stringSQL = "UPDATE platform_quantitative_"+TableE1+" SET "+key[:-1]+" WHERE `date` = '"+date+"' AND `platform_id` = '"+platId+"'"
#            print stringSQL
#            cur.execute(stringSQL)
#            conn.commit()
