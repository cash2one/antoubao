#!/usr/bin/python
# coding=utf8

from header import *
from mysqlTools import *

if __name__ == '__main__':
    TABLE_NAME = "antoubao"
    conn = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur = getCursors(conn)
    initializeCursors(cur)
    
    stringSQL = "select table_name,column_name,data_type from information_schema.columns where `table_schema` = '" + TABLE_NAME + "' order by table_name,ordinal_position"
    cur.execute(stringSQL)
    fp = open("./Fields.txt", 'w')
    tables={}
    for table_name, column_name, data_type in cur.fetchall():
        if table_name not in tables:
            tables[table_name]={}
            tables[table_name]["column_name"]=[]
            tables[table_name]["data_type"]=[]
        tables[table_name]["column_name"].append(column_name)
        tables[table_name]["data_type"].append(data_type)
        fp.write("[" + table_name + "]" + column_name +"(" + data_type + "): \n")
    fp.close()
    for table_name in tables:
        fp = open("Fields/" + str(table_name) +".txt", 'w')
        fp.write(table_name+" ")
        for i in range(0,len(tables[table_name]["column_name"])):
            fp.write(tables[table_name]["column_name"][i] +"(" + tables[table_name]["data_type"][i] + ") ")
        fp.write("\n")
        fp.close()
