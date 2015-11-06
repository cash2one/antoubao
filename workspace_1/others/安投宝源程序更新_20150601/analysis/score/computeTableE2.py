#!/use/bin/python
#coding=utf-8

import sys
import string
import MySQLdb
import numpy as np
from header import *

if __name__ == "__main__":
    sconn=MySQLdb.connect(host="db-x1.antoubao.cn", user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    scur=sconn.cursor()
    conn=MySQLdb.connect(host=HOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    cur=conn.cursor()
    aCur=conn.cursor()
    bCur=conn.cursor()

    scur.execute("SET NAMES 'UTF8'")
    scur.execute("SET CHARACTER SET UTF8")
    scur.execute("SET CHARACTER_SET_RESULTS=UTF8")
    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    SRCDB = "platform_quantitative_data_E1"
    DSTDB = "platform_quantitative_data_E2"
    PRODB = "platform_problem_record_Y"

    stringSQL = "SELECT DISTINCT date FROM "+SRCDB+" ORDER BY date ASC"
    scur.execute(stringSQL)
    dates = scur.fetchall()

    start = len(dates)-1
    if (len(sys.argv) == 2):
        if (sys.argv[1] == "reset"):
            start = 0
            cur.execute("TRUNCATE "+DSTDB)
            conn.commit()
            cur.execute("DELETE FROM platform_level_Z WHERE `date` != '"+LINEDATE+"'")
            conn.commit()
            cur.execute("DELETE FROM view_score_condition WHERE `date` != '"+LINEDATE+"'")
            conn.commit()
    else:
        cur.execute("DELETE FROM "+DSTDB+" WHERE `date` = '"+str(dates[start][0])+"'")
        conn.commit()
        cur.execute("DELETE FROM platform_level_Z WHERE `date` = '"+str(dates[start][0])+"'")
        conn.commit()
        cur.execute("DELETE FROM view_score_condition WHERE `date` = '"+str(dates[start][0])+"'")
        conn.commit()

    arrKeys = []
    ratios = {}
    stringSQL = "SHOW FULL COLUMNS FROM "+SRCDB
    scur.execute(stringSQL)
    for col in scur.fetchall():
        if (col[0] == "id") or (col[0] == "date") or (col[0] == "weekly_outstanding_loan") or (col[0] == "in_and_out") or (col[0] == "future4week_maturity"):
            continue
        arrKeys.append(col[0])
    for key in arrKeys:
        ratios[key] = 1

    levelKeys = []
    stringSQL = "SHOW FULL COLUMNS FROM platform_level_Z"
    cur.execute(stringSQL)
    for col in cur.fetchall():
        if col[0] == "id" or col[0] == "date":
            continue
        levelKeys.append(col[0])

    condKeys = []
    stringSQL = "SELECT prop FROM view_score_condition"
    cur.execute(stringSQL)
    for col in cur.fetchall():
        condKeys.append(col[0])

    for date_index in range(start, len(dates)):
        date = str(dates[date_index][0])
        
        #获取所有坏站信息和本周坏站信息
        stringSQL = "SELECT DISTINCT platform_id, date, status FROM "+PRODB
        scur.execute(stringSQL)
        proAll = []
        for proId, proDate, status in scur.fetchall():
            if int(proDate) <= int(date) and int(proDate) > int(date)-(7*24*3600) and status < 0.89:
                proAll.append(proId)
        
        proArr = []
        stringSQL = "SELECT "+",".join(arrKeys)+" FROM "+SRCDB+" WHERE `date` = '"+str(date)+"'"
        scur.execute(stringSQL)
        for _list in scur.fetchall():
            i = 0
            k = ""
            v = ""
            punishment = ""
            platid = ""
            for key in arrKeys:
                if key == "platform_id":
                    platid = _list[i]
                    if platid in proAll:
                        proArr.append(platid)
                #elif key == "black" and _list[i] is not None and "#P#" in _list[i]:
                #    proArr.append(platid)
                k = k+"`"+key+"`,"
                if _list[i] is None:
                    v = v+"'0',"
                else:
                    if key == 'weekly_ave_lending_per_bid':
                        v = v+"'"+str(_list[i]/10000)+"',"
                    else:
                        v = v+"'"+str(_list[i])+"',"
                i+=1
            if v == "":
                continue
            stringSQL = "INSERT INTO "+DSTDB+"(`date`, "+k[:-1]+") VALUES('"+str(date)+"', "+v[:-1]+")"
            cur.execute(stringSQL)
            conn.commit()

        #所有参与planB类型更新的参数列表，用于计算ratios
        planBKeys = ["turnover_registered", "weekly_ave_investment", "ave_annualized_return", "weekly_ave_lending_per_borrower", "top10_ratio_loan", "not_returned_yet", "weekly_loan_period", "provision_of_risk", "market_share_growth", "weekly_lending", "weekly_total_borrower", "weekly_ave_investment_old", "weekly_ave_investment_per_bid", "weekly_ave_bid_close_time", "weekly_ratio_new_old", "weekly_ave_lending_per_bid", "top5_ratio_loan", "borrower_HHI", "outstanding_loan", "money_growth", "borrower_growth", "investor_growth"]

        #所有参与planC类型更新的参数列表，用于计算ratios
        planCKeys = ["weekly_total_investor", "turnover_period", "weekly_total_borrower", "weekly_new_investor", "weekly_lending", "weekly_total_investor", "PR_transparency1"]

        if date <= LINEDATE:
            d = LINEDATE
            ld = LINEDATE
        else:
            d = str(dates[date_index][0])
            ld = str(dates[date_index-1][0])
            ave1 = {}
            pro_ave1 = {}
            stringSQL = "SELECT "+','.join(planBKeys)+" FROM "+DSTDB+" WHERE `date` = '"+d+"' AND `platform_name` != 'strategy_report'"
            aCur.execute(stringSQL)
            for _list in aCur.fetchall():
                for i in range(0, len(_list)):
                    if planBKeys[i] not in ave1:
                        ave1[planBKeys[i]] = []
                    ave1[planBKeys[i]].append(_list[i])
            for key in ave1.keys():
                ave1[key].remove(max(ave1[key]))
                ave1[key].remove(max(ave1[key]))
                ave1[key].remove(max(ave1[key]))
            for key in ave1.keys():
                if key not in pro_ave1:
                    pro_ave1[key] = 0
                pro_ave1[key] = np.average(ave1[key], weights=ave1['weekly_lending'])

            value = ""
            ave2 = {}
            pro_ave2 = {}
            stringSQL = "SELECT "+','.join(planBKeys)+" FROM "+DSTDB+" WHERE `date` = '"+ld+"' AND `platform_name` != 'strategy_report'"
            aCur.execute(stringSQL)
            for _list in aCur.fetchall():
                for i in range(0, len(_list)):
                    if planBKeys[i] not in ave2:
                        ave2[planBKeys[i]] = []
                    ave2[planBKeys[i]].append(_list[i])
            for key in ave2.keys():
                ave2[key].remove(max(ave2[key]))
                ave2[key].remove(max(ave2[key]))
                ave2[key].remove(max(ave2[key]))
            for key in ave2.keys():
                if key not in pro_ave2:
                    pro_ave2[key] = 0
                pro_ave2[key] = np.average(ave2[key], weights=ave2['weekly_lending'])
                if pro_ave2[key] != 0:
                    ratios[key] = float(pro_ave1[key]/pro_ave2[key])
                else:
                    ratios[key] = 1
            
            ave = {}
            stringSQL = "SELECT avg("+'),avg('.join(planCKeys)+") FROM "+DSTDB+" WHERE `date` = '"+d+"' AND `platform_name` != 'strategy_report'"
            aCur.execute(stringSQL)
            _list = aCur.fetchone()
            for i in range(0, len(_list)):
                ave[planCKeys[i]] = _list[i]
            stringSQL = "SELECT avg("+'),avg('.join(planCKeys)+") FROM "+DSTDB+" WHERE `date` = '"+ld+"' AND `platform_name` != 'strategy_report'"
            aCur.execute(stringSQL)
            _list = aCur.fetchone()
            for i in range(0, len(_list)):
                if _list[i] != 0:
                    ratios[planCKeys[i]] = float(ave[planCKeys[i]]/_list[i])

        stringSQL = "SELECT "+",".join(levelKeys)+" FROM platform_level_Z WHERE `date` = '"+ld+"'"
        cur.execute(stringSQL)
        for _list in cur.fetchall():
            i = 0
            k = ""
            v = ""
            for key in levelKeys:
                k = k+"`"+key+"`,"
                if key == "platform_id" or key == "platform_name":
                    v = v+"'"+str(_list[i])+"',"
                else:
                    v = v+"'"+str(_list[i]*ratios[key])+"',"
                i += 1
            stringSQL = "INSERT INTO "+DSTDB+"(`date`,"+k[:-1]+", `black`) VALUES('"+str(date)+"', "+v[:-1]+", '')"
            aCur.execute(stringSQL)
            conn.commit()
            if date != LINEDATE:
                stringSQL = "INSERT INTO platform_level_Z"+"(`date`,"+k[:-1]+") VALUES('"+str(date)+"', "+v[:-1]+")"
                aCur.execute(stringSQL)
                conn.commit()

        if date != LINEDATE:
            for key in condKeys:
                stringSQL = "SELECT score1,score2,score3,score4,score5 FROM view_score_condition WHERE `prop` = '"+key+"' AND `date` = '"+ld+"'"
                aCur.execute(stringSQL)
                _list = aCur.fetchone()
                stringSQL = "INSERT INTO view_score_condition(`prop`, `date`, `score1`, `score2`, `score3`, `score4`, `score5`) VALUES('"+key+"', '"+str(date)+"', '"+str(_list[0]*ratios[key])+"', '"+str(_list[1]*ratios[key])+"', '"+str(_list[2]*ratios[key])+"', '"+str(_list[3]*ratios[key])+"', '"+str(_list[4]*ratios[key])+"')"
                aCur.execute(stringSQL)
                conn.commit()
        '''
        if date_index > 0:
            thisWeekPro = []
            stringSQL = "SELECT platform_id FROM "+DSTDB+" WHERE `date` = '"+str(date)+"'"
            cur.execute(stringSQL)
            for platId in cur.fetchall():
                if platId[0] in proAll:
                    thisWeekPro.append(platId[0])
            stringSQL = "SELECT "+",".join(arrKeys)+" FROM "+DSTDB+" WHERE `date` = '"+str(dates[date_index-1][0])+"'"
            cur.execute(stringSQL)
            for _list in cur.fetchall():
                if _list[arrKeys.index('platform_id')] not in proAll or _list[arrKeys.index('platform_id')] in thisWeekPro:
                    continue
                stringSQL = "INSERT INTO "+DSTDB+"(`date`, `"+"`,`".join(arrKeys)+"`) VALUES('"+str(date)+"', '"+"','".join(str(a) for a in _list)+"')"
                cur.execute(stringSQL)
                conn.commit()
        '''
        strategyB = {}
        stringSQL = "SELECT prop, prop_map, `range` FROM view_strategyB_configure"
        cur.execute(stringSQL)
        for prop, prop_map, _range in cur.fetchall():
            if prop not in strategyB:
                strategyB[prop] = {}
            strategyB[prop][prop_map] = _range
        
        date = int(date)
        for platId in proArr:
            stringSQL = "INSERT INTO "+DSTDB+"(`date`, `"+"`, `".join(arrKeys)+"`) VALUE('"+str(date-7*24*3600*2)+"', '"+platId+"B', 'strategy_report', '"+"', '".join(['0']*(len(arrKeys)-2))+"')"
            cur.execute(stringSQL)
            conn.commit()
            result = {}
            
            for prop in strategyB:
                for prop_map in strategyB[prop]:
                    stringSQL = "SELECT "+prop_map+" FROM "+DSTDB+" WHERE `date` = '"+str(date-7*24*3600*2)+"' AND `platform_id` = '"+platId+"'"
                    ret = cur.execute(stringSQL)
                    if ret == 0:
                        break
                    value = float(cur.fetchone()[0])
                    range1 = value + value * strategyB[prop][prop_map]
                    range2 = value - value * strategyB[prop][prop_map]
                    stringSQL = "SELECT platform_id FROM "+DSTDB+" WHERE `"+prop_map+"` > '"+str(range2)+"' AND `"+prop_map+"` < '"+str(range1)+"' AND `date` = '"+str(date-7*24*3600*2)+"'"
                    ret = cur.execute(stringSQL)
                    if ret == 0:
                        result[prop] = 0
                    else:
                        where = ""
                        for platform_id in cur.fetchall():
                            where += "`platform_id` = '"+platform_id[0]+"' OR "
                        stringSQL = "SELECT avg("+prop+") FROM "+DSTDB+" WHERE "+where[:-4]
                        cur.execute(stringSQL)
                        result[prop] = cur.fetchone()[0]
                    stringSQL = "UPDATE "+DSTDB+" SET `"+prop+"` = '"+str(result[prop])+"' WHERE `platform_id` = '"+platId+"B' AND `date` = '"+str(date-7*24*3600*2)+"'"
                    cur.execute(stringSQL)
                    conn.commit()
