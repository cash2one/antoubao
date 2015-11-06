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

def rank(scored, scoreRange):
    _score = {}
    scoreDict = {}
    for level in LEVEL_LIST[:-1]:
        scoreDict[np.percentile(scoreRange, LEVEL_PERCENTAGE_DICT[level])] = level
    for score in sorted(scoreDict.keys(), reverse=True):
        if scored['score'] > score:
            scored['level'] = scoreDict[score]
            break
    else:
        scored['level'] = "C"
    return scored

def getData():
    #读取定量数据
    quanti = readQuanti(rQUANTI)

    #读取定性数据
    qualit = readQualit(rQUALIT)

    #读取总分
    scored, scoreRange = readScored(rSCORED) 

    #读取统计数据
    statis = readStatis(rSTATIS)
    
    return quanti, qualit, scored, scoreRange,  statis

result = {}
count = 0
punish_dict = getPunishmentDict()

if len(sys.argv) < 2:
    usage()
elif sys.argv[1] == '-all':
    #准备数据
    rPUNISH.flushdb()
    quanti, qualit, scored, scoreRange, statis = getData()
    for platid in scored.keys():
        if platid not in result.keys():
            result[platid] = {}
        for timestamp in scored[platid]:
            scoreSort = sorted(scoreRange[timestamp].keys(), reverse=True)
            #本周数据单项惩罚
            result[platid][timestamp] = simplePunish(quanti[platid][timestamp], qualit[platid], scored[platid][timestamp], statis[timestamp]['TOP20'], W, punish_dict)
            #纵向惩罚
            result[platid][timestamp] = linePunish(result[platid][timestamp], quanti, platid, timestamp, W, INVALID_TITLE, punish_dict)
            #总分扣除
            result[platid][timestamp]['score_initial'] = result[platid][timestamp]['score']
            result[platid][timestamp]['level_initial'] = result[platid][timestamp]['level']
            result[platid][timestamp]['score'] -= result[platid][timestamp]['punishment']
            #呵呵惩罚
            result[platid][timestamp]['hehepunishment'] = 0
            if platid in hehePunish.keys():
                result[platid][timestamp]['hehepunishment'] = hehePunish[platid]
                result[platid][timestamp]['score'] -= hehePunish[platid]
            fromHashToRedis(rPUNISH, result[platid][timestamp], 'platform_id', 'date')
            count += 1
    #@谢博，在H表之后直接计算level
    scored, scoreRange = readScored(rPUNISH)
    rPUNISH.flushdb()
    for platid in scored.keys():
        for timestamp in sorted(scored[platid]):
            scoreSort = sorted(scoreRange[timestamp].keys(), reverse=True)
            result[platid][timestamp] = rank(result[platid][timestamp], scoreSort)
            fromHashToRedis(rPUNISH, result[platid][timestamp], 'platform_id', 'date')
            
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
    quanti, qualit, scored, scoreRange, statis = getData()
    for platid in scored.keys():
        if platid not in result.keys():
            result[platid] = {}
        #本周数据单项惩罚
        result[platid][timestamp] = simplePunish(quanti[platid][timestamp], qualit[platid], scored[platid][timestamp], statis[timestamp]['TOP20'], W, punish_dict)
        #纵向惩罚
        result[platid][timestamp] = linePunish(result[platid][timestamp], quanti, platid, timestamp, W, INVALID_TITLE, punish_dict)
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
    quanti, qualit, scored, scoreRange, statis = getData()
    result[platid] = {}
    for timestamp in scored[platid]:
        #本周数据单项惩罚
        result[platid][timestamp] = simplePunish(quanti[platid][timestamp], qualit[platid], scored[platid][timestamp], statis[timestamp]['TOP20'], W, punish_dict)
        #纵向惩罚
        result[platid][timestamp] = linePunish(result[platid][timestamp], quanti, platid, timestamp, W, INVALID_TITLE, punish_dict)
        fromHashToRedis(rPUNISH, result[platid][timestamp], 'platform_id', 'date')
        count += 1
else:
    usage()

print "Punishment data("+str(count)+") written to redis-db("+str(dbPUNISH)+")!"