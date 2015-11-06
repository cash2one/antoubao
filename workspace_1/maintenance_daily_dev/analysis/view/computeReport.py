#!/use/bin/python
#coding=utf-8

import MySQLdb
import time
from atbtools.header import * 

if __name__ == "__main__":
    conn=MySQLdb.connect(host=DEVHOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    cur=conn.cursor()
    aCur=conn.cursor()
    bCur=conn.cursor()
    sconn=MySQLdb.connect(host=DEVHOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT)
    scur=sconn.cursor()

    cur.execute("SET NAMES 'UTF8'")
    cur.execute("SET CHARACTER SET UTF8")
    cur.execute("SET CHARACTER_SET_RESULTS=UTF8")
    cur.execute("SET CHARACTER_SET_CONNECTION=UTF8")
    scur.execute("SET NAMES 'UTF8'")
    scur.execute("SET CHARACTER SET UTF8")
    scur.execute("SET CHARACTER_SET_RESULTS=UTF8")
    scur.execute("SET CHARACTER_SET_CONNECTION=UTF8")
    
    E2DB = "platform_quantitative_data_E2"
    BADDB = "view_bad"
    CONFDB = "view_strategyB_configure"
    DSTDB = "view_report"

    #读取本表的历史记录，防止编辑过的信息被覆盖。
    kv = {}
    stringSQL = "SELECT platform_id, date FROM "+DSTDB
    cur.execute(stringSQL)
    for platId, date in cur.fetchall():
        kv[platId+str(date)] = 1
        
    arrKeys = []
    stringSQL = "SHOW FULL COLUMNS FROM "+E2DB
    cur.execute(stringSQL)
    for col in cur.fetchall():
        if col[0] == "id":
            continue
        arrKeys.append(col[0])
    '''
    #E2表数据平滑处理
    aveKeys = ['date', 'weekly_lending', 'ave_annualized_return', 'weekly_total_investor', 'weekly_total_borrower', 'weekly_ave_bid_close_time', 'weekly_ave_lending_per_borrower', 'weekly_ave_lending_per_bid']
    stringSQL = "SELECT DISTINCT platform_id FROM "+E2DB+" WHERE `platform_name` = 'strategy_report'"
    cur.execute(stringSQL)
    for platid in cur.fetchall():
        platid = platid[0][:-1]
        stringSQL = "SELECT `"+"`,`".join(aveKeys)+"` FROM "+E2DB+" WHERE `platform_id` = '"+platid+"' ORDER BY `date` DESC"
        aCur.execute(stringSQL)
        for _list in aCur.fetchall():
            select = ""
            date = _list[0]
            for i in range(1, len(_list)):
                if _list[i] == 0:
                    stringSQL = "SELECT avg("+aveKeys[i]+") FROM "+E2DB+" WHERE `platform_id` = '"+platid+"' AND (`date` = '"+str(date-7*24*3600)+"' OR `date` = '"+str(date+7*24*3600)+"')"
                    bCur.execute(stringSQL)
                    select += "`"+aveKeys[i]+"` = '"+str(bCur.fetchone()[0])+"', "
            if select != "":
                stringSQL = "UPDATE "+E2DB+" SET "+select[:-2]+" WHERE `platform_id` = '"+platid+"' AND `date` = '"+str(date)+"'"
                if platid == '1cf2ae102b':
                    print stringSQL
                bCur.execute(stringSQL)
                conn.commit()
    '''             

    #读取策略B配置
    config = []
    stringSQL = "SELECT prop FROM "+CONFDB
    scur.execute(stringSQL)
    for prop in scur.fetchall():
        config.append(prop[0])

    #生成报告配置
    stringSQL = "SELECT platform_id, date FROM "+E2DB+" WHERE `platform_name` = 'strategy_report' AND `platform_id` NOT LIKE '%strategy%'"
    cur.execute(stringSQL)
    for platId, date in cur.fetchall():
        platId = platId[:-1]
        date = int(date)+7*24*3600*2
        if platId+str(date) in kv:
            continue

        stringSQL = "INSERT INTO "+DSTDB+"_title(`platform_id`, `date`, `fore`, `end`) VALUES('"+platId+"', '"+str(date)+"', 'N/A', 'N/A')"
        aCur.execute(stringSQL)

        '''
        stringSQL = "SELECT DISTINCT date FROM "+E2DB+" WHERE `date` <= '"+str(date)+"' ORDER BY `date` DESC LIMIT 26"
        ret = aCur.execute(stringSQL)
        if ret == 0:
            continue
        dates = aCur.fetchall()
        firstdate = len(dates)>=2 and dates[1][0] or dates[0][0]
        lastdate = dates[len(dates)-1][0]
        '''
        bardate = date-7*24*3600*2
        firstdate = bardate+7*24*3600
        stringSQL = "SELECT DISTINCT date FROM "+E2DB+" WHERE `date` <= '"+str(firstdate)+"' AND `platform_id` = '"+platId+"' ORDER BY `date` DESC LIMIT 26"
        aCur.execute(stringSQL)
        datelist = aCur.fetchall()
        lastdate = datelist[-1][0]
        stringSQL = "SELECT DISTINCT platform_name FROM "+E2DB+" WHERE `platform_id` = '"+platId+"'"
        aCur.execute(stringSQL)
        platName = aCur.fetchone()[0]
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'radar', '"+platId+"', '"+str(bardate)+"', 'capital_adequacy_ratio,activeness_credibility, distribution,mobility_original,growth,reputation', '', '万元')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bars', '"+platId+",strategyA,strategyC', '"+str(bardate)+"', 'registered_cap,vc_cap_usd', '自有资本', '万元')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bar', '"+platId+",strategyA,"+platId+"B', '"+str(bardate)+"', 'turnover_registered', '资本充足率', '%')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bar', '"+platId+",strategyA,"+platId+"B', '"+str(bardate)+"', 'weekly_total_investor', '总投资人数', '人')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'line', '"+platId+"', '"+str(firstdate)+","+str(lastdate)+"', 'weekly_total_investor', '周投资人数', '人')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'line', '"+platId+"', '"+str(firstdate)+","+str(lastdate)+"', 'weekly_ratio_new_old', '新老投资人数比例', '')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'line', '"+platId+"', '"+str(firstdate)+","+str(lastdate)+"', 'weekly_lending', '周投资额', '万元')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bar', '"+platId+",strategyA,strategyC', '"+str(bardate)+"', 'weekly_ave_investment', '人均投资额', '万元')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'linebar', '"+platId+"', '"+str(firstdate)+","+str(lastdate)+"', 'weekly_total_investor,weekly_ave_investment', '投资人数&人均投资额', '人&万元')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'linebar', '"+platId+"', '"+str(firstdate)+","+str(lastdate)+"', 'weekly_total_investor,weekly_lending', '投资人数&总投资额', '人&万元')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'line', '"+platId+"', '"+str(firstdate)+","+str(lastdate)+"', 'weekly_ave_bid_close_time', '每万元募资时间', '秒/万元')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'linebar', '"+platId+"', '"+str(firstdate)+","+str(lastdate)+"', 'weekly_ave_bid_close_time,weekly_total_investor', '每万元募资时间&投资人数', '秒/万元&人')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bar', '"+platId+",strategyA,strategyC', '"+str(bardate)+"', 'ave_annualized_return', '年化收益率', '%')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'linebar', '"+platId+"', '"+str(firstdate)+","+str(lastdate)+"', 'ave_annualized_return,weekly_total_investor', '年化收益率&投资人数', '%&人')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bars', '"+platId+",strategyA,"+platId+"B', '"+str(bardate)+"', 'top10_ratio_loan,top5_ratio_loan', '借款人集中度', '%')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bars', '"+platId+",strategyA,strategyC', '"+str(bardate)+"', 'weekly_ave_lending_per_borrower,weekly_ave_lending_per_bid', '人均借款&标均借款', '万元')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'linebar', '"+platId+"', '"+str(firstdate)+","+str(lastdate)+"', 'weekly_total_borrower,weekly_ave_lending_per_bid', '借款人数&标均借款', '人&万元')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bar', '"+platId+",strategyA,"+platId+"B', '"+str(bardate)+"', 'not_returned_yet', '待还指标', '')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'line', '"+platId+"', '"+str(firstdate)+","+str(lastdate)+"', 'not_returned_yet', '待还指标', '')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bar', '"+platId+",strategyA,"+platId+"B', '"+str(bardate)+"', 'short_term_debt_ratio', '短期债务比率', '%')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bar', '"+platId+",strategyA,strategyC', '"+str(bardate)+"', 'cash_flow_in', '净现金流入', '')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'line', '"+platId+"', '"+str(firstdate)+","+str(lastdate)+"', 'cash_flow_in', '净现金流入', '')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bar', '"+platId+",strategyA,"+platId+"B', '"+str(bardate)+"', 'weekly_loan_period', '平均借款周期', '天')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'line', '"+platId+"', '"+str(firstdate)+","+str(lastdate)+"', 'weekly_loan_period', '平均借款周期', '')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bars', '"+platId+",strategyA,strategyC', '"+str(bardate)+"', 'money_growth,borrower_growth,investor_growth,market_share_growth', '平台成长性', '')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bars', '"+platId+"', '"+str(bardate)+"', 'financial_transparency,overdue_transparency,borrower_transparency,PR_transparency1,PR_transparency2', '透明度（内部使用）', '')"
        cur.execute(stringSQL)
        stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bars', '"+platId+"', '"+str(bardate)+"', 'compensation,third_assurance,real_name,debt_transfer,customer_service,technical_security', '安全保障（内部使用）', '')"
        cur.execute(stringSQL)
        conn.commit()
