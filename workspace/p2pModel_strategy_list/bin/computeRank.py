#!/usr/bin/python
#encoding=utf-8

from header import *

def usage():
    print "COMMAND:"
    print "\tpython "+sys.argv[0]+" [-all|-t|-p]"
    print ""
    print "OPTIONS:"
    print "\t-all: 执行所有周的评级策略"
    print "\t-t [timestamp]: 执行指定周的评级策略"
    print "\t-p [platform_id]: 计算指定平台的评级策略"
    exit(-1)

def getData():
    #读取定量数据
    quanti = readQuanti(rQUANTI)
    
    #读取总分
    scored, scoreRange = readScored(rSMOOTH)
    
    #读取状态
    status = readStatus(rSTATUS)
    
    return quanti, status, scored, scoreRange

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
    for k,v in scoreDict.items():
        _score[v] = k
    return scored, _score

def rankPunish(quanti, timestamp, scored, scoreDict, scoreArr, maxScore, minScore, status, _degrade_dict):
    if scored['level'] == 'C':
        if 'downgrading_info' not in scored.keys():
            scored['downgrading_info'] = ""
        if 'none_downgrading_info' not in scored.keys():
            scored['none_downgrading_info'] = ""
        return scored
    if 'downgrading_info' not in scored.keys():
        scored['downgrading_info'] = ""
    if 'none_downgrading_info' not in scored.keys():
        scored['none_downgrading_info'] = ""
    quanti4WeekAve = fourWeekAve(quanti, timestamp, INVALID_TITLE)
    field_list_ave = ["not_returned_yet"]
    #新的降级策略写法 @谢博
    for level in LEVEL_LIST:
        info = ""
        info_temp = ""
        if level not in _degrade_dict:
            continue
        if scored['score'] < scoreDict[level]:
            continue
        for field in _degrade_dict[level]:
            if field == "status":
                if status < float(_degrade_dict[level]["status"]["threshold"]) and scored['score'] > scoreDict[level]:
                    info += "#" + level + ": " + _degrade_dict[level]["status"]["info"] + "#"
            else:
                if field in field_list_ave:
                    value = quanti4WeekAve[field] - float(_degrade_dict[level][field]["threshold"])
                    value_temp = quanti[timestamp][field] - float(_degrade_dict[level][field]["threshold"])
                else:    
                    value = quanti[timestamp][field] - float(_degrade_dict[level][field]["threshold"])
                if _degrade_dict[level][field]["symbol"] == "GT":
                    if value > 0 :
                        info += "#" + level + ": " + _degrade_dict[level][field]["info"] + "#"
                    if field in field_list_ave and value_temp > 0:
                        info_temp += "#" + level + ": " + _degrade_dict[level][field]["info"] + "#"
                else:
                    if value < 0 :
                        info += "#" + level + ": " + _degrade_dict[level][field]["info"] + "#"
                    if field in field_list_ave and value_temp < 0:
                        info_temp += "#" + level + ": " + _degrade_dict[level][field]["info"] + "#"
    
