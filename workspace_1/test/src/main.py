# /usr/bin/python
# encoding=utf8

from sympy import *
from sympy import Derivative as D
# 
# def evalfEquation2(a, b, c, inputvalue_X):
#     y = Symbol('y')
#     x = Symbol('x')
#     y = (x**2)*a + b * x + c #这里根据参数a, b, c的不同，我们就可以定义一个任意的一元二次方程
#     print y
#     return y.subs(x, inputvalue_X)
# 
# for i in range(0, 50, 1):
#     print evalfEquation2(2,3,4,i) #这里传入的i其实就是你定义的自变量x, 打印结果就是y（随x变化而变化的y）

index_dict = {}    
index_3_list = ["weekly_new_investor", "weekly_total_investor", "weekly_ave_investment", "weekly_ave_investment_old", "top5_ratio_investment", "top10_ratio_investment"]
index_2_list = ["registered_cap", "vc_cap", "turnover_registered", "investor", "turnover", "turnover_period", "weekly_ave_turnover", "bidding_activeness", "investor_concentration", "investor_HHI", "weekly_ratio_new_old"]
for index in index_2_list + index_3_list:
    index_dict[index] = Symbol(index)

index_dict["investor"] = 0.3 * index_dict["weekly_new_investor"] + 0.7 * index_dict["weekly_total_investor"]
index_dict["aaa"] = 0.3 * index_dict["investor"] + 0.7 * index_dict["weekly_total_investor"]
print index_dict["aaa"]
print diff(index_dict["investor"], index_dict["weekly_new_investor"])
print diff(index_dict["aaa"], index_dict["weekly_total_investor"])
print diff(index_dict["aaa"], index_dict["investor"])

        