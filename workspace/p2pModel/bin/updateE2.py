#!/usr/bin/python
#encoding=utf-8

from header import *

def usage():
    print "COMMAND:"
    print "\tpython "+sys.argv[0]
    exit(-1)

def getData():
    #读取定量数据
    quanti = readQuanti(rQUANTI)
    #读取状态
    status = readStatus(rSTATUS)
    return quanti, status

#获取所有时间点列表
dates = []
for platid in rQUANTI.keys():
    for date in rRESULT.hkeys(platid):
        if int(date) not in dates:
            dates.append(int(date))
this_date = max(dates)

#准备数据
quanti, status = getData()
sGood = []
for platid in status.keys():
    if this_date in status[platid].keys():
        s = json.loads(status[platid][this_date])['status']
        if s > 1.99:
            sGood.append(platid)
print len(sGood)

#白名单数据填充
count = 0
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

print "View data("+str(count)+") written to Redis-db("+str(dbRESULT)+")!"
