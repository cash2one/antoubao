#!/usr/bin/python
#encoding=utf-8

from header import *

def usage():
    print "COMMAND:"
    print "\tpython "+sys.argv[0]
    exit(-1)

dataDict = {}
for platid in rRESULT.keys():
    for date in rRESULT.hkeys(platid):
        if date not in dataDict.keys():
            dataDict[date] = {}
        d = json.loads(rRESULT.hget(platid, date))
        while True:
            if d['score'] in dataDict[date].keys():
                d['score'] -= 0.0001
            else:
                break
        dataDict[date][d['score']] = d

for date in dataDict.keys():
    level = 'A'
    _sum = {}
    standard = {}
    #级别修正
    for score in sorted(dataDict[date].keys()):
        if 'old_date' in dataDict[date][score] and \
            dataDict[date][score]['old_date'] is not None and \
            dataDict[date][score]['score'] > 0:
            dataDict[date][score]['level'] = level
        level = dataDict[date][score]['level']
    #计算雷达图六大维度平均值
        for key in ["activeness_credibility", "growth", "distribution", "security", "capital_adequacy_ratio", "pellucidity", "mobility", "reputation", "mobility_original"]:
            if key not in _sum.keys():
                _sum[key] = 0
            _sum[key] += dataDict[date][score][key]
    for key in _sum.keys():
        standard[key] = _sum[key]/len(dataDict[date])
        for score in sorted(dataDict[date].keys()):
            dataDict[date][score]['standard_'+key] = round(standard[key], 1)

def order(dataDict, orderTitl, orderRule):
    arr = []
    dic = {}
    for value in dataDict.values():
        value[orderTitl] = round(value[orderTitl], 4)
        if len(arr) == 0:
            arr.insert(0, value)
            continue
        flag = False
        for i in range(0, len(arr)):
            if orderRule == "SMALL" and value[orderTitl] < arr[i][orderTitl]:
                arr.insert(i, value)
                flag = True
                break
            if orderRule == "BIG" and value[orderTitl] > arr[i][orderTitl]*1.000001:
                arr.insert(i, value)
                flag = True
                break
        if flag == False:
            arr.append(value)
    for i in range(0, len(arr)):
        arr[i]['rank_'+orderTitl] = i+1
        dic[arr[i]['platform_id']] = arr[i]
    return dic

#排名
dateList = sorted(dataDict.keys())
orderTitl = ["score", "weekly_total_investor", "weekly_lending", "weekly_total_borrower", "ave_annualized_return", "weekly_loan_period", "turnover_registered", "top10_ratio_loan", "not_returned_yet", "money_growth"]
orderRule = ["BIG", "BIG", "BIG", "BIG", "BIG", "SMALL", "BIG", "SMALL", "BIG", "BIG"]
for date in dateList:
    for i in range(0, len(orderTitl)):
        dataDict[date] = order(dataDict[date], orderTitl[i], orderRule[i])

#变化，从第二周开始计算
for i in range(1, len(dateList)):
    for platid in dataDict[dateList[i]].keys():
        for key in orderTitl:
            if platid not in dataDict[dateList[i-1]].keys():
                dataDict[dateList[i]][platid]["var_"+key]=0
            else:
                dataDict[dateList[i]][platid]["var_"+key]=dataDict[dateList[i-1]][platid]["rank_"+key]-dataDict[dateList[i]][platid]["rank_"+key]

count = 1
for date in dataDict.keys():
    for platid in dataDict[date].keys():
        d = {}
        d['key'] = platid
        d['field'] = date
        d['value'] = dataDict[date][platid]
        count+=1
        fromHashToRedis(rRESULT, d, 'key', 'field', 'value')

print "View data("+str(count)+") written to Redis-db("+str(dbRESULT)+")!"
