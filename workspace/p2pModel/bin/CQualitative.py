#!/usr/bin/python
#encoding=utf-8

class CQualitative(object):
    def __init__(self):
        #平台网址
        self.website = ""

        #风险保证金构成
        self.reserve_fund = ""

        #融资情况，公开融资 or 天使 or A轮等等
        self.financing_status = ""

        #企业法人
        self.stakeholders = ""

        #资金池风险
        self.capital_pool_risk

        #成立日期，营业执照日期为准
        self.established_date = ""

        #企业所在地，营业执照所在地为准
        self.location = ""

        #转让费用
        self.project_transfer = -1

        #提现限制
        self.cash_limitation = ""

        #数据更新时间
        self.last_load = ""

        #逾期担保方式的打分
        self.compensation = -1

        #获得风投数额
        self.vc_cap_usd = -1

        #注册资本金额，营业执照注册资本为准
        self.registered_cap = -1

        #项目信息总分
        self.borrower_transparency = -1

        #逾期透明度
        self.overdue_transparency

        #数据披露总分
        self.financial_transparency = -1

        #媒体曝光度，百度搜索
        self.PR_transparency1 = -1

        #媒体曝光度
        self.PR_transparency2 = -1

        #风险准备金数额a
        self.risk_allowance_ratio1 = -1

        #风险准备金数额b，为准备额外部分抽取比例
        self.risk_allowance_ratio2 = -1

        #风险准备金
        self.risk_allowance_ratio = -1

        #实名制综合评分
        self.real_name = -1

        #是否支持债权转让，是=1，否=0
        self.debt_transfer = -1

        #是否支持客服综合评分
        self.customer_service = -1

        #是否有第三方托管机构
        self.third_entrust = -1

        #是否有第三方担保机构
        self.third_assurance = -1

        #网站技术总分
        self.technical_security = -1

        #母公司注册资本
        self.parent_company_cap = -1

        #母公司名称
        self.parent_company_name = ""

        #网站建设情况综合评分
        self.website1 = -1

        #综合投资意愿
        self.attitude = -1

        #平台票据标转让
        self.bill_debt = -1

        #是否有基金标，是=1，否=0
        self.fund_yn = -1

        #平台汽车标的业务情况，主要=1，次要=0.5，无=0
        self.car_debt = -1

        #平台小额标的业务情况，主要=1，次要=0.5，无=0
        self.small_credit_bid = -1

        #平台大额标的业务情况，主要=1，次要=0.5，无=0
        self.big_credit_bid = -1

        #是否支持自动投标，是=1，否=0
        self.autobid_yn = -1

        #平台房产标的业务情况，主要=1，次要=0.5，无=0
        self.house_debt = -1

        #填写逾期归还方式的文字内容
        self.advanced_repayment = ""

        #平台主要业务方向，抵押/质押，信用标
        self.major_debt_type = ""

        #是否有担保标，很多=1，少量=0.5，没有=0
        self.guarantee_debt = -1

        #标的行业分布
        self.industry_distribution = ""

        #平台业务范围
        self.deo_distribution = ""

        #是否有APP端，是=1， 否=0
        self.app_yn = -1

        #平台问题描述
        self.problem = ""

        #平台充值费用
        self.cash_in_fee = ""

        #平台提现费用
        self.cash_out_fee = ""

        #平台评价
        self.summary = ""

        #平台资金管理费
        self.management_fee = ""

        #是否支持自动投标，是=1，否=0
        self.auto_invest = -1

        #是否上市，是=1，否=0
        self.listing = -1

        #是否国资背景，是=1，否=0
        self.state_owned = -1

        #是否银行背景，是=1，否=0
        self.bank = -1

        #平台联系电话
        self.contect_number = -1

        #平台QQ群
        self.QQ_group = -1

        #平台充值费用全描述
        self.backup_cash_in_fee = -1

        #平台提现费用全描述
        self.backup_cash_out_fee = -1

        #平台简介全描述
        self.backup_summary

        #平台资金管理费全描述
        self.backup_management_fee
