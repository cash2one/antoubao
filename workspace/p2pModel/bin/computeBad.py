#!/usr/bin/python
#encoding=utf-8

from header import *

def usage():
    print "COMMAND:"
    print "\tpython "+sys.argv[0]+" [-all|-t|-p]"
    print ""
    print "OPTIONS:"
    print "\t-all: 计算所有坏站的分数"
    print "\t-t [timestamp]: 计算指定周的坏站分数"
    print "\t-p [platform_id]: 计算指定坏站的分数"
    exit(-1)

count = 0
statis = {}

def getData():
    #读取定量数据
    quanti = readQuanti(rQUABAD)

    #读取定性数据
    qualit = readQualit(rQUALIT)

    #读取统计数据
    statis = readStatis(rSTATIS)

    return quanti, qualit, statis

quanti, qualit, statis = getData()

rSCOBAD.flushdb()

for platid in rQUABAD.keys():
    if platid not in qualit.keys():
        continue
    line_punish = {}
    for timestamp in rQUABAD.hkeys(platid):
        if timestamp < SCOREDATE:
            continue
        jsonBad = {}
        quasco = {}
        scored = {}
        punish = {}
        line_punish = {}
        if timestamp not in statis:
            statis[timestamp] = readStatis(rSTATIS, timestamp)
        #计算定量分数
        quasco = computeQuantitativeScore(quanti[platid][timestamp], qualit[platid], statis[timestamp])
        if quasco == '{}':
            continue
        for k,v in quasco.items():
            jsonBad[k] = v

        #计算总分
        scored = computeScore(quasco)
        if scored == '{}':
            continue
        for k,v in scored.items():
            jsonBad[k] = v

        #惩罚
        punish = simplePunish(quanti[platid][timestamp], qualit[platid], scored, statis[timestamp]['TOP20'], W)
        if punish == '{}':
            continue
        for k,v in punish.items():
            jsonBad[k] = v

        line_punish = linePunish(punish, quanti, platid, timestamp, W, INVALID_TITLE)
        if line_punish == '{}':
            continue
        for k,v in line_punish.items():
            jsonBad[k] = v

        jsonBad['platform_id'] = platid
        jsonBad['date'] = timestamp
        jsonBad['platform_name'] = quasco['platform_name']        
        count += 1

        #写入坏站分数
        fromHashToRedis(rSCOBAD, jsonBad, 'platform_id', 'date')

print "Bad-platform data("+str(count)+") written to redis-db("+str(dbSCOBAD)+")!"
