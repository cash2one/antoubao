#!/use/bin/python
#coding=utf-8

import time
import socket
from binascii import hexlify
from atbtools.header import *
from atbtools.computeTools import *
from math import ceil

#获得主机名和ip地址
def printMachineInfo():
    host_name = socket.gethostname() #获得本机host名
    ip_addr = socket.gethostbyname(host_name) #获得某个host的ip地址
    packed_ip_addr = socket.inet_aton(ip_addr)
    uppacked_ip_addr = socket.inet_ntoa(packed_ip_addr)
    print "Host name: %s" % host_name
    print "IP address: %s" % ip_addr
    print "IP packed: %s" % hexlify(packed_ip_addr)
    print "IP unpacked: %s" % uppacked_ip_addr

#获得每个端口的服务名
def getServiceNameByPort(_port = None):
    if _port != None:
        if isinstance(_port, int):
            #通过端口号获得服务名
            print "Port: %s => Service name: %s" % (_port, socket.getservbyport(_port))
        if isinstance(_port, str):
            #通过服务名获得端口号
            print "Service name: %s => Port: %s" % (_port, socket.getservbyname(_port))
    else:
        for _port in range(100):
            try:
                print "Port: %s => Service name: %s" % (_port, socket.getservbyport(_port))
            except:
                pass
                                                      
if __name__ == "__main__":
#     printMachineInfo()
    getServiceNameByPort(80)
    getServiceNameByPort("http")
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        