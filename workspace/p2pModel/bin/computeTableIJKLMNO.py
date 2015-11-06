#!/usr/bin/python
#encoding=utf-8

from header import *

def usage():
    print "COMMAND:"
    print "\tpython "+sys.argv[0]+" [-all|-t]"
    print ""
    print "OPTIONS:"
    print "\t-all: 计算所有周的统计数据"
    print "\t-t [timestamp]: 计算指定周的统计数据"
    exit(-1)

if len(sys.argv) < 2:
    usage()
elif sys.argv[1] == '-all':
elif sys.argv[1] == '-t':
    #读取指定日期的表E1。
    if len(sys.argv) < 3:
        usage()
    else:
        timestamp = sys.argv[2]
        if timestamp < STARTDATE:
            print "Invalid date("+str(timestamp)+"), the must be equal or greater than "+STARTDATE
            exit(-1)
else:
    usage()
