#!/use/bin/python
#coding=utf-8

import re
import json
import datetime
import time
import sys
import string
from urllib import *
from urllib2 import *
import urllib
import urllib2
import MySQLdb
import random
from atbtools.header import *

#从指定的表里获取字段值列表，以platform_id和date作为指定条件
def getFieldsDictFromTableByIdByDate(cur,table_name,platform_id,date,fields_list):
    stringSQL = "SELECT " + ','.join(fields_list) +" FROM " + table_name+" WHERE `platform_id` = '" + str(platform_id) + "' AND `date` = '" + str(date) + "'"
    print stringSQL
    ret_number = cur.execute(stringSQL)
    ret_list = []
    if ret_number == 0:
        return {}.fromkeys(fields_list,0)
    else:
        for field in cur.fetchone():
            ret_list.append(field) 

if __name__ == "__main__":
    conn=MySQLdb.connect(host=DEVHOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    cur=conn.cursor()
    aCur=conn.cursor()
    connU=MySQLdb.connect(host=SERVERHOST, user="root", passwd="4njMOzOjli", db=DB, port=PORT)
    curU=connU.cursor()
    
    curU.execute("SET NAMES 'UTF8'")
    curU.execute("SET CHARACTER SET UTF8")
    curU.execute("SET CHARACTER_SET_RESULTS=UTF8")
    
    inlineCur=conn.cursor()
    insertCur=conn.cursor()
    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")

    SRCDB = "platform_score_T"
    DSTDB = "platform_vote_U"
    #新增字段来源设置
    srcdb_E1 = "platform_quantitative_data_E1"
    srcdb_P = "platform_score_P"
    srcdb_Q5 = "platform_alert_Q5"
    newfields_dict = {}
    newfields_dict[srcdb_E1] = ["not_returned_yet", "turnover_registered","top10_ratio_loan","short_term_debt_ratio"]
    newfields_dict[srcdb_P] = ["punishment","punishment_info"]
    newfields_dict[srcdb_Q5] = ["level_change"]
    #为防止重名字段，重新命名
    field_change_dict = {"punishment" : "punishment_P"}
    
    kv = {}
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

    arrKeys = {"capital_adequacy_ratio":2, "activeness_credibility":2, "distribution":2, "mobility":2, "security":2, "pellucidity":2, "growth":2}
    for date_index in range(start, len(dates)):
        for Type,Sort in {"good":"DESC", "bad":"ASC"}.items():
            arrValues = {}
            arrValues['platform_id'] = []
            arrValues['platform_name'] = []
            arrValues['punishment'] = []
            arrValues['good_times'] = []
            arrValues['bad_times'] = []
            
            kv = {}
            kv['date'] = str(dates[date_index][0])

            if Type == "good":
                stringSQL = "SELECT score FROM "+SRCDB+" WHERE `date` = '"+kv['date']+"' AND `platform_id` = 'A+'"
            else:
                stringSQL = "SELECT score FROM "+SRCDB+" WHERE `date` = '"+kv['date']+"' AND `platform_id` = 'B+'"
            cur.execute(stringSQL)
            score = cur.fetchone()[0]

            if Type == "good":
                stringSQL = "SELECT platform_id,platform_name,"+','.join(arrKeys.keys())+",punishment"+" FROM "+SRCDB+" WHERE `date` = '"+kv['date']+"' AND `score` > '"+str(score-0.0001)+"'"
            else:
                stringSQL = "SELECT platform_id,platform_name,"+','.join(arrKeys.keys())+",punishment"+" FROM "+SRCDB+" WHERE `date` = '"+kv['date']+"' AND `score` < '"+str(score+0.0001)+"'"
                
            kv['type'] = Type
            cur.execute(stringSQL)
            for _list in cur.fetchall():
                stringSQL = "SELECT weekly_lending FROM platform_quantitative_data_E2 WHERE `platform_id` = '"+_list[0]+"'"
                aCur.execute(stringSQL)
                lending = float(aCur.fetchone()[0])
                if lending <= 100:
                    continue
                for i in range(0, len(_list)):
                    if i == 0:
                        arrValues['platform_id'].append(_list[i])
                    elif i == 1:
                        arrValues['platform_name'].append(_list[i])
                    elif i == 9:
                        arrValues['punishment'].append(_list[i])
                    else:
                        if arrKeys.keys()[i-2] not in arrValues:
                            arrValues[arrKeys.keys()[i-2]] = []
                        arrValues[arrKeys.keys()[i-2]].append(_list[i])
                
                stringSQL = "SELECT count_good, count_bad FROM view_vote WHERE `platform_id` = '"+_list[0]+"'"
                curU.execute(stringSQL)
                times = curU.fetchone()
                if times != None:
                    if times[0] != None:
                        arrValues['good_times'].append(times[0])
                    else:
                        arrValues['good_times'].append(0) 
                    if times[1] != None:
                        arrValues['bad_times'].append(times[1])
                    else:
                        arrValues['bad_times'].append(0)
                else:
                    arrValues['good_times'].append(0)
                    arrValues['bad_times'].append(0)

            for index in range(0, len(arrValues['platform_id'])):
                kv['score'] = 0
                for i in range(0, len(arrValues.keys())):
                    key = arrValues.keys()[i]
                    if key not in arrKeys.keys():
                        kv[key] = arrValues[key][index] 
                    else:
                        value = arrValues[key][index]
                        count = 30
                        for v in arrValues[key]:
                            if v > value:
                                count -= 1
                        kv[key] = count
                        kv['score'] = kv['score'] + kv[key]
                        kv['score_'+key] = 0

                for k,v in arrKeys.items():
                    for _k,_v in arrKeys.items():
                        if _k == k:
                            rank = arrKeys[k]
                        else:
                            rank = 1
                        kv['score_'+_k] = kv['score_'+_k] + (kv[k] * rank)

                #新增字段
                kv['score_update'] = kv['score'] + 30 * kv['good_times'] - 30 * kv['bad_times']
                for _database in newfields_dict:
                    _dict = getFieldsDictFromTableByIdByDate(cur, _database, arrValues['platform_id'][index], kv['date'], newfields_dict[_database])
                    for _field in newfields_dict[_database]:
                        if _field in field_change_dict:
                            kv[field_change_dict[_field]] = _dict[_field]
                        else:
                            kv[_field] = _dict[_field]

                keys = ""
                values = ""
                for k,v in kv.items():
                    keys = keys + "`"+k+"`,"
                    values = values + "'"+str(v)+"',"
                stringSQL = "INSERT INTO "+DSTDB+"("+keys[:-1]+") VALUES("+values[:-1]+")"
                cur.execute(stringSQL)
                conn.commit()
