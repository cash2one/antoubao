# /usr/bin/python
# encoding=utf8

import time
import random
import urllib2
import urllib
import json


if __name__ == '__main__':
    _start_time = time.time() 
    #response = urllib2.urlopen("http://www.fishc.com/")
    #print response.read().decode("utf-8")
    #response = urllib2.urlopen("http://placekitten.com/g/200/300")
#     req = urllib2.Request("http://placekitten.com/g/200/300")
#     response = urllib2.urlopen(req)
#     cat_img = response.read()
#     with open("cat_200_300.jpg","wb") as f:
#         f.write(cat_img)
#     print response.geturl()
#     print response.info()
#     print response.getcode()

    #url
    url = "http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=http://www.youdao.com/"
    url = "https://www.whatismyip.com/"
    #data
    data = {}
    data["type"]="AUTO"
    data["i"]="i love FishC.com"
    data["doctype"]="json"
    data["xmlVersion"]="1.8"
    data["keyfrom"]="fanyi.web"
    data["ue"]="UTF-8"
    data["action"]="FY_BY_CLICKBUTTON"
    data["typoResult"]="true"
    data = urllib.urlencode(data).encode("utf-8")
    #header
    head ={}
    head["User-Agent"] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36"
    #proxy: http://cn-proxy.com/
    enable_proxy = True
    iplist = ["124.254.57.150:8118", "124.202.169.54:8118"]#, "124.202.183.170:8118"]
    proxy_handler = urllib2.ProxyHandler({"http" : random.choice(iplist)})
    null_proxy_handler = urllib2.ProxyHandler({})
    if enable_proxy:
        opener = urllib2.build_opener(proxy_handler)
    else:
        opener = urllib2.build_opener(null_proxy_handler)
#     #给opener加header，不兼容，不用
#     opener.addheaders = ["User-Agent", "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36"]
    urllib2.install_opener(opener)
    #组装request(url,data,header)
    request = urllib2.Request(url, data, head)
    
    #申请网页
    response = urllib2.urlopen(request)
    html = response.read().decode("utf-8")
    print html
    target = json.loads(html)
    print target["translateResult"][0][0]["tgt"]
    
    
    print ""
    print "finished"
    _end_time = time.time()
    print "The whole program costs " + str(_end_time - _start_time) + " seconds."
    