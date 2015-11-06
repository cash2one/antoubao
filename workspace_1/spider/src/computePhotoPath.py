#!/use/bin/python
#coding=utf-8

import time
from atbtools.header import *
from atbtools.computeTools import *
import os
import chardet

if __name__ == "__main__":
    
    startTime = time.time()
    #获得连接        
    conn = getConn("127.0.0.1", "xiebo", "123456", "antoubao", 3306)
    cur = getCursors(conn)
    initializeCursors(cur)
    
    PHOTO = "wd_shuju"
    field_list = getAllColumnsFromTable(cur, PHOTO, del_list = ["Id"])

    stringSQL = "DELETE FROM " + PHOTO
    cur.execute(stringSQL)
    conn.commit()
    
    photo_dir = "picture"
    folder_list = os.listdir(photo_dir)
    for folder in folder_list:
        _dir = photo_dir + "/" + folder
        file_list = os.listdir(_dir)
        for _file in file_list:
            name = _file.decode("GBK")[:-4].encode("utf-8")
            picurl = photo_dir + "/" + folder + "/" + name + ".png"
            keyword =  str(folder)
            value_list = [name, picurl, keyword]
            stringSQL = "INSERT INTO " + PHOTO + " (`" + "`, `".join(field_list) + "`) VALUES('" + "', '".join(value_list) + "')"
            cur.execute(stringSQL)
            conn.commit()

    closeCursors(cur)
    closeConns(conn)        
    print ""
    print "finished"
    endTime = time.time()
    print "The whole program costs " + str(endTime - startTime) + " seconds."        