#         #旧的降级策略写法 @李云祥
#         if status < 0.89 and scored['score'] > scoreDict['A']:
#             info += "#BADPLAT#"
#         if quanti4WeekAve['not_returned_yet'] < 1 and scored['score'] > scoreDict['A+']:
#             info += "#YET#"
#         if (quanti[timestamp]['top10_ratio_loan'] > 0.25 and scored['score'] > scoreDict['A++']) \
#             or (quanti[timestamp]['top10_ratio_loan'] > 0.35 and scored['score'] > scoreDict['A+']) \
#             or (quanti[timestamp]['top10_ratio_loan'] > 0.55 and scored['score'] > scoreDict['A']):
#             info += "#TOP10#"
#         if (quanti[timestamp]['ave_annualized_return'] > 15.5 and scored['score'] > scoreDict['A++']) \
#             or (quanti[timestamp]['ave_annualized_return'] > 15.99 and scored['score'] > scoreDict['A+']) \
#             or (quanti[timestamp]['ave_annualized_return'] > 16.99 and scored['score'] > scoreDict['A']) \
#             or (quanti[timestamp]['ave_annualized_return'] > 18.99 and scored['score'] > scoreDict['B++']):
#             info += "#AVE#"
#         if (quanti[timestamp]['weekly_total_borrower'] < 50 and scored['score'] > scoreDict['A++']) \
#             or (quanti[timestamp]['weekly_total_borrower'] < 20 and scored['score'] > scoreDict['A+']) \
#             or (quanti[timestamp]['weekly_total_borrower'] < 5 and scored['score'] > scoreDict['A']):
#             info += "#BORROWER#"
#         if (quanti[timestamp]['weekly_lending'] < 500 and scored['score'] > scoreDict['A+']) \
#             or (quanti[timestamp]['weekly_lending'] < 300 and scored['score'] > scoreDict['A']):
#             info += "#LENDING#"
        
        if info == "":
            if info_temp == "":
                break
            else:
                scored['none_downgrading_info'] += info_temp
                continue
        scored['downgrading_info'] += info
        scored['none_downgrading_info'] += info_temp

        for key in scoreArr.keys():
            if key != "score":
                continue
            pos = 0
            #查找当前分数对应的级别
            while pos < len(scoreArr[key]) and scored[key] < scoreArr[key][pos]:
                pos+=1
            if pos == len(scoreArr[key]):
                continue
            if pos == 0:
                score1 = maxScore[key]
            else:
                score1 = scoreArr[key][pos-1]
            if pos == len(scoreArr[key])-1:
                score2 = scoreArr[key][pos]
                score3 = minScore[key]
            else:
                score2 = scoreArr[key][pos]
                score3 = scoreArr[key][pos+1]
            if score1 == score2:
                continue
            if scored[key] == score1:
                scored[key] = score2 - 0.0001
            else:
                scored[key] = ((scored[key]-score2)/(score1-score2))**(0.5)*(score2-score3)+score3
            if key == 'score':
                scored['level'] = LEVEL_LIST[pos+1]
    return scored

def limit(values):
    maxData = {}
    minData = {}
    arr = {}
    scoreArr = {}
    for platid in values.keys():
        for timestamp in values[platid].keys():
            if timestamp not in arr.keys():
                arr[timestamp] = {}
            for key in ["activeness_credibility", "growth", "distribution", "security", "capital_adequacy_ratio", "pellucidity", "score"]:
                if key not in arr[timestamp].keys():
                    arr[timestamp][key] = []
                arr[timestamp][key].append(values[platid][timestamp][key])
    for timestamp in arr.keys():
        if timestamp not in maxData.keys():
            maxData[timestamp] = {}
        if timestamp not in minData.keys():
            minData[timestamp] = {}
        if timestamp not in scoreArr.keys():
            scoreArr[timestamp] = {}
        for key in arr[timestamp].keys():
            tmp = sorted(arr[timestamp][key], reverse=True)
            maxData[timestamp][key] = tmp[0]
            minData[timestamp][key] = tmp[-1]
            scoreArr[timestamp][key] = []
#             LEVEL_PERCENTAGE_DICT_temp = {"A++":98, "A+":81.3, "A":52, "B++":51, "B+":20.1987, "B":5.9}
            for level in LEVEL_LIST[:-1]:
                scoreArr[timestamp][key].append(np.percentile(tmp, LEVEL_PERCENTAGE_DICT[level]))
#                 scoreArr[timestamp][key].append(np.percentile(tmp, LEVEL_PERCENTAGE_DICT_temp[level]))
    return maxData, minData, scoreArr

