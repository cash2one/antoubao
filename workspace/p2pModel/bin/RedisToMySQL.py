#!/usr/bin/python
#encoding=utf-8

from header import *

def usage():
    print "COMMAND:"
    print "\tpython "+sys.argv[0]+" [-t|all]"
    print ""
    print "OPTIONS:"
    print "\t-all: 同步Redis中的所有数据到MySQL"
    print "\t-t [REDIS-DB No.]: 同步Redis中指定Table的数据到MySQL"
    print ""
    print "REDIS-DB No.:"
    print "\t"+str(dbSTATIS)+"\tIJKLMNO_statis"
    for k,v in TABLE.items():
        print "\t"+str(k)+"\t"+str(v)
    exit(-1)

def dumpStatis(DATACUR, DATACONN, rSTATIS, TYPES):
    print "Dump Statis Data ..."
    for t,table in TYPES.items():
        DATACUR.execute("DELETE FROM `"+table+"`")
        DATACONN.commit()
        for timestamp in rSTATIS.hkeys(t):
            values = json.loads(rSTATIS.hget(t, timestamp))
            if "SIG" in t:
                v = {}
                v['h'] = {}
                v['l'] = {}
                v['h']['date'] = timestamp
                v['l']['date'] = timestamp
                for key,value in values.items():
                    if key[-2:] == "_h":
                        v['h'][key[:-2]] = value
                        v['h']['type'] = "h"
                    elif key[-2:] == "_l":
                        v['l'][key[:-2]] = value
                        v['l']['type'] = "l"
                    else:
                        v['h'][key] = value
                        v['l'][key] = value
                fromHashToMySQL(DATACUR, DATACONN, TYPES[t], v['h'])
                fromHashToMySQL(DATACUR, DATACONN, TYPES[t], v['l'])
            else:
                v = values
                v['date'] = timestamp
                fromHashToMySQL(DATACUR, DATACONN, TYPES[t], v)

def dumpData(DATACUR, DATACONN, rTABLE, myTABLE):
    print "Dump "+myTABLE+" Data ..."
    DATACUR.execute("DELETE FROM `"+myTABLE+"`")
    DATACONN.commit()
    for platid in rTABLE.keys():
        for timestamp in rTABLE.hkeys(platid):
            values = json.loads(rTABLE.hget(platid, timestamp))
            fromHashToMySQL(DATACUR, DATACONN, myTABLE, values)

if len(sys.argv) < 2:
    usage()
elif sys.argv[1] == '-all':
    #下载统计表
    dumpStatis(DATACUR, DATACONN, rSTATIS, TYPES)
    #下载数据表
    for table in TABLE.keys():
        r = redis.Redis(host=REDISHOST, port=REDISPORT, db=table)
        dumpData(DATACUR, DATACONN, r, TABLE[table])
elif sys.argv[1] == '-t':
    #-t 参数合法性检查
    if len(sys.argv) < 3:
        usage()
    else:
        table = int(sys.argv[2])
    if table == dbSTATIS:
        dumpStatis(DATACUR, DATACONN, rSTATIS, TYPES)
    elif table in TABLE.keys():
        r = redis.Redis(host=REDISHOST, port=REDISPORT, db=table)
        if table == 8 or table == 10 or table == 0:
            dumpData(DEVCUR, DEVCONN, r, TABLE[table])
        else:
            dumpData(DATACUR, DATACONN, r, TABLE[table])
    else:
        usage()
else:
    usage()
