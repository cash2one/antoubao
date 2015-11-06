#!/use/bin/python
#coding=utf-8

import sys
import string
import MySQLdb
import numpy as np
from atbtools.header import *
from atbtools.computeTools import get1DZeroArray
from matplotlib.finance import index_bar

if __name__ == "__main__":
    LEVEL=["C", "B", "B+", "B++", "A", "A+", "A++"]
    sconn=MySQLdb.connect(host=DBHOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    conn=MySQLdb.connect(host=DEVHOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
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

    index_list = ["score", "capital_adequacy_ratio", "activeness_credibility", "distribution", "mobility", "security", "pellucidity", "growth"]
    #index_list = ["score"]
    index_list = list(set(arrKeys) & set(index_list))
    index_number = len(index_list)
    score_index = index_list.index("score")
    for date_index in range(start, len(dates)):
        kv = {}
        kv['date'] = str(dates[date_index][0])
        print kv['date']

        #获取当前时间及之前所有坏站的status状态
        proAll = {}
        proDate = {}
        stringSQL = "SELECT platform_id, date, status FROM "+PRODB+" WHERE `date` <= '"+kv['date']+"' ORDER BY `date` DESC"
        scur.execute(stringSQL)
        for platId, date, status in scur.fetchall():
            if platId not in proAll:
                proAll[platId] = status
                proDate[platId] = int(date)
        
        value_list_dict = {}
        for index in index_list:
            value_list_dict[index] = []
        stringSQL = "SELECT " + ",".join(index_list) + " FROM "+SRCDB+" WHERE `date` = '"+kv['date']+"'"
        cur.execute(stringSQL)
        for rets in cur.fetchall():
            for i in range(index_number):
                value_list_dict[index_list[i]].append(rets[i])
        index_dict = {}
        index_sorted_dict = {}
        for index in index_list:
            index_dict[index] = {"A++": np.percentile(value_list_dict[index],97.5), "A+":np.percentile(value_list_dict[index],81.3), "A":np.percentile(value_list_dict[index],50), "B++":np.percentile(value_list_dict[index],49), "B+":np.percentile(value_list_dict[index],3.3113+16.8874), "B":np.percentile(value_list_dict[index],5.9)}
            index_sorted_dict[index] = sorted(index_dict[index].values())[::-1] #从高向低排
        scoreArr = index_sorted_dict["score"]
        scoreDict = index_dict["score"]
        platAll = []
        first = 0
        while True:
            warningArr = {}
            for index in index_list:
                warningArr[index] = {}
            punishArr = {}
            if first == 0:
                DB = SRCDB
            else:
                DB = DSTDB
            stringSQL = "SELECT platform_name, platform_id, " + ",".join(index_list) + " FROM "+DB+" WHERE `date` = '"+kv['date']+"'"
            cur.execute(stringSQL)
            for rets in cur.fetchall():
                platName = rets[0]
                platId = rets[1]
                value_list = rets[2:]
                score = value_list[score_index]
                if platId not in platAll:
                    platAll.append(platId)
                _date = kv['date']
                if platId in proAll.keys() and proAll[platId] < 0.89:
                    _date = (proDate[platId]-((proDate[platId]-1414252800)%(7*24*3600)))-(7*24*3600) #坏站用两周以前的数据
                stringSQL = "SELECT top10_ratio_loan, top5_ratio_loan, ave_annualized_return, weekly_total_borrower, weekly_lending FROM "+E2DB+" WHERE `date` = '"+str(_date)+"' AND `platform_id` = '"+platId+"'"
                ret = aCur.execute(stringSQL)
                if ret == 0:
                    continue
                top10,top5,ave,borrower,lending = aCur.fetchone()
                stringSQL = "SELECT not_returned_yet FROM "+E2DB+" WHERE `date` <= '"+str(_date)+"' AND `platform_id` = '"+platId+"' ORDER BY `date` DESC LIMIT 4"
                aCur.execute(stringSQL)
                yet = 0
                i = 0.4
                for _yet in aCur.fetchall():
                    yet += _yet[0]*i
                    i -= 0.1

                info = ""
                if platId not in LEVEL:
                    if platId in proAll.keys() and proAll[platId] < 0.89 and score > scoreArr[2]:
                        info += "#BADPLAT#"
                    if yet < 1 and score > scoreArr[1]:
                        info += "#YET#"
                    if (top10 > 0.25 and score > scoreArr[0]) or (top10 > 0.35 and score > scoreArr[1]) or (top10 > 0.55 and score > scoreArr[2]):
                        info += "#TOP10#"
                    if (ave > 15.5 and score > scoreArr[0]) or (ave > 15.99 and score > scoreArr[1]) or (ave > 16.99 and score > scoreArr[2]):
                        info += "#AVE#"
                    if (borrower < 50 and score > scoreArr[0]) or (borrower < 20 and score > scoreArr[1]) or (borrower < 5 and score > scoreArr[2]):
                        info += "#BORROWER#"
                    if (lending < 500 and score > scoreArr[1]) or (lending < 300 and score > scoreArr[2]):
                        info += "#LENDING#"
                    if info != "":
                        punishArr[platId] = info
                        for i in range(index_number):
                            warningArr[index_list[i]][platId] = value_list[i]

            _max = {}.fromkeys(index_list, 0)
            _min = {}.fromkeys(index_list, 0)
            if len(warningArr["score"]) != 0:
                for index in index_list:
                    _max[index] = max(warningArr[index].values())
                    _min[index] = min(warningArr[index].values())
            elif first == 1:
                break
            else:
                pass

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
                
                if kv['platform_id'] in warningArr["score"].keys():
                    kv['punishment'] = kv['score']
                    kv['punishment_info'] = punishArr[kv['platform_id']]
                    
                    #判断问题站所在的等级
                    pos = -1
                    for i in range(0, 3): #A++, A+, A
                        if warningArr["score"][kv['platform_id']] >= scoreArr[i]:
                            pos = i
                            score = scoreArr[i]
                            bscore = scoreArr[i+1]
                            break
                    if pos == -1:
                        continue
                    for index in index_list:
                        #score表示该等级的分数，bscore表示下一等级的分数
                        score = index_sorted_dict[index][pos]
                        bscore = index_sorted_dict[index][pos + 1]
                        if _max[index] == _min[index]:
                            kv[index] = bscore+((score-bscore)*0.625)
                        else:
                            kv[index] = (warningArr[index][kv['platform_id']]-_min[index])/(_max[index]-_min[index])*(score-bscore)*0.65+bscore+((score-bscore)*0.3)
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

            if first == 0:
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
                        stringSQL = "INSERT INTO "+DSTDB+"(`date`, `"+"`,`".join(arrKeys)+"`, `status`, `punishment`, `punishment_info`) VALUES('"+str(kv['date'])+"', '"+"','".join((str(a) for a in _list))+"', '"+str(proAll[platid])+"', '0', '')"
                        aCur.execute(stringSQL)
                        conn.commit()
        
        #统计TOP10平台各项平均值
        sigma = {}
        sigmaKeys = e2ArrKeys[:]
        sigmaKeys.remove('provision_of_risk_num')
        stringSQL = "SELECT `"+"`,`".join(sigmaKeys)+"` FROM platform_quantitative_data_3sigma_O WHERE `type` = 'high' AND `date` = '"+str(kv['date'])+"'"
        cur.execute(stringSQL)
        _list = cur.fetchone()
        for i in range(0, len(sigmaKeys)):
            if sigmaKeys[i] == 'platform_id' or sigmaKeys[i] == 'platform_name' or sigmaKeys[i] == 'date':
                continue
            sigma[sigmaKeys[i]] = _list[i]

        where = "(`platform_id` != '6372008a69' AND `platform_name` != 'strategy_report' AND `platform_id` != 'A++' AND `platform_id` != 'A+' AND `platform_id` != 'A' AND `platform_id` != 'B++' AND `platform_id` != 'B+' AND `platform_id` != 'B' AND `platform_id` != 'C')"
        stringSQL = "SELECT platform_id FROM "+DSTDB+" WHERE `date` = '"+str(kv['date'])+"' AND "+where+" ORDER BY `score` DESC"
        cur.execute(stringSQL)
        where = ""
        k = {}
        indexArray = []
        for _platId in cur.fetchall():
            platId = _platId[0]
            indexArray.append(platId)
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
            for i in range(0, len(indexArray)):
                platid = indexArray[i]
                if platid not in k:
                    continue
            #for platid in k.keys():
                if (key == 'weekly_ave_lending_per_borrower' or key == 'weekly_ave_lending_per_bid') and (k[platid]['weekly_ave_lending_per_borrower'] < k[platid]['weekly_ave_lending_per_bid']*0.9):
                    print "jump weekly_ave_lending_per_borrower&weekly_ave_lending_per_bid "+platid
                    continue
                if key != "provision_of_risk_num" and k[platid][key] > sigma[key]:
                    print "jump 3SIGMA ["+key+"]"+platid
                    continue
                #if key == 'registered_cap' and k[platid]['registered_cap'] > 50000:
                #    print "jump registered_cap "+platid
                #    continue
                if count >= 10:
                    break
                if key not in sumArr:
                    sumArr[key] = 0
                if key not in aveArr:
                    aveArr[key] = 0
                sumArr[key] += float(k[platid][key])
                count += 1
            if count != 0:
                aveArr[key] = float(sumArr[key]/count)

        stringSQL = "INSERT INTO "+E2DB+"(`platform_id`, `platform_name`, `date`, `"+"`,`".join(aveArr.keys())+"`) VALUES('strategyA', 'strategy_report', '"+str(kv['date'])+"', '"+"','".join(str(v) for v in aveArr.values())+"')"
        cur.execute(stringSQL)
        conn.commit()
