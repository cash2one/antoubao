#!/use/bin/python
#coding=utf-8

import MySQLdb
import time
import urllib
import urllib2
from atbtools.header import * 

#cache数据表
if __name__ == "__main__":
    conn=MySQLdb.connect(host=DEVHOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    cur=conn.cursor()
    aCur=conn.cursor()
    sconn=MySQLdb.connect(host=DBHOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    scur=sconn.cursor()

    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")
    cur.execute("SET CHARACTER_SET_CONNECTION=UTF8")
    scur.execute("SET NAMES 'UTF8'")
    scur.execute("SET CHARACTER SET UTF8")
    scur.execute("SET CHARACTER_SET_RESULTS=UTF8")
    scur.execute("SET CHARACTER_SET_CONNECTION=UTF8")

    SRCDB = {}
    SRCDB["platform_problem_record_Y"] = ["platform_id", "platform_name"]
    SRCDB["view_report"] = ["platform_id", "platform_name"]
    SRCDB["view_mobile"] = ["platform_id", "platform_name", "level"]
 
    DSTDB = "view_cache"

    cur.execute("TRUNCATE "+DSTDB)
    conn.commit()

    stringSQL = "SELECT DISTINCT platform_id FROM `platform_quantitative_data_E2` WHERE `platform_name` = 'strategy_report'"
    cur.execute(stringSQL)
    for platId in cur.fetchall():
        platId = platId[0]
        if platId == 'strategyA':
            platName = "前十平均"
        elif platId == 'strategyC':
            platName = "行业平均"
        elif platId[-1] == 'B':
            platName = "属性相似平均"
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`) VALUE('"+platId+"', '"+platName+"')"
        cur.execute(stringSQL)
    conn.commit()

    for table in SRCDB.keys():
        stringSQL = "SELECT "+",".join(SRCDB[table])+" FROM "+table
        if table == "platform_problem_record_Y":
            scur.execute(stringSQL)
            arrList = scur.fetchall()
        else:
            cur.execute(stringSQL)
            arrList = cur.fetchall()
        for _list in arrList:
            values = ""
            platid = ""
            in_mobile = ""
            kv = {}
            for i in range(0, len(_list)):
                kv[SRCDB[table][i]] = _list[i]
                if SRCDB[table][i] != 'platform_id':
                    if kv[SRCDB[table][i]] is None:
                        continue
                    else:
                        kv[SRCDB[table][i]] = _list[i]
                        values += "`"+SRCDB[table][i]+"` = '"+kv[SRCDB[table][i]]+"',"
                if SRCDB[table][i] == 'platform_id':
                    platid = _list[i]
            if table == "view_report":
                stringSQL = "SELECT * FROM "+table+" WHERE `show` = '1' AND `platform_id` = '"+str(platid)+"'"
                ret = aCur.execute(stringSQL)
                if ret == 0:
                    kv['report'] = '0'
                    values += "`report` = '0',"
                else:
                    kv['report'] = '1'
                    values += "`report` = '1',"
            elif table == "view_mobile":
                kv['in_mobile'] = '1'
                values += "`in_mobile` = '1',"
            else:
                kv['bad'] = '1'
                values += "`bad` = '1',"

            stringSQL = "SELECT * FROM "+DSTDB+" WHERE `platform_id` = '"+kv['platform_id']+"'"
            ret = aCur.execute(stringSQL)
            
            if ret == 0:
                stringSQL = "INSERT INTO "+DSTDB+"(`"+"`,`".join(kv.keys())+"`) VALUES('"+"','".join(kv.values())+"')"
            else:
                stringSQL = "UPDATE "+DSTDB+" SET "+values[:-1]+" WHERE `platform_id` = '"+kv['platform_id']+"'"
            aCur.execute(stringSQL)
            conn.commit()

    '''
    url = 'http://www.antoubao.cn/test/interface.php?data={"header":{"authcode":"ed3ca8b1e3211b8a8af1795c73faa842cff1af8c96ef6281830112f21c192bb4"}, "body":{"cmd":"reload"}}'
    urllib2.Request(url)
    '''
