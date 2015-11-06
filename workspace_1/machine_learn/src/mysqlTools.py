#!/usr/bin/python
# coding=utf8

import MySQLdb

# 函数为数据库连接、关闭函数
def getConn(HOST, USERNAME, PASSWORD, DB, PORT):
    return MySQLdb.connect(host=HOST, user=USERNAME, passwd=PASSWORD, db=DB, port=PORT) #, charset="utf8")

def getCursors(conn, n=1):
    if n == 1:
        return conn.cursor()  # 注意n=1一定要单独拿出来讨论，不然会被包装为tuple，使得后面的initializeCursors出问题
    cursors = []
    while n >= 1:
        cursors.append(conn.cursor())
        n -= 1
    return tuple(cursors)

def initializeCursors(*cursors):
    for cur in cursors:
        cur.execute("SET NAMES 'UTF8'")
        cur.execute("SET CHARACTER SET UTF8")
        cur.execute("SET CHARACTER_SET_RESULTS=UTF8")
        cur.execute("SET CHARACTER_SET_CONNECTION=UTF8")

def closeConns(*conns):
    for conn in conns:
        conn.close()

def closeCursors(*cursors):
    for cursor in cursors:
        cursor.close()
