#!/use/bin/python
#coding=utf-8

import sys
import string
import MySQLdb
import numpy as np
from header import *

if __name__ == "__main__":
    sconn=MySQLdb.connect(host="db-x1.antoubao.cn", user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    conn=MySQLdb.connect(host=HOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    scur=sconn.cursor()
    cur=conn.cursor()
    aCur=conn.cursor()

    scur.execute("SET NAMES 'UTF8'")
    scur.execute("SET CHARACTER SET UTF8")
    scur.execute("SET CHARACTER_SET_RESULTS=UTF8")
    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    SRCDB = "platform_score_S"
    DSTDB = "platform_score_T"
    E2DB = "platform_quantitative_data_E2"
    PRODB = "platform_problem_record_Y"

    arrKeys = []
    stringSQL = "SHOW FULL COLUMNS FROM "+SRCDB
    cur.execute(stringSQL)
    for col in cur.fetchall():
        if (col[0] == "id") or (col[0] == "date") or (col[0] == "punishment") or (col[0] == "punishment_info"):
            continue
        arrKeys.append(col[0])
    
    e2ArrKeys = []
    stringSQL = "SHOW FULL COLUMNS FROM "+E2DB
    cur.execute(stringSQL)
    for col in cur.fetchall():
        if (col[0] == "platform_id") or (col[0] == "platform_name") or (col[0] == "id") or (col[0] == "date") or (col[0] == "weekly_outstanding_loan") or (col[0] == "in_and_out") or (col[0] == "future4week_maturity") or (col[0] == "black"):
            continue
        e2ArrKeys.append(col[0])
    
    stringSQL = "SELECT DISTINCT date FROM "+SRCDB+" ORDER BY date ASC"
    cur.execute(stringSQL)
    dates = cur.fetchall()

    start = len(dates)-1
    if (len(sys.argv) == 2):
        if (sys.argv[1] == "reset"):
            start = 0
            cur.execute("TRUNCATE "+DSTDB)
            conn.commit()
    else:
        cur.execute("DELETE FROM "+DSTDB+" WHERE `date` = '"+str(dates[start][0])+"'")
        conn.commit()

    for date_index in range(start, len(dates)):
        kv = {}
        kv['date'] = str(dates[date_index][0])

        #获取当前时间及之前所有坏站的status状态
        proAll = {}
        proDate = {}
        stringSQL = "SELECT platform_id, date, status FROM "+PRODB+" WHERE `date` <= '"+kv['date']+"' ORDER BY `date` DESC"
        scur.execute(stringSQL)
        for platId, date, status in scur.fetchall():
            if platId not in proAll:
                proAll[platId] = status
                proDate[platId] = int(date)

        stringSQL = "SELECT score FROM "+SRCDB+" WHERE `date` = '"+kv['date']+"'"
        cur.execute(stringSQL)
        score = cur.fetchall()

        scoreDict = {"A++": np.percentile(score,97.2), "A+":np.percentile(score,96-13.09), "A":np.percentile(score,67.6), "B++":np.percentile(score,3.3113+16.8874+26.8212), "B+":np.percentile(score,3.3113+16.8874), "B":np.percentile(score,3.3113)}
        scoreArr = sorted(scoreDict.values())[::-1]

        platAll = []
        first = 0
        while True:
            warningArr = {}
            punishArr = {}
            if first == 0:
                DB = SRCDB
            else:
                DB = DSTDB

            stringSQL = "SELECT platform_name, platform_id, score FROM "+DB+" WHERE `date` = '"+kv['date']+"'"
            cur.execute(stringSQL)
            for platName, platId, score in cur.fetchall():
                if platId not in platAll:
                    platAll.append(platId)
                stringSQL = "SELECT top10_ratio_loan, top5_ratio_loan, ave_annualized_return, weekly_total_borrower, weekly_lending FROM "+E2DB+" WHERE `date` = '"+kv['date']+"' AND `platform_id` = '"+platId+"'"
                aCur.execute(stringSQL)
                top10,top5,ave,borrower,lending = aCur.fetchone()
                stringSQL = "SELECT not_returned_yet FROM "+E2DB+" WHERE `date` <= '"+kv['date']+"' AND `platform_id` = '"+platId+"' ORDER BY `date` DESC LIMIT 4"
                aCur.execute(stringSQL)
                yet = 0
                i = 0.4
                for _yet in aCur.fetchall():
                    yet += _yet[0]*i
                    i -= 0.1

                info = ""
                if platId not in LEVEL:
                    if yet < 1 and score > scoreArr[1]:
                        info += "#YET#"
                    if (top10 > 0.25 and score > scoreArr[0]) or (top10 > 0.35 and score > scoreArr[1]) or (top10 > 0.55 and score > scoreArr[2]):
                        info += "#TOP10#"
                    if (ave > 16 and score > scoreArr[0]) or (ave > 17 and score > scoreArr[1]) or (ave > 19.5 and score > scoreArr[2]):
                        info += "#AVE#"
                    if (borrower < 50 and score > scoreArr[0]) or (borrower < 20 and score > scoreArr[1]) or (borrower < 5 and score > scoreArr[2]):
                        info += "#BORROWER#"
                    if (lending < 500 and score > scoreArr[1]) or (lending < 200 and score > scoreArr[2]):
                        info += "#LENDING#"
                    if info != "":
                        warningArr[platId] = score
                        punishArr[platId] = info

            if len(warningArr.values()) != 0:
                _max = max(warningArr.values())
                _min = min(warningArr.values())
            elif first == 1:
                break
            else:
                _max = 0
                _min = 0

            stringSQL = "SELECT "+','.join(arrKeys)+" FROM "+DB+" WHERE `date` = '"+kv['date']+"'"
            cur.execute(stringSQL)
            for _list in cur.fetchall():
                kv['status'] = 1
                kv['punishment'] = 0
                kv['punishment_info'] = ""
                for i in range(0, len(_list)):
                    kv[arrKeys[i]] = _list[i] 
                    if arrKeys[i] == 'platform_id' and _list[i] in proAll:
                        kv['status'] = proAll[_list[i]]
            
                if kv['platform_id'] in LEVEL:
                    kv['score'] = scoreDict[kv['platform_id']]
                
                if kv['platform_id'] in warningArr.keys():
                    kv['punishment'] = kv['score']
                    kv['punishment_info'] = punishArr[kv['platform_id']]

                    for i in range(0, 3):
                        if warningArr[kv['platform_id']] >= scoreArr[i]:
                            score = scoreArr[i]
                            bscore = scoreArr[i+1]
                            break
                    if _max == _min:
                        kv['score'] = bscore+((score-bscore)*0.625)
                    else:
                        kv['score'] = (warningArr[kv['platform_id']]-_min)/(_max-_min)*(score-bscore)*0.65+bscore+((score-bscore)*0.3)
                keys = ""
                values = ""
                if first == 0:
                    for _k,_v in kv.items():
                        keys += "`"+_k+"`,"
                        values += "'"+str(_v)+"',"

                    stringSQL = "INSERT INTO "+DSTDB+"("+keys[:-1]+") VALUES("+values[:-1]+")"
                else:
                    for _k,_v in kv.items():
                        if _k != "punishment" and _k != "punishment_info":
                            values += "`"+_k+"` = '"+str(_v)+"',"
                    stringSQL = "UPDATE "+DSTDB+" SET "+values[:-1]+" WHERE `platform_id` = '"+kv['platform_id']+"' AND `date` = '"+kv['date']+"'"
                aCur.execute(stringSQL)
                conn.commit()
            first = 1

        #问题站数据补全
        stringSQL = "SELECT DISTINCT platform_id FROM "+DSTDB+" WHERE `date` < '"+str(kv['date'])+"'"
        cur.execute(stringSQL)
        for platid in cur.fetchall():
            platid = platid[0]
            if platid not in platAll and platid in proAll:
                stringSQL = "SELECT `"+"`,`".join(arrKeys)+"` FROM "+DSTDB+" WHERE `platform_id` = '"+platid+"' AND `date` < '"+str(proDate[platid]-7*24*3600)+"' AND `date` > '"+str(proDate[platid]-2*7*24*3600)+"'"
                ret = aCur.execute(stringSQL)
                if ret == 0:
                    continue
                _list = aCur.fetchone()
                stringSQL = "INSERT INTO "+DSTDB+"(`date`, `"+"`,`".join(arrKeys)+"`, `status`) VALUES('"+str(kv['date'])+"', '"+"','".join((str(a) for a in _list))+"', '"+str(proAll[platid])+"')"
                aCur.execute(stringSQL)
                conn.commit()

        #统计TOP10平台各项平均值
        where = "(`platform_name` != 'strategy_report' AND `platform_id` != 'A++' AND `platform_id` != 'A+' AND `platform_id` != 'A' AND `platform_id` != 'B++' AND `platform_id` != 'B+' AND `platform_id` != 'B' AND `platform_id` != 'C')"
        stringSQL = "SELECT platform_id FROM "+DSTDB+" WHERE `date` = '"+str(kv['date'])+"' AND "+where+" ORDER BY `score` DESC"
        cur.execute(stringSQL)
        where = ""
        k = {}
        for _platId in cur.fetchall():
            platId = _platId[0]
            for key in e2ArrKeys:
                if key == 'platform_id' or key == 'platform_name' or key == 'date':
                    continue
                stringSQL = "SELECT "+key+" FROM "+E2DB+" WHERE `date` = '"+str(kv['date'])+"' AND `platform_id` = '"+platId+"'"
                ret = aCur.execute(stringSQL)
                if ret == 0:
                    continue
                if platId not in k:
                    k[platId] = {}
                if key not in k[platId]:
                    k[platId][key] = aCur.fetchone()[0]

        #初期数据不规范
        if len(k.keys()) < 10:
            continue

        aveArr = {}
        sumArr = {}
        for key in e2ArrKeys:
            if key == 'platform_id' or key == 'platform_name' or key == 'date':
                continue
            count = 0
            for platid in k.keys():
                if (key == 'weekly_ave_lending_per_borrower' or key == 'weekly_ave_lending_per_bid') and (k[platid]['weekly_ave_lending_per_borrower'] < k[platid]['weekly_ave_lending_per_bid']):
                    print "jump weekly_ave_lending_per_borrower&weekly_ave_lending_per_bid "+platid
                    continue
                if key == 'registered_cap' and k[platid]['registered_cap'] > 50000:
                    print "jump registered_cap "+platid
                    continue
                if count >= 10:
                    break
                if key not in sumArr:
                    sumArr[key] = 0
                if key not in aveArr:
                    aveArr[key] = 0
                sumArr[key] += float(k[platid][key])
                count += 1
            aveArr[key] = float(sumArr[key]/count)

        stringSQL = "INSERT INTO "+E2DB+"(`platform_id`, `platform_name`, `date`, `"+"`,`".join(aveArr.keys())+"`) VALUES('strategyA', 'strategy_report', '"+str(kv['date'])+"', '"+"','".join(str(v) for v in aveArr.values())+"')"
        cur.execute(stringSQL)
        conn.commit()
