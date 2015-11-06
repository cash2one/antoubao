# -*- coding: utf-8 -*-
#!/usr/bin/python

# from mailthon import postman, email
from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
import sys


# def send_mail(site, type):
# 
#     smtp = postman(host='smtp.ym.163.com', port=25, auth=('shuaizhiguo@antoubao.cn', 'gladstone,123'))
#     if int(type) == 0:
#         _content = site + " 抓取出现问题 "
#     else:
#         _content = site + " 抓取结果出现异常 "
#     smtp.send(email(
#         sender='Spider Guard <shuaizhiguo@antoubao.cn>',
#         receivers=['<shuaizhiguo@antoubao.cn>','<lihaixiao@antoubao.cn>','<fenghan@antoubao.cn>','<xiebo@antoubao.cn>','<qishuai@antoubao.cn>'],
#         #receivers=['<shuaizhiguo@antoubao.cn>'],
#         subject='Spider 报警',
#         content=_content,
# ))

def collect_dead_info(site):
    srcdb_daily_bids = "platform_bids_daily_report"
    this_date = time.strftime("%Y%m%d")
    
    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    
    stringSQL="SELECT * FROM " + srcdb_daily_bids + " WHERE `site_id` = '" + site + "' AND date = '" + this_date + "'"
    ret = cur_db.execute(stringSQL)
    if ret == 0:
        stringSQL="INSERT INTO " + srcdb_daily_bids + " (`site_id`, `date`, `dead_bids_number`) VALUES('" + "', '".join([site, this_date, "1"]) + "')"
        cur_db.execute(stringSQL)
    else:
        stringSQL = "UPDATE " + srcdb_daily_bids + " SET `dead_bids_number` = `dead_bids_number` + 1 WHERE `site_id` = '" + site + "' AND date = '" + this_date + "'"
        cur_db.execute(stringSQL)
    conn_db.commit()
    
    closeCursors(cur_db)
    closeConns(conn_db)

if __name__=='__main__':
    #send_mail(sys.argv[1],sys.argv[2])
    collect_dead_info(delQuotes([str(sys.argv[1])])[0])