#!/usr/bin/python
#encoding=utf-8

from header import *

def usage():
    print "COMMAND:"
    print "计算坏站报告所属数据"
    print "\tpython "+sys.argv[0]
    exit(-1)

count = 0

#准备数据
quanti, status, statis = readQuanti(rQUANTI), readStatus(rSTATUS), readStatis(rSTATIS)
rREPORT.flushdb()

#读取所有平台的状态值
dStatus = {}
for platid in status.keys():
    for date in status[platid].keys():
        num = json.loads(status[platid][date])['status']
        date = (int(date)-1388851200)%(7*24*3600) == 0 and int(date) or int(date)-(int(date)-1388851200)%(7*24*3600)+(7*24*3600)
        if platid not in dStatus.keys():
            dStatus[platid] = {}
        dStatus[platid][date] = str(num)

#读取相关属性关联配置
strategyB = {}
stringSQL = "SELECT `prop`, `prop_map`, `range` FROM view_strategyB_configure"
DEVCUR.execute(stringSQL)
for prop, prop_map, _range in DEVCUR.fetchall():
    if prop not in strategyB:
        strategyB[prop] = {}
    strategyB[prop][prop_map] = _range

#获取E2表结构
arrKeys = []
stringSQL = "SHOW FULL COLUMNS FROM E2_quantitative_data"
DEVCUR.execute(stringSQL)
for col in DEVCUR.fetchall():
    if col[0] == "id" or col[0] == "source":
        continue
    arrKeys.append(col[0])

#清理E2_report数据表
DEVCUR.execute("DELETE FROM E2_quantitative_data_report")
DEVCONN.commit()

platids = []
platids_level_dict = {}
stringSQL = "SELECT platform_id, level FROM view_mobile ORDER BY `score` DESC"
DEVCUR.execute(stringSQL)
for platform_id, level in DEVCUR.fetchall():
    platids.append(platform_id)
    platids_level_dict[platform_id] = level
dates = set()

#遍历View_mobile表中所有平台
stringSQL = "SELECT MAX(`date`) FROM view_mobile"
DEVCUR.execute(stringSQL)
this_date = int(DEVCUR.fetchone()[0])
for platid in platids:
    #@谢博，坏站锁定策略
    stringSQL = "SELECT `date`, `status`, `level` FROM total_status WHERE `platform_id` = '" + platid + "' AND `date` < '" + str(this_date) + "' ORDER BY `date` DESC LIMIT 1"
    _count = DSCUR.execute(stringSQL)
    if _count != 0:
        _date, status, level = DSCUR.fetchone()
        #坏站级别锁定
        if level != None and status < 0.89:
            stringSQL = "UPDATE view_mobile SET `level` = '" + level + "' WHERE `platform_id` = '"+platid+"'"
            DEVCUR.execute(stringSQL)
        #补充坏站级别，方便以后锁定
        if level == None and status < 0.89:
            stringSQL = "UPDATE total_status SET `level` = '" + platids_level_dict[platid] + "' WHERE `platform_id` = '"+platid+"' AND `date` = '" + str(_date) + "'"
            DSCUR.execute(stringSQL)
            DSCONN.commit()
    if platid not in dStatus:
        #该平台不是坏站，则不作处理
        continue
    #更新view_mobile表中坏站的status
    maxDate = max(dStatus[platid].keys())
    status = float(dStatus[platid][maxDate])
    #兼容iOS旧版本，去掉status大于1的数值
    if status > 1:
        status = 1
    stringSQL = "UPDATE view_mobile SET `status` = '"+str(round(status, 1))+"' WHERE `platform_id` = '"+platid+"'"
    DEVCUR.execute(stringSQL)
    DEVCONN.commit()
    if status > 0.89:
        continue
    for date in dStatus[platid]:
        if float(dStatus[platid][date]) > 0.89:
            continue
        date = date-2*7*24*3600
        #计算该平台出事两周前存在有效数据的日期
        found = False
        for d in sorted(quanti[platid].keys(), reverse=True):
            if date >= int(d):
                date = d
                found = True
                break
        if found == False:
            continue
        #获取坏站出事前一周（含）之前的所有数值
        stringSQL = "SELECT `"+"`,`".join(arrKeys)+"` FROM E2_quantitative_data WHERE `platform_id` = '"+str(platid)+"' AND `date` <= '"+str(int(date)+7*24*3600)+"'"
        DEVCUR.execute(stringSQL)
        result = DEVCUR.fetchall()
        for _list in result:
            stringSQL = "INSERT INTO E2_quantitative_data_report(`"+"`,`".join(arrKeys)+"`) VALUES('"+"','".join([str(s) for s in _list])+"')"
            DEVCUR.execute(stringSQL)
            count += 1
        #计算坏站出事前两周的相关属性数值
        stringSQL = "INSERT INTO E2_quantitative_data_report(`platform_id`, `platform_name`, `date`) VALUES('"+platid+"B', '相关属性平均', '"+str(date)+"')"
        DEVCUR.execute(stringSQL)
        count += 1
        DEVCONN.commit()
        for prop in strategyB:
            prop_map = strategyB[prop].keys()[0]
            value = quanti[platid][date][prop_map]
            range1 = value+value*strategyB[prop][prop_map]
            range2 = value-value*strategyB[prop][prop_map]
            stringSQL = "SELECT platform_id FROM E2_quantitative_data WHERE `"+prop_map+"` > '"+str(range2)+"' AND `"+prop_map+"` < '"+str(range1)+"' AND `date` = '"+str(date)+"'"
            DEVCUR.execute(stringSQL)
            where = ""
            for platform_id in DEVCUR.fetchall():
                where += "`platform_id` = '"+platform_id[0]+"' OR "
            if where == "":
                continue
            stringSQL = "SELECT avg("+prop+") FROM E2_quantitative_data WHERE ("+where[:-4]+") AND `date` = '"+str(date)+"'"
            ret = DEVCUR.execute(stringSQL)
            stringSQL = "UPDATE E2_quantitative_data_report SET `"+prop+"` = '"+str(DEVCUR.fetchone()[0])+"' WHERE `platform_id` = '"+platid+"B' AND `date` = '"+str(date)+"'"
            DEVCUR.execute(stringSQL)
        DEVCONN.commit()
        dates.add(date)

