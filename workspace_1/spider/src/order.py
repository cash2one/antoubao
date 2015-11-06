#!/use/bin/python
#coding=utf-8

import random
import timeit
import time

def InsertSort(_list):
    value_list = [_list[0]]
    for value_new in _list[1:]:
        count = 0
        for value_old in value_list:
            if value_old >= value_new:
                break
            count += 1
        value_list.insert(count, value_new)
    return value_list

def ShellSort(_list):
    value_list = _list[::]
    list_number = len(_list)
    d = list_number / 2
    while d > 0:
        for i in range(d):
            index_list = range(i, list_number, d)
            list_temp = _list[i::d]
            
            list_temp = InsertSort(list_temp)
            for j in range(len(index_list)):
                value_list[index_list[j]] = list_temp[j]
        d /= 2
    return value_list

def test(_sort_function):
    N = 100
    value_list = random.sample(range(N), N)
    print _sort_function.__name__
    result_list = _sort_function(value_list)
    print result_list
    if result_list != range(N):
        print _sort_function.__name__ + " is wrong !"
        exit(1)
    print
    
if __name__ == "__main__":
    start = time.time()
    
    #获得当前文件的函数列表和module列表
    g=globals()
    function_list = []
    module_list = []
    for x in g.keys():
        if hasattr(g[x],'__call__') and "test" not in x:
            function_list.append(x)
            #测试：
            test(eval(x))
        elif hasattr(g[x],'__package__') and not hasattr(g[x],'__import__'):
            module_list.append(x)
    #组装setup字符串
    setup = "from __main__ import "
    for module in module_list:
        setup += module + ", "
    for func in function_list:
        setup += func + ", "
    setup = setup[:-2] + "; "
    
    repeat_number = 100
    N = 100
    setup += "N = " + str(N) + "; "
    
    for func in function_list:
        print func
        stmt = "value_list = random.sample(range(N), N); "
        stmt += func + "(value_list)"
        t = timeit.Timer(stmt = stmt, setup = setup)
        value_list = t.repeat(repeat = repeat_number, number = 1)
        print "min = " + str(min(value_list))
        print "max = " + str(max(value_list))
        print "ave = " + str(sum(value_list) / repeat_number)
        print
        
    end = time.time()
    print "花费" + str(end - start) + "秒."