#谢博，通过降级策略字符串获得最低等级的降级
def getLowestDegrade(_str):
    if _str == None or len(_str) == 0:
        return None
    degrade_list = _str.split("##")
    if len(degrade_list) == 0:
        return None
    degrade_set = set()
    for degrade_info in degrade_list:
        degrade_set.add(degrade_info.split(": ")[0].replace("#", ""))
    lowest_grade_index = 0
    for degrade in degrade_set:
        index_number = LEVEL_LIST.index(degrade)
        if index_number > lowest_grade_index:
            lowest_grade_index = index_number
    return lowest_grade_index
    
result = {}
scoreDict = {}
count = 0
degrade_dict = getDegradeDict()

if len(sys.argv) < 2:
    usage()
elif sys.argv[1] == '-all':
    #准备数据
    rRAKPUN.flushdb()
    quanti, status, scored, scoreRange = getData()
    maxData, minData, scoreArr = limit(scored)
    timestamp_set = set()
    field_set = set()
    for platid in scored.keys():
        if platid not in result.keys():
            result[platid] = {}
        #为了使得当周的坏站也会被降级策略命中，在这里用最新的status，而不是历史的时时status。否则会在历史上坏站为A（因为历史是坏站的前两周，这个时候status还没有小于0.89），补充历史数据时也依旧为A
        if platid not in status.keys():
            status_temp = 1
        else:
#             date_list = [int(x) for x in status[platid].keys() if int(x) < int(timestamp)]
            date_list = [int(x) for x in status[platid].keys()]
            if len(date_list) == 0:
                status_temp = 1
            else:
                newest_bad_date = str(max(date_list))
                status_temp = json.loads(status[platid][newest_bad_date])["status"]
        for timestamp in sorted(scored[platid]):
            timestamp_set.add(timestamp)
            #评级
            scoreSort = sorted(scoreRange[timestamp].keys(), reverse=True)
            result[platid][timestamp], scoreDict[timestamp] = rank(scored[platid][timestamp], scoreSort)
            field_set.update(scoreArr[timestamp])
            result[platid][timestamp]["score_after_smooth"] = scored[platid][timestamp]["score"]
            result[platid][timestamp]["level_after_smooth"] = result[platid][timestamp]["level"]
            #降级惩罚
            result[platid][timestamp] = rankPunish(quanti[platid], timestamp, result[platid][timestamp], scoreDict[timestamp], scoreArr[timestamp], maxData[timestamp], minData[timestamp], status_temp, degrade_dict)
            result[platid][timestamp]["level_after_degrade"] = result[platid][timestamp]["level"]
            result[platid][timestamp]["score_after_degrade"] = result[platid][timestamp]["score"]
#             fromHashToRedis(rRAKPUN, result[platid][timestamp], 'platform_id', 'date')

    #@谢博，增加降级后的四周平滑策略
    #获得每一周各个级别的最大分数
    score_level_dict = {}
    for timestamp in timestamp_set:
        score_level_dict[timestamp] = {}
        for field in field_set:
            score_level_dict[timestamp][field] = {}
            for level in LEVEL_LIST:
                score_level_dict[timestamp][field][level] = []
    for platid in result.keys():
        for timestamp in sorted(result[platid]):
            level = result[platid][timestamp]["level"]
            for field in field_set:
                score_level_dict[timestamp][field][level].append(result[platid][timestamp][field])
    for timestamp in score_level_dict:
        for field in score_level_dict[timestamp]:
            for level in score_level_dict[timestamp][field]:
                #注意这里维度分实际上并不一定按照级别排列，即A的站某一维度的分可能在该维度的level中并不是A
                score_level_dict[timestamp][field][level] = max(score_level_dict[timestamp][field][level])
    #平滑
    smooth_dict = {1:0.25, 2:0.5, 3:0.6, 4:0.75}
    for platid in result.keys():
