#!/usr/bin/python
#encoding=utf-8

from header import *

def usage():
    print "COMMAND:"
    print "\tpython "+sys.argv[0]+" [-all|-t|-p]"
    print ""
    print "OPTIONS:"
    print "\t-all: 执行所有周的数据平滑策略"
    print "\t-t [timestamp]: 执行指定周的数据平滑策略"
    print "\t-p [platform_id]: 计算指定平台的数据平滑策略"
    exit(-1)

def getData():
    #读取总分
    scored, scoreRange = readScored(rPUNISH)
    
    #读取状态
    status = readStatus(rSTATUS)
    
    return status, scored

'''
def fourWeekAve(scored, timestamp):
    ratios = []
    result = {}
    result[timestamp] = {}
    timestamps = sorted(scored.keys(), reverse=True)
    pos = timestamps.index(timestamp)
    count = len(timestamps)-pos
    if count == 1:
        ratios = [1]
    elif count == 2:
        ratios = [0.7, 0.3]
    elif count == 3:
        ratios = [0.6, 0.2, 0.2]
    else:
        ratios = [0.4, 0.3, 0.2, 0.1]
    i = 0
    for ratio in ratios:
        for key in scored[timestamps[pos+i]].keys():
            if key in INVALID_TITLE:
                if "punishment" not in key:
                    result[timestamp][key] = scored[timestamp][key]
                continue
            if key not in result[timestamp].keys():
                result[timestamp][key] = 0
            if scored[timestamps[pos+i]][key] is None:
                continue
            result[timestamp][key] += scored[timestamps[pos+i]][key]*ratio
        i += 1
    return result[timestamp]
'''
result = {}
count = 0

if len(sys.argv) < 2:
    usage()
elif sys.argv[1] == '-all':
    #准备数据
    rSMOOTH.flushdb()
    status, scored = getData()
    for platid in scored.keys():
        if platid not in result.keys():
            result[platid] = {}
        for timestamp in scored[platid]:
            #四周平均
            result[platid][timestamp] = fourWeekAve(scored[platid], timestamp, INVALID_TITLE)
            fromHashToRedis(rSMOOTH, result[platid][timestamp], 'platform_id', 'date')
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
    status, scored = getData()
    for platid in scored.keys():
        if platid not in result.keys():
            result[platid] = {}
        #四周平均
        result[platid][timestamp] = fourWeekAve(scored[platid], timestamp)
        fromHashToRedis(rSMOOTH, result[platid][timestamp], 'platform_id', 'date')
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
    status, scored = getData()
    result[platid] = {}
    for timestamp in scored[platid]:
        #四周平均
        result[platid][timestamp] = fourWeekAve(scored[platid], timestamp)
        fromHashToRedis(rSMOOTH, result[platid][timestamp], 'platform_id', 'date')
        count += 1
else:
    usage()

print "Smooth data("+str(count)+") written to redis-db("+str(dbSMOOTH)+")!"
