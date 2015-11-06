#!/usr/bin/python
#encoding=utf-8

from header import *

def usage():
    print "COMMAND:"
    print "\tpython "+sys.argv[0]+" [-all|-t|-p]"
    print ""
    print "OPTIONS:"
    print "\t-all: 执行所有周的惩罚策略"
    print "\t-t [timestamp]: 执行指定周的惩罚策略"
    print "\t-p [platform_id]: 计算指定平台的惩罚策略"
    exit(-1)

def getData():
    #读取定量数据
    quanti = readQuanti(rQUANTI)

    #读取定性数据
    qualit = readQualit(rQUALIT)

    #读取状态数据
    status = readStatus(rSTATUS)
    
    #读取总分
    scored, scoreRange = readScored(rSCORED) 

    #读取统计数据
    statis = readStatis(rSTATIS)
    
    return quanti, qualit, scored, statis, status

result = {}
count = 0

if len(sys.argv) < 2:
    usage()
elif sys.argv[1] == '-all':
    #准备数据
    rPUNISH.flushdb()
    quanti, qualit, scored, statis, status = getData()
    for platid in scored.keys():
        if platid not in result.keys():
            result[platid] = {}
        if platid not in status.keys():
            status[platid] = 1
        for timestamp in scored[platid]:
            #本周数据单项惩罚
            result[platid][timestamp] = simplePunish(quanti[platid][timestamp], qualit[platid], scored[platid][timestamp], statis[timestamp]['TOP20'], W)
            #纵向惩罚
            result[platid][timestamp] = linePunish(result[platid][timestamp], quanti, platid, timestamp, W, INVALID_TITLE)
            #呵呵惩罚
            if platid in hehePunish.keys():
                result[platid][timestamp]['score'] -= hehePunish[platid]
            fromHashToRedis(rPUNISH, result[platid][timestamp], 'platform_id', 'date') 
            count += 1
elif sys.argv[1] == '-t':
    #-t 参数合法性检查
    if len(sys.argv) < 3:
        usage()
    else:
        timestamp = int(sys.argv[2])
        if timestamp < SCOREDATE:
            print "Invalid date("+str(timestamp)+"), the must be equal or greater than "+str(SCOREDATE)
            exit(-1)
    #准备数据
    quanti, qualit, scored, statis, status = getData()
    for platid in scored.keys():
        if platid not in result.keys():
            result[platid] = {}
        if platid not in status.keys():
            status[platid] = 1
        #本周数据单项惩罚
        result[platid][timestamp] = simplePunish(quanti[platid][timestamp], qualit[platid], scored[platid][timestamp], statis[timestamp]['TOP20'], W)
        #纵向惩罚
        result[platid][timestamp] = linePunish(result[platid][timestamp], quanti, platid, timestamp, W, INVALID_TITLE)
        fromHashToRedis(rPUNISH, result[platid][timestamp], 'platform_id', 'date')
        count += 1
elif sys.argv[1] == '-p':
    #-p 参数合法性检查
    if len(sys.argv) < 3:
        usage()
    else:
        platid = sys.argv[2]
        if len(platid) != 10:
            print "Invalid platform_id("+str(platid)+")"
            exit(-1)
    #准备数据
    quanti, qualit, scored, statis, status = getData()
    result[platid] = {}
    status[platid] = 1
    for timestamp in scored[platid]:
        #本周数据单项惩罚
        result[platid][timestamp] = simplePunish(quanti[platid][timestamp], qualit[platid], scored[platid][timestamp], statis[timestamp]['TOP20'], W)
        #纵向惩罚
        result[platid][timestamp] = linePunish(result[platid][timestamp], quanti, platid, timestamp, W, INVALID_TITLE)
        fromHashToRedis(rPUNISH, result[platid][timestamp], 'platform_id', 'date')
        count += 1
else:
    usage()

print "Punishment data("+str(count)+") written to redis-db("+str(dbPUNISH)+")!"
