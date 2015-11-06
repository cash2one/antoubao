#!/usr/bin/python
#encoding=utf-8

from header import *

def usage():
    print "COMMAND:"
    print "\tpython "+sys.argv[0]
    exit(-1)

#数据格式化
def normalize(d):
    for key in d.keys():
        if d[key] is None:
            d[key] = 0
    d['mobility_original'] = d['mobility']
    d['mobility'] = round(d['capital_adequacy_ratio']*0.3367+d['mobility_original']*0.6633, 1)
    d['reputation'] = round((d['pellucidity']+d['security'])/2, 1)
    for key in Integer:
        d[key] = int(d[key])
    for key in Decimal:
        d[key] = round(d[key], 1)
    for key in Decimal2:
        d[key] = round(d[key], 2)
    for key in Decimal3:
        d[key] = round(d[key], 3)
    if d['third_entrust'] == 0:
        d['third_entrust'] = '无第三方托管'
        d['third_entrust_num'] = 0
    else:
        d['third_entrust'] = '有第三方托管'
        d['third_entrust_num'] = 1
    if d['debt_transfer'] == 0:
        d['debt_transfer'] = '不支持'
        d['debt_transfer_num'] = 0
    else:
        d['debt_transfer'] = '支持'
        d['debt_transfer_num'] = 1
    if d['platform_name'] == u'前海理想金融':
        d['platform_name'] = u'前海理想'
    if d['platform_name'] == u'凤凰金融（江西）':
        d['platform_name'] = u'江西凤凰'
    if d['platform_name'] == u'汇盈金服(汇盈贷)':
        d['platform_name'] = u'汇盈金服'
    if d['weekly_loan_period'] is not None:
        d['weekly_loan_period'] = round(d['weekly_loan_period']/30, 2)
    if d['top10_ratio_loan'] is not None:
        d['top10_ratio_loan'] = round(d['top10_ratio_loan']*100, 1)
    if d['top5_ratio_investment'] is not None:
        d['top5_ratio_investment'] = round(d['top5_ratio_investment']*100, 1)
    if d['top10_ratio_investment'] is not None:
        d['top10_ratio_investment'] = round(d['top10_ratio_investment']*100, 1)
    if d['turnover_registered'] is not None:
        d['turnover_registered'] = round(d['turnover_registered']*100, 1)
    if d['money_growth'] is not None:
        d['money_growth'] = round((d['money_growth']-1)*100, 1)
    return d

def getData():
    #读取定量数据
    quanti = readQuanti(rQUANTI)
    #读取定性数据
    qualit = readQualit(rQUALIT)
    #读取总分
    scored = readRank(rRAKPUN)
    #读取状态
    status = readStatus(rSTATUS)
    return quanti, qualit, scored, status

#准备数据
quanti, qualit, scored, status = getData()
datas = [quanti, qualit, scored]
sGood = []
sBad = {}
sStat = {}
goodboy = {}
for platid in status.keys():
    for date in status[platid].keys():
        if platid not in goodboy.keys():
            goodboy[platid] = date
        elif date > goodboy[platid]:
            goodboy[platid] = date
            if platid in sGood:
                sGood.remove(platid)
            if platid in sStat:
                sStat.pop(platid)
            if platid in sBad:
                sBad.pop(platid)
        else:    
            continue        
        s = json.loads(status[platid][date])['status']
        if s > 1.99:
            sGood.append(platid)
        elif s < 0.89:
            sStat[platid] = s
            sBad[platid] = int(date)-((int(date)-1388851200)%(7*24*3600))-(7*24*3600)

dataTable = []
dataTable.append(["platform_id", "platform_name", "date", "turnover_period", "weekly_total_investor", "weekly_lending", "weekly_total_borrower", "ave_annualized_return", "weekly_loan_period", "turnover_registered", "top10_ratio_loan", "not_returned_yet", "money_growth", "cash_flow_in", "top5_ratio_investment", "top10_ratio_investment"])
dataTable.append(["website", "financing_status", "registered_cap", "established_date", "location", "debt_transfer", "cash_in_fee", "cash_out_fee", "management_fee", "advanced_repayment", "reserve_fund", "third_entrust", "listing", "state_owned", "bank", "third_assurance", "vc_cap_usd", "house_debt", "car_debt", "small_credit_bid", "big_credit_bid", "bill_debt"])
dataTable.append(["level", "score", "activeness_credibility", "growth", "distribution", "security", "capital_adequacy_ratio", "pellucidity", "mobility"])

