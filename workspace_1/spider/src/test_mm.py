# /usr/bin/python
# encoding=utf8

import time
import random
import urllib2
import urllib
import json
import os

def openURL(url):
    request = urllib2.Request(url)
    request.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36")
    try:
        response = urllib2.urlopen(request)
    except urllib2.URLError, e:
        if hasattr(e,"code"):
            print e.code
        if hasattr(e,"reason"):
            print e.reason
    else:
        print "OK"
    html = response.read()
    return html

def getPage(url):
    html = openURL(url).decode("utf-8")
    a = html.find("current-comment-page") + 23
    b = html.find("]", a)
    return html[a:b]

def find_imgs(url):
    html = openURL(url).decode("utf-8")
    img_addrs = []
    a = html.find("img src=")
    while a != -1:
        b = html.find(".jpg",a,a+150)
        if b != -1:
            img_addrs.append(html[a+9:b+4])
        else:
            b = a + 9
        a = html.find("img src=", b)
    return img_addrs

def save_imgs(floder, img_addrs):
    for each in img_addrs:
        filename = each.split("/")[-1]
        with open(filename, "wb") as f:
            img = openURL(each)
            f.write(img)
    
def downloadMM(folder = "ooxx", pages = 2):
    os.mkdir(folder)
    os.chdir(folder)
    url = "http://jandan.net/ooxx/"
    page_num = int(getPage(url))
    
    for i in range(pages):
        page_num -= i
        page_url = url + "page-" + str(page_num) + "#comments"
        img_addrs = find_imgs(page_url)
        save_imgs(folder, img_addrs)
        
if __name__ == '__main__':
    _start_time = time.time() 
    downloadMM()
    
    print ""
    print "finished"
    _end_time = time.time()
    print "The whole program costs " + str(_end_time - _start_time) + " seconds."
    