#删除干扰项
for key in INVALID_TITLE:
    if key in arrKeys:
        arrKeys.remove(key)

#需要计算前十平均和行业平均的日期
for date in dates:
    #计算去除3SIG后的行业平均值
    value = []
    for key in arrKeys:
        if key+"_h" not in statis[date]['3SIG']:
            stringSQL = "SELECT avg("+key+") FROM E2_quantitative_data WHERE `date` = '"+str(date)+"'"
        else:
            stringSQL = "SELECT avg("+key+") FROM E2_quantitative_data WHERE `"+key+"` < "+str(statis[date]['3SIG'][key+"_h"])+" AND `"+key+"` > "+str(statis[date]['3SIG'][key+"_l"])+" AND `date` = '"+str(date)+"'"
        DEVCUR.execute(stringSQL)
        v = DEVCUR.fetchone()[0]
        if v is None:
            value.append('')
        else:
            value.append(v)
    stringSQL = "INSERT INTO E2_quantitative_data_report(`platform_id`, `platform_name`, `date`, `"+"`,`".join(arrKeys)+"`) VALUES('strategyC', '行业平均', '"+str(date)+"', '"+"','".join([str(s) for s in value])+"')"
    DEVCUR.execute(stringSQL)
    count += 1

    #计算去除3SIG和非法值后的TOP10平台平均值
    stringSQL = "SELECT platform_id FROM T_rank WHERE `date` = '"+str(date)+"' ORDER BY `score` DESC"
    DEVCUR.execute(stringSQL)
    platids = DEVCUR.fetchall()
    value = []
    for key in arrKeys:
        sumValue = 0
        c = 0
        for platid in platids:
            platid = platid[0]
            stringSQL = "SELECT "+key+", weekly_ave_lending_per_borrower, weekly_ave_lending_per_bid FROM E2_quantitative_data WHERE `date` = '"+str(date)+"' AND `platform_id` = '"+platid+"'"
            DEVCUR.execute(stringSQL)
            v, per_borrower, per_bid = DEVCUR.fetchone()
            if value is None or \
                (key+"_h" in statis[date]['3SIG'] and (
                v > statis[date]['3SIG'][key+'_h'] or \
                v < statis[date]['3SIG'][key+'_l'])):
                continue
            if (key == 'weekly_ave_lending_per_borrower' or key == 'weekly_ave_lending_per_bid') and \
                (per_borrower*10000 < per_bid*0.9):
                continue
            sumValue += v
            c += 1
            if c == 10:
                break
        if c == 0:
            value.append(0)
        else:
            value.append(sumValue/c)
    stringSQL = "INSERT INTO E2_quantitative_data_report(`platform_id`, `platform_name`, `date`, `"+"`,`".join(arrKeys)+"`) VALUES('strategyA', '前十平均', '"+str(date)+"', '"+"','".join([str(s) for s in value])+"')"
    DEVCUR.execute(stringSQL)
    count += 1
DEVCONN.commit()

print "Bad-platform data("+str(count)+") written to MySQL-db(view_mobile&E2_BAD)!"