#         if platid != "b3a878b9b9":
#             continue
        timestamp_list = sorted(result[platid])
        lowest_grade_list = []
        for timestamp in timestamp_list:
            if "downgrading_info" in result[platid][timestamp]:
                lowest_grade_list.append(getLowestDegrade(result[platid][timestamp]["downgrading_info"]))
            else:
                lowest_grade_list.append(None)
        timestamp_list_number = len(timestamp_list)
        for i in range(timestamp_list_number):
            timestamp = timestamp_list[i]
            result[platid][timestamp]["degrade_smooth_info"] = ""
            lowest_grade_this = LEVEL_LIST.index(result[platid][timestamp]["level"])
            for j in range(max(i - 4, 0), i)[::-1]:
                lowest_grade_last = lowest_grade_list[j]
                if lowest_grade_last != None and lowest_grade_this <= lowest_grade_last:
                    this_week_ratio = smooth_dict[i - j]
                    last_week_level = LEVEL_LIST[lowest_grade_last + 1]
                    for field in field_set:
                        if field == "score":
                            result[platid][timestamp]["degrade_smooth_info"] = "-" + str(i-j) + "#" + last_week_level + "#" +  str(this_week_ratio) + " * " + "%.4f" % result[platid][timestamp]["score"] + " + " + str(1 - this_week_ratio) + " * " + "%.4f" % score_level_dict[timestamp]["score"][last_week_level]
                            assert result[platid][timestamp]["score"] > score_level_dict[timestamp]["score"][last_week_level]
                        result[platid][timestamp][field] = this_week_ratio * result[platid][timestamp][field] + (1 - this_week_ratio) * score_level_dict[timestamp][field][last_week_level]
                    break
    #根据得分排名重新计算等级。
    for timestamp in timestamp_set:
        platid_score_level_list = []
        for platid in result.keys():
            if timestamp in result[platid]:
                platid_score_level_list.append((platid, result[platid][timestamp]["score"], result[platid][timestamp]["level"]))
        platid_score_level_list.sort(key=lambda x:-x[1])
        platid_score_level_list = [list(x) for x in platid_score_level_list]
        num = len(platid_score_level_list)
        for i in range(1, num):
            if LEVEL_LIST.index(platid_score_level_list[i][2]) < LEVEL_LIST.index(platid_score_level_list[i-1][2]):
                platid_score_level_list[i][2] = platid_score_level_list[i-1][2]
                result[platid_score_level_list[i][0]][timestamp]["level"] = result[platid_score_level_list[i-1][0]][timestamp]["level"]
    
    for platid in result.keys():
        for timestamp in sorted(result[platid]):
            count += 1
            fromHashToRedis(rRAKPUN, result[platid][timestamp], 'platform_id', 'date')
            
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
    quanti, status, scored, scoreRange = getData()
    for platid in scored.keys():
        if platid not in result.keys():
            result[platid] = {}
        if platid not in status.keys():
            status[platid] = 1
        #评级
        scoreSort = sorted(scoreRange[timestamp].keys(), reverse=True)
        result[platid][timestamp], scoreDict[timestamp] = rank(scored[platid][timestamp], scoreSort)
        #降级惩罚
        result[platid][timestamp] = rankPunish(quanti[platid], timestamp, result[platid][timestamp], scoreDict[timestamp], scoreSort[0], scoreSort[-1], degrade_dict)
        fromHashToRedis(rRAKPUN, result[platid][timestamp], 'platform_id', 'date')
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
    quanti, status, scored, scoreRange = getData()
    result[platid] = {}
    status[platid] = 1
    for timestamp in scored[platid]:
        #评级
        scoreSort = sorted(scoreRange[timestamp].keys(), reverse=True)
        result[platid][timestamp], scoreDict[timestamp] = rank(scored[platid][timestamp], scoreSort)
        #降级惩罚
        result[platid][timestamp] = rankPunish(quanti[platid], timestamp, result[platid][timestamp], scoreDict[timestamp], scoreSort[0], scoreSort[-1], degrade_dict)
        fromHashToRedis(rRAKPUN, result[platid][timestamp], 'platform_id', 'date')
        count += 1
else:
    usage()

print "Rank data("+str(count)+") written to redis-db("+str(dbRAKPUN)+")!"