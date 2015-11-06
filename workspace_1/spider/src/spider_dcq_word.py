# /usr/bin/python
# encoding=utf-8

import time
import random
import urllib2
import urllib
import json
import os
import re
from atbtools.spiderTools import *
from atbtools.computeTools import *

if __name__ == '__main__':
    _start_time = time.time() 
    #获得连接        
    conn = getConn("127.0.0.1", "xiebo", "123456", "antoubao", 3306)
    cur = getCursors(conn)
    initializeCursors(cur)
    
    SRCDB_A = "platform_qualitative_a"
    
    html = getHtml("http://www.daichuqu.com/Search")
    html = extractor(html, ['<ul class="clearfix lhptlist" id="myList">', "</ul>"])[0]
    count = 0
    platform_url_dict = {}
    while True:
        (platform_str, html) = extractor(html, ['><a href=',' target='])
        if None == platform_str:
            break
        platform_url = extractor(platform_str,['"', '"'])[0]
        platform_name = extractor(platform_str,['title="', '"'])[0]
        if platform_url == None or platform_name == None:
            continue
        platform_name = platform_name.decode("utf-8") #先转化为unicode代码
        platform_name = platform_name.encode("utf-8")
        platform_url_dict[platform_name] = platform_url
        count += 1
    print "一共有" + str(count) + "个平台."
    field1_dict = {}
    field1_dict["资本充足率"] = ["注册资本", "风险准备金", "融资状况"]
    field1_dict["控制人状况"] = ["法人及股东", "管理团队", "自融风险", "上线时间", "所在地域", "网站地址", "隶属公司", "网站备案主体"]
    field1_dict["产品类型"] = ["产品类型", "利息管理费"]
    field1_dict["垫付规则"] = ["垫付资格", "垫付时间"]
    field1_dict["流动性状况"] = ["债权转让", "充值提现限制", "充值费用", "提现费用", "自动投标"]
    field1_list = []
    for field in field1_dict:
        field1_list += field1_dict[field]
    field2_list = ["隶属公司", "备案号", "业务模式", "主要产品", "资金流向", "安全保障", "年化收益率", "流动性状况", "充值提现限制", "起投金额"]
    field2_length_dict = {x : len(x) for x in field2_list}
    field_list = list(set(field1_list) | set(field2_list))
    for field in field_list: 
        insertField(conn, cur, SRCDB_A, field, "VARCHAR(512) DEFAULT NULL")

    for platform_name in platform_url_dict:
        time.sleep(3)
        platform_url = platform_url_dict[platform_name]
        print platform_url
        html = getHtml(platform_url)
        if html == None:
            continue
        html = extractor(html, ['<h2><strong>基础资料</strong></h2>', '<div', '</div>'])[0]
        if html == None:
            continue
        if '资本充足率' in html:
            continue
            #先插入平台名
            _type = 1
            stringSQL="SELECT * FROM " + SRCDB_A + " WHERE `平台名称` = '" + platform_name + "'"
            ret = cur.execute(stringSQL)
            if ret == 0:
                stringSQL="INSERT INTO " + SRCDB_A + "(`平台名称`, `平台类型`, `平台网址`) VALUES('" + platform_name + "', '" + str(_type) + "', '" + platform_url + "')"
            else:
                stringSQL="UPDATE " + SRCDB_A + " SET `平台类型` = '" + str(_type) + "', `平台网址` = '" + platform_url + "' WHERE `平台名称` = '" + platform_name + "'"
            cur.execute(stringSQL)
            conn.commit() 
            #再插入定性属性
            key_value_list = []
            while True:
                (_str, html) = extractor(html, ["<section", "</h2>", "<dl><dt>", "</dd></dl></section>"])
                if None == _str:
                    break
                dl_str = _str.split("</dd></dl><dl><dt>")
                for dl in dl_str:
                    dd_str = dl.split("</dt><dd>")
                    field = dd_str[0]
                    value = dd_str[1]
                    if field in field1_list:
                        key_value_list.append("`" + field + "` = '" + value + "'")
            stringSQL="UPDATE " + SRCDB_A + " SET " + ",".join(key_value_list) + " WHERE `平台名称` = '" + platform_name + "'"
            cur.execute(stringSQL)
            conn.commit()
            
        elif '业务模式' in html:
            _type = 2
            stringSQL="SELECT * FROM " + SRCDB_A + " WHERE `平台名称` = '" + platform_name + "'"
            ret = cur.execute(stringSQL)
            if ret == 0:
                stringSQL="INSERT INTO " + SRCDB_A + "(`平台名称`, `平台类型`, `平台网址`) VALUES('" + platform_name + "', '" + str(_type) + "', '" + platform_url + "')"
            else:
                stringSQL="UPDATE " + SRCDB_A + " SET `平台类型` = '" + str(_type) + "', `平台网址` = '" + platform_url + "' WHERE `平台名称` = '" + platform_name + "'"
            cur.execute(stringSQL)
            conn.commit()
            #再插入定性属性
            (_str, html) = extractor(html, ["查看更多"])
            _str = delTag(_str)
            if _str == None:
                continue
            #获得已知标签在字符串中的位置
            field_index_dict = {}
            for field in field2_list:
                temp = _str.find(field)
                if temp != -1:
                    field_index_dict[field] = temp
            field_list_sorted, field_index_list_sorted = sortDictByValue(field_index_dict)
            field_list_sorted.reverse()
            field_index_list_sorted.reverse()
            field_sorted_number = len(field_list_sorted)
            key_value_list = []
            for i in range(field_sorted_number):
                field = field_list_sorted[i]
                start_index = field_index_list_sorted[i] + field2_length_dict[field]
                if i < field_sorted_number - 1:
                    end_index = field_index_list_sorted[i + 1]
                    value = _str[start_index:end_index]
                else:
                    value = _str[start_index:]
                value = value.replace("\r", "").replace("\t", "").replace("\t", "").replace("\t", "").replace(" ", "").replace("&nbsp", "").replace("；", ";")
                if value.startswith(":"):
                    value = value[len(":"):]
                if value.startswith("："):
                    value = value[len("："):]
                if value.startswith(";"):
                    value = value[len(";"):]
                value = re.subn('\n+$', '', value)[0]
                value = re.subn('^\n+', '', value)[0]
                value = re.subn('\n+', ';', value)[0]
                value = re.subn(';+', '；', value)[0]
                print field
                print value
                key_value_list.append("`" + field + "` = '" + value + "'")    
            stringSQL="UPDATE " + SRCDB_A + " SET " + ",".join(key_value_list) + " WHERE `平台名称` = '" + platform_name + "'"
            cur.execute(stringSQL)
            conn.commit()
            
    print ""
    print "finished"
    _end_time = time.time()
    print "The whole program costs " + str(_end_time - _start_time) + " seconds."