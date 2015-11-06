#!/usr/bin/python
#encoding=utf-8

from header import *

def usage():
    print "COMMAND:"
    print "\tpython "+sys.argv[0]+" [-all|-t|-p]"
    print ""
    print "OPTIONS:"
    print "\t-all: 计算所有周的平台维度分数"
    exit(-1)

def rank(scored, scoreRange):
    _score = {}
    scoreDict = {}
    for level in LEVEL_LIST[:-1]:
        scoreDict[np.percentile(scoreRange, LEVEL_PERCENTAGE_DICT[level])] = level
    for score in sorted(scoreDict.keys(), reverse=True):
        if scored['score'] > score:
            scored['level'] = scoreDict[score]
            break
    if 'level' not in scored:
        scored['level'] = "C"
    return scored

scount = 0

if len(sys.argv) < 2:
    usage()
elif sys.argv[1] == '-all':
    rSCORED.flushdb()
    #循环遍历所有平台，按照时间维度存入pinfoDict
    for platid in rQUASCO.keys():
        for timestamp in rQUASCO.hkeys(platid):
#             if int(timestamp) < SCOREDATE:
            if timestamp < SCOREDATE:
                continue
            jsonPlat = json.loads(rQUASCO.hget(platid, timestamp))
            #计算总分
            jsonScore = computeScore(jsonPlat)
            if jsonScore == '{}':
                continue
            jsonScore['platform_id'] = platid
            jsonScore['date'] = timestamp
            jsonScore['platform_name'] = jsonPlat['platform_name']
            jsonScore['source'] = jsonPlat['source']
            jsonScore['status'] = jsonPlat['status']
            fromHashToRedis(rSCORED, jsonScore, 'platform_id', 'date')
            scount += 1
    
quanti = readQuanti(rQUANTI)
scored, scoreRange = readScored(rSCORED)
setTop20Ave(rSTATIS, scoreRange, quanti, INVALID_TITLE)

#@谢博，在H表之后直接计算level
rSCORED.flushdb()
for platid in scored.keys():
    for timestamp in sorted(scored[platid]):
        scoreSort = sorted(scoreRange[timestamp].keys(), reverse=True)
        scored[platid][timestamp] = rank(scored[platid][timestamp], scoreSort)
        fromHashToRedis(rSCORED, scored[platid][timestamp], 'platform_id', 'date')
        
print "Score data("+str(scount)+") written to redis-db("+str(dbSCORED)+")!"