Integer = ["weekly_total_investor", "weekly_lending", "weekly_total_borrower", "turnover_period"]
Decimal = ["ave_annualized_return", "weekly_loan_period", "activeness_credibility", "growth", "distribution", "security", "pellucidity", "mobility", "status"]
Decimal2 = ["not_returned_yet"]
Decimal3 = ["top10_ratio_loan", "top5_ratio_investment", "top10_ratio_investment", "turnover_registered", "money_growth"]

rRESULT.flushdb()

#数据标准化
result = {}
count = 0
for platid in scored.keys():
    if platid in BLACKLIST:
        continue
    for date in scored[platid].keys():
        d = {}
        result['platid'] = platid
        result['date'] = date
        for i in range(0, len(dataTable)):
            for key in dataTable[i]:
                if i == 1:
                    d[key] = datas[i][platid][key]
                else:
                    d[key] = datas[i][platid][date][key]
        d['status'] = 1
        result['value'] = normalize(d)
        count += 1
        fromHashToRedis(rRESULT, result, "platid", "date", "value")

#获取所有时间点列表
dates = []
for platid in rRESULT.keys():
    for date in rRESULT.hkeys(platid):
        if int(date) not in dates:
            dates.append(int(date))

#雷达图标准化
_dict = {}
d = {}
for date in dates:
    _dict['activeness_credibility'] = []
    _dict['distribution'] = []
    _dict['security'] = []
    _dict['mobility'] = []
    _dict['growth'] = []
    _dict['pellucidity'] = []
    _dict['reputation'] = []
    _dict['mobility_original'] = []
    _dict['capital_adequacy_ratio'] = []
    _dict['platform_id'] = []
    for platid in rRESULT.keys():
        if rRESULT.hexists(platid, date) == 0:
            continue
        d[platid] = json.loads(rRESULT.hget(platid, date))
        for key in _dict.keys():
            _dict[key].append(d[platid][key])
    dfh = score_transfer(_dict, 1.5)
    i = 0
    for platid in _dict['platform_id']:
        for key in _dict.keys():
            if key == 'platform_id':
                continue
            d[platid][key] = round(dfh[key][i], 1)
        rRESULT.hset(platid, date, json.dumps(d[platid]))
        i+=1

#黑白名单数据填充
for platid in rRESULT.keys():
    d = {}
    if platid in sGood:
        for date in sorted(dates):
            _date = date
            if rRESULT.hexists(platid, date) == 0:
                i = 1
                while True:
                    _date = _date-i*7*24*3600
                    if _date < min(dates):
                        break
                    data = rRESULT.hget(platid, _date)
                    if data is None:
                        #i+=1
                        continue
                    d = json.loads(data)
                    if 'old_date' in d.keys():
                        #i+=1
                        continue
                    d["date"] = date
                    d["old_date"] = _date
                    rRESULT.hset(platid, date, json.dumps(d))
                    count+=1
                    break
    elif platid in sBad:
        for date in sorted(dates):
            if date <= sBad[platid]:
                continue
            _date = sBad[platid]
            i = 1
            while rRESULT.hexists(platid, _date) == 0:
                _date = _date-i*7*24*3600
                if _date < STARTDATE:
                    break
            data = rRESULT.hget(platid, _date)
            if data is None:
                if rRESULT.hexists(platid, date) != 0:
                    data = rRESULT.hget(platid, date)
                    d = json.loads(data)
                    d["status"] = sStat[platid]
                    d["score"] -= 500
                    rRESULT.hset(platid, date, json.dumps(d))
            else:
                d = json.loads(data)
                d["date"] = date
                d["old_date"] = _date
                d["status"] = sStat[platid]
                d["score"] -= 500
                rRESULT.hset(platid, date, json.dumps(d))
            '''
            if rRESULT.hexists(platid, _date) == 0:
                i = 1
                while True:
                    _date = _date-i*7*24*3600
                    if _date < STARTDATE:
                        break
                    data = rRESULT.hget(platid, _date)
                    if data is None:
                        continue
                    d = json.loads(data)
                    if 'old_date' in d.keys():
                        continue
                    d["date"] = date
                    d["old_date"] = _date
                    d['status'] = sStat[platid]
                    #d['score'] -= 500
                    rRESULT.hset(platid, date, json.dumps(d))
                    break
            else:
                data = rRESULT.hget(platid, _date)
                d = json.loads(data)
                d['date'] = date
                d['old_date'] = _date
                d['status'] = sStat[platid]
                d['score'] -= 500
                rRESULT.hset(platid, date, json.dumps(d))
            '''
            count+=1

print "View data("+str(count)+") written to Redis-db("+str(dbRESULT)+")!"
