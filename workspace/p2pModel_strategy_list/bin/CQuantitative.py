#!/usr/bin/python
#encoding=utf-8

class CQuantitative(object):
    def __init__(self):
        #资本充足率
        self.turnover_registered = -1

        #本周新投资人数
        self.weekly_new_investor = -1

        #总投资人数
        self.weekly_total_investor = -1

        #周借款总额
        self.weekly_lending = -1

        #周平均投资额
        self.weekly_ave_investment = -1

        #老投资人平均投资额
        self.weekly_ave_investment_old = -1

        #标均投资额
        self.weekly_ave_investment_per_bid = -1

        #周平均满标时间
        self.weekly_close_time = -1

        #投资人HHI
        self.investor_HHI = -1

        #新老投资人比例
        self.weekly_ratio_new_old = -1

        #人均借款额
        self.weekly_ave_lending_per_borrower = -1

        #标均借款额
        self.weekly_ave_lending_per_bid = -1

        #总借款人数
        self.weekly_total_borrower = -1

        #前十借款人占比
        self.top10_ratio_loan = -1

        #前五借款人占比
        self.top5_ratio_loan = -1

        #借款人HHI
        self.borrower_HHI = -1

        #待还指标
        self.not_returned_yet = -1

        #周还款期限
        self.weekly_loan_period = -1

        #贷款余额指标
        self.outstanding_loan_ratio = -1

        #投资增长率
        self.money_growth = -1

        #借款人增长率
        self.borrower_growth = -1

        #投资人增长率
        self.investor_growth = -1

        #市场增长率
        self.market_share_growth = -1

        #平均年化利率
        self.ave_annualized_return = -1

        #后四周借款总额
        self.latest4week_lending = -1

        #加权成交量
        self.turnover_period = -1

        #短期债务比率
        self.short_term_debt_ratio = -1

        #黑名单
        self.black = -1

        #净现金流入
        self.cash_flow_in = -1

        #前五投资人占比
        self.top5_ratio_investment = -1

        #前十投资人占比
        self.top10_ratio_investment = -1
