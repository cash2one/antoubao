#!/usr/bin/python
#encoding=utf-8

import random
import hashlib
import sys
import MySQLdb
import json
import os
import redis
import json
#import CPlatform
#import CStatis
import numpy as np
from math import log
from utils import *

#数据库配置
PORT=3306
USERNAME="root"
DBNAME="antoubao"

#数据源配置
DSHOST="db-x1.antoubao.cn"
DSPWD="4njMOzOjli"
DSCONN=MySQLdb.connect(host=DSHOST, user=USERNAME, passwd=DSPWD, db=DBNAME, port=PORT)
DSCUR=DSCONN.cursor()
DSCUR.execute("SET NAMES 'UTF8'")
DSCUR.execute("SET CHARACTER SET UTF8")
DSCUR.execute("SET CHARACTER_SET_RESULTS=UTF8")
DSCUR.execute("SET CHARACTER_SET_CONNECTION=UTF8")

#分析库配置
DATAHOST="ddpt-data.antoubao.cn"
DATAPWD="4njMOzOjli"
DATACONN=MySQLdb.connect(host=DATAHOST, user=USERNAME, passwd=DATAPWD, db=DBNAME, port=PORT)
DATACUR=DATACONN.cursor()
DATACUR.execute("SET NAMES 'UTF8'")
DATACUR.execute("SET CHARACTER SET UTF8")
DATACUR.execute("SET CHARACTER_SET_RESULTS=UTF8")
DATACUR.execute("SET CHARACTER_SET_CONNECTION=UTF8")

#分析库配置
DEVHOST="dev-x1.antoubao.cn"
DEVPWD="4njMOzOjli"
DEVCONN=MySQLdb.connect(host=DEVHOST, user=USERNAME, passwd=DEVPWD, db=DBNAME, port=PORT)
DEVCUR=DEVCONN.cursor()
DEVCUR.execute("SET NAMES 'UTF8'")
DEVCUR.execute("SET CHARACTER SET UTF8")
DEVCUR.execute("SET CHARACTER_SET_RESULTS=UTF8")
DEVCUR.execute("SET CHARACTER_SET_CONNECTION=UTF8")

#分析库配置
TYPES = {"1SIG": "I_statis_1sigma", \
        "2SIG": "J_statis_2sigma", \
        "3SIG": "K_statis_3sigma", \
        "MIN": "L_statis_MIN", \
        "MAX": "M_statis_MAX", \
        "AVE": "N_statis_AVE", \
        "VAR": "O_statis_VAR", \
        "TOP20": "N1_statis_TOP20AVE"}

'''
#测试库配置
TESTHOST="ddpt-test.antoubao.cn"
TESTPWD="4njMOzOjli"
TESTCONN=MySQLdb.connect(host=TESTHOST, user=USERNAME, passwd=TESTPWD, db=DBNAME, port=PORT)
TESTCUR=TESTCONN.cursor()
TESTCUR.execute("SET NAMES 'UTF8'")
TESTCUR.execute("SET CHARACTER SET UTF8")
TESTCUR.execute("SET CHARACTER_SET_RESULTS=UTF8")
TESTCUR.execute("SET CHARACTER_SET_CONNECTION=UTF8")
'''

