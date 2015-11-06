#!/usr/bin/python
#encoding=utf-8

from header import *

def usage():
    print "COMMAND:"
    print "\tpython "+sys.argv[0]+" [-all|-t|-p]"
    print ""
    print "OPTIONS:"
    print "\t-all: 计算所有周的平台分数"
    print "\t-t [timestamp]: 计算指定周的平台分数"
    print "\t-p [platform_id]: 计算指定平台的分数"
    exit(-1)

qcount = 0
scount = 0
statis = {}

if len(sys.argv) < 2:
    usage()
elif sys.argv[1] == '-all':
    rQUASCO.flushdb()
    rSCORED.flushdb()
    #循环遍历所有平台，按照时间维度存入pinfoDict
    for platid in rQUANTI.keys():
        for timestamp in rQUANTI.hkeys(platid):
            if timestamp < SCOREDATE:
                continue
            if timestamp not in statis:
                statis[timestamp] = readStatis(rSTATIS, timestamp)
            #计算定量分数
            jsonPlat = computeQuantitativeScore(rQUANTI.hget(platid, timestamp), rQUALIT.get(platid), statis[timestamp])
            if jsonPlat == '{}':
                continue
            fromHashToRedis(rQUASCO, jsonPlat, 'platform_id', 'date')
            qcount += 1
            #计算总分
            jsonScore = computeScore(jsonPlat)
            if jsonScore == '{}':
                continue
            jsonScore['platform_id'] = platid
            jsonScore['date'] = timestamp
            jsonScore['platform_name'] = jsonPlat['platform_name']
            fromHashToRedis(rSCORED, jsonScore, 'platform_id', 'date')
            scount += 1
elif sys.argv[1] == '-t':
    #-t 参数合法性检查
    if len(sys.argv) < 3:
        usage()
    else:
        timestamp = int(sys.argv[2])
        if timestamp < SCOREDATE:
            print "Invalid date("+str(timestamp)+"), the must be equal or greater than "+str(SCOREDATE)
            exit(-1)
    #读取统计数据
    if timestamp not in statis:
        statis[timestamp] = readStatis(rSTATIS, timestamp)
    #循环遍历所有平台
    for platid in rQUANTI.keys():
        jsonPlat = computeQuantitativeScore(rQUANTI.hget(platid, timestamp), rQUALIT.get(platid), statis[timestamp])
        if jsonPlat == '{}':
            continue
        fromHashToRedis(rQUASCO, jsonPlat, 'platform_id', 'date')
        qcount += 1
        jsonScore = computeScore(jsonPlat)
        if jsonScore == '{}':
            continue
        jsonScore['platform_id'] = platid
        jsonScore['date'] = timestamp
        fromHashToRedis(rSCORED, jsonScore, 'platform_id', 'date')
        scount += 1
elif sys.argv[1] == '-p':
    #-p 参数合法性检查
    if len(sys.argv) < 3:
        usage()
    else:
        platid = sys.argv[2]
        if len(platid) != 10:
            print "Invalid platform_id("+str(platid)+")"
            exit(-1)
    #循环遍历指定平台的所有日期数据
    for timestamp in rQUANTI.hkeys(platid):
        if timestamp not in statis:
            statis[timestamp] = readStatis(rSTATIS, timestamp)
        jsonPlat = computeQuantitativeScore(rQUANTI.hget(platid, timestamp), rQUALIT.get(platid), statis[timestamp])
        if jsonPlat == '{}':
            continue
        fromHashToRedis(rQUASCO, jsonPlat, 'platform_id', 'date')
        qcount += 1
        jsonScore = computeScore(jsonPlat)
        if jsonScore == '{}':
            continue
        jsonScore['platform_id'] = platid
        jsonScore['date'] = timestamp
        fromHashToRedis(rSCORED, jsonScore, 'platform_id', 'date')
        scount += 1
else:
    usage()

quanti = readQuanti(rQUANTI)
scored, scoreRange = readScored(rSCORED)
setTop20Ave(rSTATIS, scoreRange, quanti, INVALID_TITLE)

print "Score data("+str(qcount)+") written to redis-db("+str(dbQUASCO)+")!"
print "Score data("+str(scount)+") written to redis-db("+str(dbSCORED)+")!"
