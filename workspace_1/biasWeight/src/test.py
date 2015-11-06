# /usr/bin/python
# encoding=utf8

from multiprocessing import Process, Pool, Manager,Lock
from multiprocessing.dummy import Pool as ThreadPool
import time
import Queue
import random
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import copy
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.colors import LogNorm
#from enthought.mayavi import mlab

# def f(que,_num,_index):
#     time.sleep(_num)
#     for i in range(_num):
#         que[_index] += 1
# 
# def f1(_weight_value_order_list1,range_temp):
#     Q_sum = 0
#     for j in range_temp:
#         _weight_value_order_list_temp = copy.deepcopy(_weight_value_order_list1)
#         for k in range(weight_index_number): #[0:2]
#             _weight_value_order_list_temp[weight_index[k]] = iteration_weight_list[(j / iteration_weight_number ** (weight_index_number -k - 1)) % iteration_weight_number]
#         print j, _weight_value_order_list_temp
#         Q_sum += j
#     _list[a] += Q_sum
#     z.value += Q_sum
#     time.sleep(2)
#         
# que = Manager().list(range(30))
# z = Manager().Value("d", 0)
# print type(que)
# print que[1]
startTime = time.time() 
# BLOCKCONTAINS = 3
# weight_number = 7
# iteration_weight_number = 3
# #weight_value_order_list1 = Manager().list([0] * weight_number )
# weight_value_order_list1 = [0] * weight_number
# iteration_weight_list = [x * 0.001 for x in range(1,iteration_weight_number+1)]
# print iteration_weight_list
# block_number = weight_number / BLOCKCONTAINS
# block_reminder = weight_number % BLOCKCONTAINS
# parallel_number = 4
# _list = Manager().list([0] * parallel_number)
# for i in range(block_number + 1):
#     if i == block_number:
#         weight_index = range(BLOCKCONTAINS * i,weight_number)
#     else:
#         weight_index = range(BLOCKCONTAINS * i,BLOCKCONTAINS * (i + 1))
#     weight_index_number = len(weight_index)
#     if weight_index_number == 0:
#         continue
#     #3**2 = 9
#     iteration_number = iteration_weight_number ** weight_index_number
#     print iteration_number
#     #开始并行
#     parallel_per_number = iteration_number / parallel_number
#     parallel_reminder = iteration_number % parallel_number
#     start = 0
#     end = 0
#     pool_list = [0] * parallel_number
#     sum_list = [0] * parallel_number
#     for a in range(parallel_number):
#         end = start + parallel_per_number
#         if parallel_reminder > 0:
#             end += 1
#             parallel_reminder -= 1
#         range_temp = range(start,end)
#         start = end
#         if len(range_temp) == 0:
#             continue
#         print range_temp
#         pool_list[a] = Process(target=f1,args = (weight_value_order_list1,range_temp))
#         pool_list[a].start()
#     for a in range(parallel_number):
#         if 0 != pool_list[a]:
#             pool_list[a].join()
#     weight_value_order_list1[0]=4
#     weight_value_order_list1[0]=3 
# print 111,_list
# print 222, z.value
#             for k in range(weight_index_number): #[0:2]
#                 weight_value_order_list1[weight_index[k]] = iteration_weight_list[(j / iteration_weight_number ** (weight_index_number -k - 1)) % iteration_weight_number]
#             print weight_value_order_list1
#             time.sleep(0.5)
# plt.plot(np.array(range(5)), np.array(range(5)), 'o', ms=15, label = "1")
# plt.plot(np.array([1,2,3]), np.array([2,4,6]), 's', ms=8, label = "2")
# plt.legend(loc='lower right', numpoints = 1, scatterpoints = 1, fontsize = 15)
# plt.show()

# mgr = Manager()
# que = mgr.list()
# que.append(0)
# que.append(0)
# p=[]
# a=[5,5]
# for i in range(2):
#     p.append(Process(target=f, args=(que, a[i],i)))
# for i in range(2):
#     p[i].start()
# for i in range(2):
#     p[i].join()
# print que
fig = plt.figure()
ax = fig.gca(projection='3d')
N = 40
x = np.linspace(1.0/N, 1, N)
y = np.linspace(1.0/N, 1, N)
X, Y = np.meshgrid(x, y)
P1 = 1/(1+(1-X)/Y/9.0)
P2 = 1/(1+(1-Y)/X*9.0)
surf = ax.plot_surface(X, Y, P1, rstride=1, cstride=1, norm = LogNorm(), cmap = cm.jet)
surf = ax.plot_surface(X, Y, P2, rstride=1, cstride=1, norm = LogNorm(), cmap = cm.jet)
plt.xlabel("p1")
plt.ylabel("p2")
plt.show()
#P1 = (1 + y) / x
print ""
print "finished"
endTime = time.time()
print "The whole program costs " + str(endTime - startTime) + " seconds."
    