#Redis配置
REDISHOST="127.0.0.1"
REDISPORT=6379
REDISPWD="HpH5S6mZet"
#定量表
dbQUANTI=0
#定性表
dbQUALIT=1
#状态表
dbSTATUS=2
#统计表
dbSTATIS=3
#定量分数表
dbQUASCO=4
#分数表
dbSCORED=5
#惩罚表
dbPUNISH=6
#平滑表
dbSMOOTH=7
#降级表
dbRAKPUN=8
#汇总表
dbRESULT=9
#报告表
dbREPORT=10
rQUANTI = redis.Redis(host=REDISHOST, port=REDISPORT, db=dbQUANTI) #E2
rQUALIT = redis.Redis(host=REDISHOST, port=REDISPORT, db=dbQUALIT) #F
rSTATUS = redis.Redis(host=REDISHOST, port=REDISPORT, db=dbSTATUS) #total_status
rSTATIS = redis.Redis(host=REDISHOST, port=REDISPORT, db=dbSTATIS)
rQUASCO = redis.Redis(host=REDISHOST, port=REDISPORT, db=dbQUASCO) #E3
rSCORED = redis.Redis(host=REDISHOST, port=REDISPORT, db=dbSCORED) #H
rPUNISH = redis.Redis(host=REDISHOST, port=REDISPORT, db=dbPUNISH) #P
rSMOOTH = redis.Redis(host=REDISHOST, port=REDISPORT, db=dbSMOOTH) #S
rRAKPUN = redis.Redis(host=REDISHOST, port=REDISPORT, db=dbRAKPUN) #T
rRESULT = redis.Redis(host=REDISHOST, port=REDISPORT, db=dbRESULT) #V
rREPORT = redis.Redis(host=REDISHOST, port=REDISPORT, db=dbREPORT) #E2_report
TABLE = {dbQUANTI: "E2_quantitative_data", \
        dbQUASCO: "E3_quantitative_score", \
        dbSCORED: "H_score", \
        dbPUNISH: "P_punishment", \
        dbSMOOTH: "S_smooth", \
        dbRAKPUN: "T_rank", \
        dbRESULT: "V_view", \
        dbREPORT: "E2_quantitative_data_report"}

#数据起始日期
STARTDATE=1422720000
#分数起始日期
SCOREDATE=STARTDATE+(4*7*24*3600)

#惩罚系数
W = 0.844

#字段过滤项
INVALID_TITLE = ["platform_id", "platform_name", "black", "date", "in_and_out", "punishment_info", "punishment", "status"]
QUALIT_TITLE = ['customer_service', 'third_assurance', 'technical_security', 'debt_transfer', 'third_entrust', 'overdue_transparency', 'financial_transparency', 'borrower_transparency', 'PR_transparency2', 'real_name']

#罚分，负数为加分。红岭创投-3.05、e租宝-4
hehePunish = {'c38f13eb81':3.05, '05f75f9e85':4}
#黑名单，米牛网、658金融城、金联储、盈盈理财、小企业e家
BLACKLIST = ['209c2758e2', 'fad64286c7', '5041ece6c3', 'a275f904fc', 'b6a08f5df6']

#呵呵坏站级别，为了和已发布的报告保持一致，对下列坏站的级别进行锁定。
BADLEVEL = {'c31f707db0':'B++', \
        'a44b3abd4e':'B++', \
        '9a81f0ff1c':'B+', \
        '5ec0b8c81e':'B+', \
        'ac7eb08d8b':'B+', \
        '1434f0704f':'B+', \
        '9e2b3cebc7':'B+', \
        'ad5fa3a811':'B+', \
        '39ccdefafb':'B+', \
        '0e51df24ab':'B+', \
        '9a0f56ecdf':'B+', \
        '0d428fd0ed':'B+', \
        '29e0cdb53f':'B+', \
        '791c2e8f29':'B+', \
        'abe7a45f19':'B+', \
        '6e0331203e':'B+', \
        'da5b476d78':'B+', \
        '847e0795e3':'B+', \
        'cf0f9c0061':'B+', \
        '5452674c5c':'B', \
        '43783a79c4':'B', \
        '44e73730f2':'B', \
        '58ad4da70e':'B', \
        'b144563a7f':'B', \
        'd711cc60fc':'B', \
        '1696e25b8b':'B', \
        'de87e2f695':'B', \
        'e41012629d':'B', \
        'dcdd3bfc72':'B', \
        '971fe8d3bd':'B', \
        '299102f09f':'B', \
        'c5bb452d0d':'B', \
        'a108957448':'B', \
        '7f4559fd7f':'B', \
        '05ffce85a2':'B', \
        '3a88fd8031':'B', \
        'f222e564db':'C', \
        '666d724ce1':'C', \
        '4e2008a495':'C', \
        'ec30673f51':'C', \
        '8ecfbeb8d5':'C', \
        'c058541f9a':'C', \
        'a360217690':'C'}
