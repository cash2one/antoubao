# /usr/bin/python
# encoding=utf-8

import time
import random
import urllib2
import urllib
import json
import os
from atbtools.spiderTools import *
from atbtools.computeTools import *
        
if __name__ == '__main__':
    _start_time = time.time() 
    html = getHtml("http://www.daichuqu.com/Search")
    html = extractor(html, ['<ul class="clearfix lhptlist" id="myList">'])[1]
    count = 0
    pinyin = PinYin()
    pinyin.load_word()
    while True:
        (platform_str, html) = extractor(html, ['title=','data=','</h2>'])
        if None == platform_str:
            break
        picture_src = extractor(platform_str,['"', '"'])[0]
        platform_name = extractor(platform_str,["<h2>"])[1]
        if picture_src == None or picture_src == "":
            continue
        count += 1
        platform_name = delBlank(platform_name).decode("utf-8") #先转化为unicode代码
        folder_name = pinyin.hanzi2pinyin(platform_name)[0][0]
        if folder_name in "0123456789":
            folder_name = "0-9"
        else:
            folder_name = folder_name.upper()
        if False == os.path.exists("picture\\" + folder_name):
            os.mkdir("picture\\" + folder_name)
        picture_src = "http://www.daichuqu.com" + picture_src
        filename = "picture\\" + folder_name + "\\" + platform_name + ".png"
        print str(filename)
        if os.path.exists(filename):
            continue
        fp = open(filename, "wb")
        img = getHtml(picture_src)
        fp.write(img)
        fp.close()
    print "一共有" + str(count) + "个平台."
    print ""
    print "finished"
    _end_time = time.time()
    print "The whole program costs " + str(_end_time - _start_time) + " seconds."
    
    "<h2><strong>基础资料</strong></h2>"