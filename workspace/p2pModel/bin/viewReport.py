#!/use/bin/python
#coding=utf-8

from header import *

E2BADDB = "E2_quantitative_data_report"
DSTDB = "view_report"

#读取本表的历史记录，防止编辑过的信息被覆盖。
kv = {}
stringSQL = "SELECT platform_id, date FROM "+DSTDB
DEVCUR.execute(stringSQL)
for platId, date in DEVCUR.fetchall():
    kv[platId+str(date)] = 1
        
arrKeys = []
stringSQL = "SHOW FULL COLUMNS FROM "+E2BADDB
DEVCUR.execute(stringSQL)
for col in DEVCUR.fetchall():
    if col[0] == "id":
        continue
    arrKeys.append(col[0])

#生成报告配置
stringSQL = "SELECT platform_id, date FROM "+E2BADDB+" WHERE `platform_name` = '相关属性平均'"
DEVCUR.execute(stringSQL)
for platId, date in DEVCUR.fetchall():
    platId = platId[:-1]
    #线图时间
    firstDate = int(date)+7*24*3600
    stringSQL = "SELECT DISTINCT date FROM "+E2BADDB+" WHERE `platform_id` = '"+platId+"' ORDER BY `date` DESC LIMIT 26"
    DEVCUR.execute(stringSQL)
    datelist = DEVCUR.fetchall()
    lastDate = datelist[-1][0]
    #柱图时间
    barDate = int(date)
    #报告发布时间
    reportDate = int(date)
    #检查数据是否已存在，存在则跳过。
    if platId+str(reportDate) in kv:
        continue
    
    #更新Report_Title表
    stringSQL = "INSERT INTO "+DSTDB+"_title(`platform_id`, `date`, `fore`, `end`) VALUES('"+platId+"', '"+str(reportDate)+"', 'N/A', 'N/A')"
    DEVCUR.execute(stringSQL)

    #获取平台名称
    stringSQL = "SELECT DISTINCT platform_name FROM "+E2BADDB+" WHERE `platform_id` = '"+platId+"'"
    DEVCUR.execute(stringSQL)
    platName = DEVCUR.fetchone()[0]

    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'radar', '"+platId+"', '"+str(barDate)+"', 'capital_adequacy_ratio,activeness_credibility, distribution,mobility_original,growth,reputation', '', '万元')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bars', '"+platId+",strategyA,strategyC', '"+str(barDate)+"', 'registered_cap,vc_cap_usd', '自有资本', '万元')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bar', '"+platId+",strategyA,"+platId+"B', '"+str(barDate)+"', 'turnover_registered', '资本充足率', '%')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bar', '"+platId+",strategyA,"+platId+"B', '"+str(barDate)+"', 'weekly_total_investor', '总投资人数', '人')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'line', '"+platId+"', '"+str(firstDate)+","+str(lastDate)+"', 'weekly_total_investor', '周投资人数', '人')"
    DEVCUR.execute(stringSQL)

    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'line', '"+platId+"', '"+str(firstDate)+","+str(lastDate)+"', 'weekly_ratio_new_old', '新投资人占比', '')"
    DEVCUR.execute(stringSQL)

    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bars', '"+platId+",strategyA,strategyC', '"+str(barDate)+"', 'top5_ratio_investment,top10_ratio_investment', '投资人集中度', '万元')"
    DEVCUR.execute(stringSQL)

    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'line', '"+platId+"', '"+str(firstDate)+","+str(lastDate)+"', 'top5_ratio_investment', '前五大投资人集中度', '')"
    DEVCUR.execute(stringSQL)

    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'line', '"+platId+"', '"+str(firstDate)+","+str(lastDate)+"', 'top10_ratio_investment', '前十大投资人集中度', '')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'line', '"+platId+"', '"+str(firstDate)+","+str(lastDate)+"', 'weekly_lending', '周投资额', '万元')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bar', '"+platId+",strategyA,strategyC', '"+str(barDate)+"', 'weekly_ave_investment', '人均投资额', '万元')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'linebar', '"+platId+"', '"+str(firstDate)+","+str(lastDate)+"', 'weekly_total_investor,weekly_ave_investment', '投资人数&人均投资额', '人&万元')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'linebar', '"+platId+"', '"+str(firstDate)+","+str(lastDate)+"', 'weekly_total_investor,weekly_lending', '投资人数&总投资额', '人&万元')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'line', '"+platId+"', '"+str(firstDate)+","+str(lastDate)+"', 'weekly_ave_bid_close_time', '每万元募资时间', '秒/万元')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'linebar', '"+platId+"', '"+str(firstDate)+","+str(lastDate)+"', 'weekly_ave_bid_close_time,weekly_total_investor', '每万元募资时间&投资人数', '秒/万元&人')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bar', '"+platId+",strategyA,strategyC', '"+str(barDate)+"', 'ave_annualized_return', '年化收益率', '%')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'linebar', '"+platId+"', '"+str(firstDate)+","+str(lastDate)+"', 'ave_annualized_return,weekly_total_investor', '年化收益率&投资人数', '%&人')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bars', '"+platId+",strategyA,"+platId+"B', '"+str(barDate)+"', 'top10_ratio_loan,top5_ratio_loan', '借款人集中度', '%')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bars', '"+platId+",strategyA,strategyC', '"+str(barDate)+"', 'weekly_ave_lending_per_borrower,weekly_ave_lending_per_bid', '人均借款&标均借款', '万元')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'linebar', '"+platId+"', '"+str(firstDate)+","+str(lastDate)+"', 'weekly_total_borrower,weekly_ave_lending_per_bid', '借款人数&标均借款', '人&万元')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bar', '"+platId+",strategyA,"+platId+"B', '"+str(barDate)+"', 'not_returned_yet', '待还指标', '')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'line', '"+platId+"', '"+str(firstDate)+","+str(lastDate)+"', 'not_returned_yet', '待还指标', '')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bar', '"+platId+",strategyA,"+platId+"B', '"+str(barDate)+"', 'short_term_debt_ratio', '短期债务比率', '%')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bar', '"+platId+",strategyA,strategyC', '"+str(barDate)+"', 'cash_flow_in', '净现金流入', '')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'line', '"+platId+"', '"+str(firstDate)+","+str(lastDate)+"', 'cash_flow_in', '净现金流入', '')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bar', '"+platId+",strategyA,"+platId+"B', '"+str(barDate)+"', 'weekly_loan_period', '平均借款周期', '天')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'line', '"+platId+"', '"+str(firstDate)+","+str(lastDate)+"', 'weekly_loan_period', '平均借款周期', '')"
    DEVCUR.execute(stringSQL)

    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bars', '"+platId+",strategyA,strategyC', '"+str(barDate)+"', 'money_growth,borrower_growth,investor_growth,market_share_growth', '平台成长性', '')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bars', '"+platId+"', '"+str(barDate)+"', 'financial_transparency,overdue_transparency,borrower_transparency,PR_transparency1,PR_transparency2', '透明度（内部使用）', '')"
    DEVCUR.execute(stringSQL)
    
    stringSQL = "INSERT INTO "+DSTDB+"(`platform_id`, `platform_name`, `date`, `show`, `type`, `platform_id_list`, `date_list`, `property`, `title`, `unit`) VALUES('"+platId+"', '"+platName+"', '"+str(date)+"', '0', 'bars', '"+platId+"', '"+str(barDate)+"', 'compensation,third_assurance,real_name,debt_transfer,customer_service,technical_seDEVCURity', '安全保障（内部使用）', '')"
    DEVCUR.execute(stringSQL)
DEVCONN.commit()
