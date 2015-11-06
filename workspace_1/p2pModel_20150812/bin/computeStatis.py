#!/usr/bin/python
#encoding=utf-8

from header import *

def usage():
    print "COMMAND:"
    print "\tpython "+sys.argv[0]+" [-all|-t]"
    print ""
    print "OPTIONS:"
    print "\t-all: 计算所有周的统计数据"
    print "\t-t [timestamp]: 计算指定周的统计数据"
    exit(-1)

def getMax(valueDict):
    tmpDict = {}
    for key in valueDict.keys():
        tmpDict[key] = np.max(valueDict[key])
    return json.dumps(tmpDict)

def getMin(valueDict):
    tmpDict = {}
    for key in valueDict.keys():
        tmpDict[key] = np.min(valueDict[key])
    return json.dumps(tmpDict)

def getAve(valueDict, sigma):
    tmpDict = {}
    for key in valueDict.keys():
        for value in valueDict[key]:
            if value < sigma[key+'_l'] or value > sigma[key+'_h']:
                valueDict[key].remove(value)
        tmpDict[key] = np.mean(valueDict[key])
    return json.dumps(tmpDict)

def getVar(valueDict, sigma):
    tmpDict = {}
    for key in valueDict.keys():
        for value in valueDict[key]:
            if value < sigma[key+'_l'] or value > sigma[key+'_h']:
                valueDict[key].remove(value)
        tmpDict[key] = np.var(valueDict[key])
    return json.dumps(tmpDict)

def getSigma(valueDict, limit):
    tmpDict = {}
    for key in valueDict.keys():
        minValue = ""
        length = int(len(valueDict[key])*limit)
        i = 0
        valueDict[key].sort()
        while True:
            if length+i >= len(valueDict[key]):
                break
            value = np.var(valueDict[key][i:length+i])
            if minValue == "" or value < minValue:
                minValue = value
                tmpDict[key+"_l"] = valueDict[key][i]
                tmpDict[key+"_h"] = valueDict[key][length+i]
            i+=1
    return json.dumps(tmpDict)

_1SIGMA = 0.6827
_2SIGMA = 0.9545
_3SIGMA = 0.98125

def getStatis(valueDict, t, sigma=""):
    if t == "MAX":
        return getMax(valueDict)
    elif t == "MIN":
        return getMin(valueDict)
    elif t == "AVE":
        return getAve(valueDict, sigma)
    elif t == "VAR":
        return getVar(valueDict, sigma)
    elif t == "1SIG":
        return getSigma(valueDict, _1SIGMA)
    elif t == "2SIG":
        return getSigma(valueDict, _2SIGMA)
    elif t == "3SIG":
        return getSigma(valueDict, _3SIGMA)
    else:
        return None

def writeStatistics(pinfos, QUALIT_TITLE):
    c = 0
    d = {}
    valueDict = {}
    #遍历所有平台数据
    for pinfo in pinfos:
        if pinfo is None:
            continue
        pinfoDict = json.loads(pinfo)
        d['date'] = pinfoDict['date']
        platId = pinfoDict['platform_id']
        #四周成交量小于770的站去除
        s = 0
        i = 0
        for t in range(0, (d['date']-STARTDATE)/(7*24*3600)):
            jsonStr = rQUANTI.hget(platId, d['date']-(t*7*24*3600))
            if jsonStr is None:
                continue
            info = json.loads(jsonStr)
            if info['weekly_lending'] == 0 or info['weekly_lending'] is None:
                continue
            s += float(info['weekly_lending'])
            i += 1
            if i >= 4:
                break
        if s < 770:
            continue
        #按照字段类型，填充valueArr，内部保存所有需要参与计算的数值集合。
        for k,v in pinfoDict.items():
            if k in INVALID_TITLE or v is None or v == "" or v == 0:
                continue
            if k not in valueDict:
                valueDict[k] = []
            valueDict[k].append(v)
    #对没有内容的字段进行补齐
    for k in pinfoDict.keys():
        if k not in INVALID_TITLE and k not in valueDict.keys():
            valueDict[k] = [0]*100
    #去掉定性数据
    for key in QUALIT_TITLE: 
        if key in valueDict.keys():
            del valueDict[key]
    #数值集合传给getStatis，计算出实际值
    sigma = ""
    for t in sorted(TYPES.keys()):
        d['type'] = t
        value = getStatis(valueDict, t, sigma)
        if value is None:
            continue
        d['value'] = json.loads(value)
        if d['value'] == '{}':
            continue
        if t == "2SIG":
            sigma = d['value']
        fromHashToRedis(rSTATIS, d, 'type', 'date', 'value')
        c += 1
    return c

count = 0

if len(sys.argv) < 2:
    usage()
elif sys.argv[1] == '-all':
    rSTATIS.flushdb()
    pinfoDict = {}
    #循环便利所有平台，按照时间维度存入pinfoDict
    for platId in rQUANTI.keys(): #平台
        for field in rQUANTI.hkeys(platId): #时间
            if field not in pinfoDict:
                pinfoDict[field] = []
            pinfoDict[field].append(rQUANTI.hget(platId, field)) #包含了每个时间的，所有平台的全部属性
    #遍历pinfoDict，将每个日期的平台的数据传给writeStatistics
    for date in pinfoDict.keys():
        if date < SCOREDATE:
            continue
        count += writeStatistics(pinfoDict[date], QUALIT_TITLE)
elif sys.argv[1] == '-t':
    #-t 参数合法性检查
    if len(sys.argv) < 3:
        usage()
    else:
        timestamp = int(sys.argv[2])
        if timestamp < SCOREDATE:
            print "Invalid date("+str(timestamp)+"), the must be equal or greater than "+str(SCOREDATE)
            exit(-1)
    pinfoArr = []
    #循环遍历所有平台
    for platId in rQUANTI.keys():
        #获取指定时间的该平台数据
        pinfoArr.append(rQUANTI.hget(platId, timestamp))
    #当前时间下所有平台的数据传给writeStatistics
    count += writeStatistics(pinfoArr, QUALIT_TITLE)
else:
    usage()

print "Statistics data("+str(count)+") written to redis-db("+str(dbSTATIS)+")!"
