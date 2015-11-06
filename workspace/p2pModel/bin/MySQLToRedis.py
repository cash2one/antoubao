#!/usr/bin/python
#encoding=utf-8

from header import *

def usage():
    print "COMMAND:"
    print "\tpython "+sys.argv[0]+" [-t|all]"
    print ""
    print "OPTIONS:"
    print "\t-all: 同步MySQL中的所有数据到Redis"
    print "\t-t [REDIS-DB No.]: 同步MySQL中指定Table的数据到Redis"
    print ""
    print "REDIS-DB No.:"
    print "\t"+str(dbSTATIS)+"\tIJKLMNO_statis"
    for k,v in TABLE.items():
        print "\t"+str(k)+"\t"+str(v)
    exit(-1)

def dumpStatis(DATACUR, DATACONN, rSTATIS, TYPES):
    for key,table in TYPES.items():
        arrKeys = []
        stringSQL = "SHOW FULL COLUMNS FROM "+table
        DATACUR.execute(stringSQL)
        for col in DATACUR.fetchall():
            if col[0] != "id":
                arrKeys.append(col[0])

        v = {}
        stringSQL = "SELECT `"+"`,`".join(arrKeys)+"` FROM "+table
        DATACUR.execute(stringSQL)
        for values in DATACUR.fetchall():
            d = {}
            for i in range(0, len(values)):
                v[arrKeys[i]] = values[i]
            if 'type' in v.keys():
                for _k, _v in v.items():
                    if _k != 'date' and _k != 'type' and _k[-2:] != '_l' and _k[-2:] != '_h':
                        v[_k+"_"+v['type']] = _v
                if _k+"_l" not in v.keys() or _k+"_h" not in v.keys():
                    continue
                for _k in v.keys():
                    if _k != 'date' and _k != 'type' and _k[-2:] != '_l' and _k[-2:] != '_h':
                        del v[_k]
                del v['type']
            d['db'] = key
            d['date'] = str(v['date'])
            d['value'] = v
            v = {}
            fromHashToRedis(rSTATIS, d, 'db', 'date', 'value')

def dumpData(DATACUR, DATACONN, rTABLE, myTABLE):
    arrKeys = []
    stringSQL = "SHOW FULL COLUMNS FROM "+table
    DATACUR.execute(stringSQL)
    for col in DATACUR.fetchall():
        if col[0] != "id":
            arrKeys.append(col[0])

    stringSQL = "SELECT"
    return None

if len(sys.argv) < 2:
    usage()
elif sys.argv[1] == '-all':
    #上传统计表
    dumpStatis(DATACUR, DATACONN, rSTATIS, TYPES)
    
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
        dumpData(DATACUR, DATACONN, r, TABLE[table])
    else:
        usage()
else:
    usage()
