#!/usr/bin/python
#encoding=utf-8

from header import *

def usage():
    print "COMMAND:"
    print "\tpython "+sys.argv[0]
    exit(-1)

dataDict = {}
for platid in sorted(rRESULT.keys()):
    for date in sorted(rRESULT.hkeys(platid)):
        if date not in dataDict.keys():
            dataDict[date] = {}
        d = json.loads(rRESULT.hget(platid, date))
        while True:
            if d['score'] in dataDict[date].keys():
                if LEVEL_LIST.index(d['level']) < LEVEL_LIST.index(dataDict[date][d['score']]['level']):
                    d_temp = dataDict[date][d['score']]
                    dataDict[date][d['score']] = d
                    d = d_temp
                d['score'] -= 0.0001
            else:
                break
        dataDict[date][d['score']] = d

#谢博
#将因为白名单补充历史数据的站的相应分值予以调整(级别保持不变)
adjust_list = ["score", "activeness_credibility", "growth", "distribution", "security", "capital_adequacy_ratio", "pellucidity", "mobility", "reputation", "mobility_original"]
distribution_dict = {}
number_dict = {}
for date in sorted(dataDict.keys()):
    #获得每个时间内各个维度的分布
    distribution_dict[date] = {}
    for key in adjust_list:
        distribution_dict[date][key] = {}
        for level in LEVEL_LIST:
            distribution_dict[date][key][level] = []
    #白名单和普通名单
    white_score_list = []
    normal_score_list = []
    for score in sorted(dataDict[date].keys()):
        if 'old_date' in dataDict[date][score]:
            if dataDict[date][score]['old_date'] is not None and dataDict[date][score]['score'] > 0:
                white_score_list.append(score)
        else:
                normal_score_list.append(score)
    #用普通名单来计算各个历史周中key的分值分布(从小到大排列)
    for score in normal_score_list:
        for key in adjust_list:
            level = dataDict[date][score]['level']
            if key == "score" and dataDict[date][score][key] < 0:
                continue
            distribution_dict[date][key][level].append(dataDict[date][score][key])
    number_dict[date] = {}
    for key in adjust_list:
        number_dict[date][key] = {}
        for level in LEVEL_LIST:
            distribution_dict[date][key][level].sort()
            number_dict[date][key][level] = len(distribution_dict[date][key][level])
                 
    #白名单在历史周的相应级别的百分比
    relative_position_dict = {}
    for score in white_score_list:
        relative_position_dict[score] = {}
        level = dataDict[date][score]['level']
        old_date = str(dataDict[date][score]['old_date'])
        for key in adjust_list:
            relative_position_dict[score][key] = distribution_dict[old_date][key][level].index(dataDict[old_date][score][key]) + 1
            relative_position_dict[score][key] /= float(number_dict[old_date][key][level])
     
    #计算白名单在本周各个key的分数
    for score in white_score_list:
        level = dataDict[date][score]['level']
        for key in adjust_list:
            ratio_list = [float(i + 1) / number_dict[date][key][level] for i in range(number_dict[date][key][level])]
            if relative_position_dict[score][key] < ratio_list[0]:
                dataDict[date][score][key] = 2 * distribution_dict[date][key][level][0] - distribution_dict[date][key][level][1]
            else:
                for i in range(1, number_dict[date][key][level]):
                    if ratio_list[i - 1] <= relative_position_dict[score][key] <= ratio_list[i]:
                        dataDict[date][score][key] = (distribution_dict[date][key][level][i - 1] + distribution_dict[date][key][level][i]) / 2

#李云翔
for date in sorted(dataDict.keys()):
    _sum = {}
    standard = {}
    #级别修正
#     level = 'A'
    for score in sorted(dataDict[date].keys()):
        #级别修正
#         if 'old_date' in dataDict[date][score] and \
#             dataDict[date][score]['old_date'] is not None and \
#             dataDict[date][score]['score'] > 0:
#             dataDict[date][score]['level'] = level
#         level = dataDict[date][score]['level']
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
