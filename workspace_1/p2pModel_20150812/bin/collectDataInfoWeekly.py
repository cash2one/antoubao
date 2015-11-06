#!/usr/bin/python
#encoding=utf-8

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from atbtools.spiderTools import *
import xlrd
import xlwt
import xlutils.copy

#定义文本格式
def set_style(name,height,bold=False):
    style = xlwt.XFStyle() # 初始化样式
    
    font = xlwt.Font() # 为样式创建字体
    font.name = name # 'Times New Roman'
    font.bold = bold
    font.color_index = 4
    font.height = height
    
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    alignment.vert = xlwt.Alignment.VERT_CENTER
    
    # borders= xlwt.Borders()
    # borders.left= 6
    # borders.right= 6
    # borders.top= 6
    # borders.bottom= 6
    
    style.font = font
    style.alignment = alignment
    # style.borders = borders
    
    return style

#讲xlrd的merge格式改成xlwt的merge格式  
def changeXlrd2Xlwt(_index_list):
    return _index_list[0], _index_list[1] - 1, _index_list[2], _index_list[3] - 1   
  
if __name__ == '__main__':
    srcdb_Y = "total_status"
    srcdb_VIEW_MOBILE = "view_mobile"
    srcdb_V = "V_view"
    srcdb_E1 = "platform_quantitative_data_E1"
    srcdb_A = "platform_quantitative_wdzj_weekly_A"
    srcdb_B = "platform_quantitative_dcq_weekly_B"

    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    conn_ddpt = getConn(DDPT_DATAHOST, USERNAME, PASSWORD, DB, PORT)
    cur_ddpt = getCursors(conn_ddpt)
    conn_dev = getConn(DEVHOST, USERNAME, PASSWORD, DB, PORT)
    cur_dev = getCursors(conn_dev)
    initializeCursors(cur_db, cur_ddpt, cur_dev)
    
    
    total_dict = {}
    total_dict["时间戳"] = {}
    total_dict["时间戳"]["order"] = 1
    total_dict["时间戳"]["child"] = []
    
    total_dict["抓站个数"] = {}
    total_dict["抓站个数"]["order"] = 2
    total_dict["抓站个数"]["child"]["从表A抓取"] = []
    total_dict["抓站个数"]["child"]["从表B抓取"] = []
    total_dict["抓站个数"]["child"]["最终排名个数"] = []
    
    total_dict["本周不同级别的站的个数为(括号内为各级别设置的百分位)"] = {}
    total_dict["本周不同级别的站的个数为(括号内为各级别设置的百分位)"]["order"] = 3
    total_dict["本周不同级别的站的个数为(括号内为各级别设置的百分位)"]["child"]["A++"] = []
    total_dict["本周不同级别的站的个数为(括号内为各级别设置的百分位)"]["child"]["A+"] = []
    total_dict["本周不同级别的站的个数为(括号内为各级别设置的百分位)"]["child"]["A"] = []
    total_dict["本周不同级别的站的个数为(括号内为各级别设置的百分位)"]["child"]["B++"] = []
    total_dict["本周不同级别的站的个数为(括号内为各级别设置的百分位)"]["child"]["B+"] = []
    total_dict["本周不同级别的站的个数为(括号内为各级别设置的百分位)"]["child"]["B"] = []
    total_dict["本周不同级别的站的个数为(括号内为各级别设置的百分位)"]["child"]["C"] = []
    
    total_dict["本周坏站的个数"] = {}
    total_dict["本周坏站的个数"]["order"] = 4
    total_dict["本周坏站的个数"]["child"] = []
    
    total_dict["本周坏站被评为A及A以上个数"] = {}
    total_dict["本周坏站被评为A及A以上个数"]["order"] = 5
    total_dict["本周坏站被评为A及A以上个数"]["child"] = []
    total_dict["每周升上A的平台（平台名/现级别/原级别/提升名次）"] = {}
    total_dict["每周升上A的平台（平台名/现级别/原级别/提升名次）"]["order"] = 6
    total_dict["每周升上A的平台（平台名/现级别/原级别/提升名次）"]["child"] = ["number"]
    total_dict["每周降下A的平台（平台名/现级别/原级别/下降名次）"] = {}
    total_dict["每周降下A的平台（平台名/现级别/原级别/下降名次）"]["order"] = 7
    total_dict["每周降下A的平台（平台名/现级别/原级别/下降名次）"]["child"] = ["number"]
    total_dict["本周黑名单（平台名/状态）"] = {}
    total_dict["本周黑名单（平台名/状态）"]["order"] = 8
    total_dict["本周黑名单（平台名/状态）"]["child"] = ["number"]
    total_dict["本周人工降分策略（平台名/评级）"] = {}
    total_dict["本周人工降分策略（平台名/评级）"]["order"] = 9
    total_dict["本周人工降分策略（平台名/评级）"]["child"] = ["number"]
    total_dict["本周坏站被锁定（平台名/级别）"] = {}
    total_dict["本周坏站被锁定（平台名/级别）"]["order"] = 10
    total_dict["本周坏站被锁定（平台名/级别）"]["child"] = ["number"]
    index_list = sortDictByKeyValue(total_dict, "order")[0]
    index_list.sort(reverse = True)
    print index_list
    #预处理
    in_file = xlrd.open_workbook('dataWeekly.xls', formatting_info=True)
    in_sheet = sheet2 = in_file.sheet_by_index(0)
    #备份
    backup_file = xlutils.copy.copy(in_file)    
    backup_file.save('dataWeekly_backup.xls')
    print in_sheet.merged_cells
    out_file = xlwt.Workbook()
    sheet1 = out_file.add_sheet(u'sheet1',cell_overwrite_ok=True)
    index_dict = {}
    for index_list in in_sheet.merged_cells:
        word = sheet2.cell_value(index_list[0],index_list[2])
        index_dict[word] = index_list
    for word in index_dict:
        (a, b, c, d) = changeXlrd2Xlwt(index_dict[word])
        print word, a,b,c,d
        sheet1.write_merge(a, b, c, d, word, set_style('Times New Roman',220,False))
    initial_timestamp = 1438444800
    date_list = getDifferentFieldlist(srcdb_V, cur_ddpt, "date")
    this_date = date_list[-1]
    date_list = range(initial_timestamp, this_date + 1, SECONDSPERWEEK)
    
    for date in date_list:
        
    
    
    last_date = date_list[-2]
    initial_column = 2
    this_column = initial_column + (this_date - initial_timestamp) / SECONDSPERWEEK
    out_file.save("dataWeekly_new.xls")
    exit(0)
    info_file = open("info.txt", "w")
    _string = "本周的时间戳为" + str(this_date) + "(" + time.strftime("%Y-%m-%d", time.localtime(this_date)) + ")" 
    print _string 
    info_file.write(_string + "\n")
    print 
    info_file.write("\n")
    
    #本周信息汇总
    #1.站的个数
    A_number = getNumberFromFieldByDate(srcdb_A, cur_db, this_date)
    B_number = getNumberFromFieldByDate(srcdb_B, cur_db, this_date)
    _string = "本周从表A抓取的站的个数为" + str(A_number) + "." 
    print _string 
    info_file.write(_string + "\n")
    _string = "本周从表B抓取的站的个数为" + str(B_number) + "." 
    print _string 
    info_file.write(_string + "\n")
    all_number = getNumberFromFieldByDate(srcdb_VIEW_MOBILE, cur_dev, this_date)
    _string = "本周进入最终排名的站的个数为" + str(all_number) + "." 
    print _string 
    info_file.write(_string + "\n")
    print 
    info_file.write("\n")
    
    #2.不同级别的站的个数
    level_percent_dict = {}.fromkeys(LEVEL_LIST, 0)
    fp = open("computeRank.py", "r")
    for line in fp:
        if "np.percentile(scoreRange" in line:
            level = extractor(line, ["\"", "\""])[0]
            level_percent_dict[level] = float(eval(extractor(line, ["percentile(scoreRange,", ")"])[0]))
        
    fp.close()
    level_dict = {}.fromkeys(LEVEL_LIST, 0)
    stringSQL = "SELECT `level` FROM " + srcdb_VIEW_MOBILE + " WHERE `date` = '" + str(this_date) + "'"
    cur_dev.execute(stringSQL)
    for level in cur_dev.fetchall():
        level_dict[level[0]] += 1
    _string = "本周不同级别的站的个数为(括号内为各级别设置的百分位)：" 
    print _string 
    info_file.write(_string + "\n")
    for level in LEVEL_LIST:
        _string = level + "(" + str(level_percent_dict[level]) + "): " + str(level_dict[level])
        print _string 
        info_file.write(_string + "\n") 
    print 
    info_file.write("\n")
    
    #3.坏站个数
    stringSQL = "SELECT `platform_id`, `platform_name`, `status` FROM " + srcdb_VIEW_MOBILE + " WHERE `date` = '" + str(this_date) + "' AND `status` < 0.89" 
    cur_dev.execute(stringSQL)
    bad_platform_dict = {}
    bad_number = 0
    for platform_id, platform_name, status in cur_dev.fetchall():
        bad_number += 1
        if status in ["A++", "A+", "A"]:
            bad_platform_dict[platform_id] = {} 
            bad_platform_dict[platform_id]["platform_name"] = platform_name 
            bad_platform_dict[platform_id]["status"] = status 
        
    _string = "本周坏站的个数为" + str(bad_number) + "."
    print _string 
    info_file.write(_string + "\n")
    bad_aboveA_number = len(bad_platform_dict)
    if bad_aboveA_number == 0:
        _string = "本周并没有坏站被评为A及A以上."
        print _string 
        info_file.write(_string + "\n")
    else:
        _string = "本周有" + str(bad_aboveA_number) + "个坏站的级别在A及A以上，它们是："
        print _string 
        info_file.write(_string + "\n")
        for platform_id in bad_platform_dict:
            _string = platform_id + "(" + bad_platform_dict[platform_id]["platform_name"] + "): " + bad_platform_dict[platform_id]["status"]
            print _string 
            info_file.write(_string + "\n")
    print 
    info_file.write("\n")
            
    fp = open("header.py", "r")
    count = 0
    pos = 0
    badlevel_str_list = []
    hehePunish = {}
    BLACKLIST = []
    BADLEVEL = {}
    for line in fp:
        count += 1
        if "hehePunish" in line:
            exec(line)
        if "BLACKLIST" in line:
            exec(line)
        if "BADLEVEL" in line:
            pos = count
            badlevel_str_list.append(line)
        if count > pos:
            badlevel_str_list.append(line)
            if "}" in line:
                exec("".join(badlevel_str_list))
                break
    fp.close()
    
    #获得所有的黑名单
    black_number = len(BLACKLIST)
    if black_number == 0:
        _string = "本周黑名单为空." 
        print _string 
        info_file.write(_string + "\n")
    else:
        _string = "本周黑名单一共有" + str(black_number) + "个平台，他们的status分别为：" 
        print _string 
        info_file.write(_string + "\n")
        for platform_id in BLACKLIST:
            stringSQL = "SELECT `platform_name` FROM " + srcdb_Y + " WHERE `platform_id` = '" + platform_id + "'"
            ret = cur_db.execute(stringSQL)
            if ret == 0:
                _string = "不存在'" + platform_id + "'这个platform_id名称." 
                print _string 
                info_file.write(_string + "\n")
            else:
                platform_name = cur_db.fetchone()[0]
                stringSQL = "SELECT `status` FROM " + srcdb_Y + " WHERE `platform_id` = '" + platform_id + "'"
                ret = cur_db.execute(stringSQL)
                if ret != 0 :
                    status = cur_db.fetchone()[0]
                else:
                    status = None
                _string = platform_id + "(" + platform_name + "): " + str(status)
                print _string 
                info_file.write(_string + "\n")
    print 
    info_file.write("\n")    
    
    #获得所有的降级策略
    punish_dict_number = len(hehePunish)
    if punish_dict_number == 0:
        _string = "本周没有人工降分策略为空." 
        print _string 
        info_file.write(_string + "\n")
    else:
        _string = "本周有" + str(punish_dict_number) + "个人工降分策略，它们的最终评级为：" 
        print _string
        info_file.write(_string + "\n")
        for platform_id in hehePunish:
            stringSQL = "SELECT `platform_name` FROM " + srcdb_Y + " WHERE `platform_id` = '" + platform_id + "'"
            ret = cur_db.execute(stringSQL)
            if ret == 0:
                _string = "不存在'" + platform_id + "'这个platform_id名称." 
                print _string 
                info_file.write(_string + "\n")
            else:
                platform_name = cur_db.fetchone()[0]
                del_score = hehePunish[platform_id]
                del_score *= -1
                if del_score < 0 :
                    del_score = str(del_score)
                else:
                    del_score = "+" + str(del_score)
                stringSQL = "SELECT `level` FROM " + srcdb_VIEW_MOBILE + " WHERE `platform_id` = '" + platform_id + "' AND `date` = '" + str(this_date) + "'" 
                ret = cur_dev.execute(stringSQL)
                if ret == 0:
                    level = None
                else:
                    level = cur_dev.fetchone()[0]
                _string = platform_id + "(" + platform_name + ")(" + del_score + "): "  + str(level)
                print _string 
                info_file.write(_string + "\n")
    print 
    info_file.write("\n") 
    
    #坏站级别锁定
    bad_dict_number = len(BADLEVEL)
    bad_dict = {}
    if bad_dict_number == 0:
        _string = "本周没有坏站的级别被锁定." 
        print _string 
        info_file.write(_string + "\n")
    else:
        _string = "本周有" + str(bad_dict_number) + "个坏站的级别被锁定，分别为：" 
        print _string
        info_file.write(_string + "\n")
        for platform_id in BADLEVEL:
            stringSQL = "SELECT `platform_name` FROM " + srcdb_Y + " WHERE `platform_id` = '" + platform_id + "'"
            ret = cur_db.execute(stringSQL)
            if ret == 0:
                _string = "不存在'" + platform_id + "'这个platform_id名称." 
                print _string 
                info_file.write(_string + "\n")
            else:
                _string = platform_id + "(" + cur_db.fetchone()[0] + "): " + BADLEVEL[platform_id]
                print _string 
                info_file.write(_string + "\n")
    
    closeCursors(cur_db, cur_dev)
    closeConns(conn_db, conn_dev)  