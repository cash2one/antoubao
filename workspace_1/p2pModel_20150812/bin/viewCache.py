#!/use/bin/python
#coding=utf-8

from header import *

DSTDB = "view_cache"

DEVCUR.execute("TRUNCATE "+DSTDB)
DEVCONN.commit()

stringSQL = "SELECT DISTINCT platform_id, platform_name FROM `E2_quantitative_data_report` WHERE `platform_name` = '属性相似平均'"
DEVCUR.execute(stringSQL)
for platId, platName in DEVCUR.fetchall():
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`) VALUE('"+platId+"', '"+platName+"')"
    DEVCUR.execute(stringSQL)
DEVCONN.commit()

dictName = {}
dictLevel = {}
dictBad = {}
dictReport = {}
dictMobile = {}
dictStatus = {}
dictRate = {}

stringSQL = "SELECT DISTINCT platform_id, platform_name FROM `view_report` WHERE `show` = '1'"
DEVCUR.execute(stringSQL)
for platId, platName in DEVCUR.fetchall():
    dictName[platId] = platName
    dictReport[platId] = '1'

stringSQL = "SELECT platform_id, platform_name, level, ave_annualized_return FROM `view_mobile`"
DEVCUR.execute(stringSQL)
for platId, platName, level, ave_rate in DEVCUR.fetchall():
    dictName[platId] = platName
    dictMobile[platId] = '1'
    dictLevel[platId] = level
    dictRate[platId] = ave_rate

goodboy = []
stringSQL = "SELECT platform_id, platform_name, status FROM `total_status` ORDER BY `date` DESC"
DSCUR.execute(stringSQL)
for platId, platName, status in DSCUR.fetchall():
    if status < 0.89 and platId not in goodboy:
        dictBad[platId] = '1'
    if platId not in goodboy:
        dictStatus[platId] = round(status, 1)
    dictName[platId] = platName
    goodboy.append(platId)

for platid in dictName.keys():
    if platid is None:
        continue
    if platid not in dictReport.keys():
        dictReport[platid] = '0'
    if platid not in dictBad.keys():
        dictBad[platid] = '0'
    if platid not in dictMobile.keys():
        dictMobile[platid] = '0'
    if platid not in dictStatus.keys():
        dictStatus[platid] = '1'
    if platid not in dictLevel.keys():
        dictLevel[platid] = 'N/A'
    if platid not in dictRate.keys():
        dictRate[platid] = -1
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `level`, `report`, `bad`, `in_mobile`, `status`, `ave_rate`) VALUES('"+platid+"', '"+dictName[platid]+"', '"+dictLevel[platid]+"', '"+dictReport[platid]+"', '"+dictBad[platid]+"', '"+dictMobile[platid]+"', '"+str(dictStatus[platid])+"', '"+str(dictRate[platid])+"')"    
    DEVCUR.execute(stringSQL)
DEVCONN.commit()
