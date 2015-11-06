#!/usr/bin/python
#encoding=utf-8

from header import *

def usage():
    print "COMMAND:"
    print "\tpython "+sys.argv[0]+" [-all|-t|-f]"
    print "获取数据源的所有数据，如果是坏站，则拷贝出事前两周的数据。"
    print ""
    print "OPTIONS:"
    print "\t-all: 初始化所有定量数据"
    print "\t-t [timestamp]: 初始化指定周的定量数据"
    print "\t-f: 初始化定性数据"
    print "\t-y: 初始化平台状态数据"
    exit(-1)

def readQuantitative(d, s):
    #遍历定量表内容，依次写入Redis的db(0)和db(9)。
    count = 0
    badArr = []
    for jsonStr in s:
        sinfo = json.loads(json.dumps(jsonStr))
        if sinfo['status'] < 0.89:
            badArr.append(sinfo['platform_id'])
    for jsonStr in d:
        pinfo = json.loads(json.dumps(jsonStr))
        #关键数值为0，跳过
        if (pinfo['platform_id'] in badArr and pinfo['black'] == '#B5#') \
            or pinfo['black'] == '#P#' \
            or pinfo['black'] is None \
            or pinfo['black'] == '':
            del pinfo['black']
        else:
            continue
        ret = fromHashToRedis(rQUANTI, pinfo, 'platform_id', 'date')
        if ret == 0:
            print "Failure in writing out "+pinfo['platform_name']+"."
        else:
            count+=1
    return count

if len(sys.argv) < 2:
    usage()
elif sys.argv[1] == '-all':
    rQUANTI.flushdb()
    #读取定量表E1所有内容。
    d = fromMySQLToArray(DSCUR, "platform_quantitative_data_E1", " WHERE `date` >= "+str(STARTDATE)+" ORDER BY `date` ASC")
    if len(d) == 0:
        print "Failure in reading in platform_quantitative_data_E1."
        exit(-1)
    s = fromMySQLToArray(DSCUR, "total_status")
    count = readQuantitative(d, s)
    print "Quantitative data("+str(count)+") written to redis-db("+str(dbQUANTI)+")!"    
elif sys.argv[1] == '-t':
    #读取指定日期的表E1。
    if len(sys.argv) < 3:
        usage()
    else:
        timestamp = int(sys.argv[2])
        if timestamp < STARTDATE:
            print "Invalid date("+str(timestamp)+"), the must be equal or greater than "+str(STARTDATE)
            exit(-1)
    d = fromMySQLToArray(DSCUR, "platform_quantitative_data_E1", " WHERE `date` = '"+str(timestamp)+"'")
    if len(d) == 0:
        print "Failure in reading in platform_quantitative_data_E1."
        exit(-1)
    s = fromMySQLToArray(DSCUR, "total_status")
    count = readQuantitative(d, s)
    print "Quantitative data("+str(count)+") written to redis-db("+str(dbQUANTI)+")!"
elif sys.argv[1] == '-f':
    rQUALIT.flushdb()
    #读取定性表F
    d = fromMySQLToArray(DSCUR, "platform_qualitative_F")
    if len(d) == 0:
        print "Failure in reading in platform_qualitative_F."
        exit(-1)
    #遍历定性表内容，依次写入Redis的db(1)
    count = 0
    for v in d:
        if 'platform_name' not in v.keys():
            print "Invalid data."
            continue
        v['platform_id'] = str(hashlib.md5(v['platform_name']).hexdigest())[:10]
        ret = fromDictToRedis(rQUALIT, v['platform_id'], v)
        if ret == 0:
            print "Failure in writing out "+v['platform_name']+"."
        else:
            count+=1
    print "Qualitative data("+str(count)+") written to redis-db("+str(dbQUALIT)+")!"
elif sys.argv[1] == '-y':
    rSTATUS.flushdb()
    #读取平台状态表Y
    d = fromMySQLToArray(DSCUR, "total_status")
    if len(d) == 0:
        print "Failure in reading in total_status."
        exit(-1)
    #遍历状态表内容，依次写入Redis的db(3)
    count = 0
    for jsonStr in d:
        pinfo = json.loads(json.dumps(jsonStr))
        ret = fromHashToRedis(rSTATUS, pinfo, 'platform_id', 'date', 'status|summary')
        if ret == 0:
            print "Failure in writing out "+pinfo['platform_name']+"."
        else:
            count+=1
    print "Status data("+str(count)+") written to redis-db("+str(dbSTATUS)+")!"
else:
    usage()
