# /usr/bin/python
# coding=utf8

import os
from time import time
import re
import win32com.client as win32
import xlwt

circle_no = '\xe2\x97\x8b'
circle_yes = '\xe2\x8a\x99'
square_no = '\xe2\x96\xa1'
square_yes = '\xe2\x88\x9a'
char_length = len(circle_no)
blank = "xc2\xa0"

#从字符串中通过特征值查询所需要的字符串
def extractor(_content, _char_special):
    char_number = len(_char_special)
    index_start = 0
    for i in range(char_number):
        try: 
            result = _content[index_start:].find(_char_special[i])
        except:
            return (None, None)
        if result == -1:
            return (None, None)
        if i == char_number - 1:
            return (_content[index_start:index_start + result], _content[(index_start + result + len(_char_special[i])):])
        index_start += result + len(_char_special[i])

#找出用户选择的项                                    
def chooseYes(_str):
    if circle_no in _str:
        _yes = circle_yes
        _no = circle_no
    if square_no in _str:
        _yes = square_yes
        _no = square_no
    _list = re.split(_yes + "|" + _no, _str)
    value = _list[0]
    for text in _list[1:]:
        index = _str.index(text)
        if _str[index - char_length : index] == _yes:
            value += _yes + text
    return value

#清除字符串中的格式符号
def cleanStr(_str):
    value = _str
    value = re.subn('^\n+', '', value)[0]        
    value = re.subn('^\r+', '', value)[0]
    value = re.subn('^(\xc2\xa0)+', '', value)[0]
    value = re.subn('^\s+', '', value)[0]
    value = re.subn('\n+', '\n', value)[0]
    value = re.subn('\n+$', '', value)[0]
    return value         

#定义excel文本格式
def set_style(name, height, pattern_fore_colour, bold = False, wrap = False):
    style = xlwt.XFStyle() # 初始化样式
    
    font = xlwt.Font() # 为样式创建字体
    font.name = name # 'Times New Roman'
    font.bold = bold
    font.color_index = 4
    font.height = height
    
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    alignment.vert = xlwt.Alignment.VERT_CENTER
    if wrap != False:
        alignment.wrap = xlwt.Alignment.SHRINK_TO_FIT
    
    pattern = xlwt.Pattern()
    pattern.pattern_fore_colour = pattern_fore_colour
    borders= xlwt.Borders()
    borders.left= 1
    borders.right= 1
    borders.top= 1
    borders.bottom= 1
    
    style.font = font
    style.alignment = alignment
    style.pattern = pattern
    style.borders = borders
    
    return style

#返回windows文字
def getWinWord(_str):
    return _str.decode("UTF-8").encode("GB2312")

if __name__ == '__main__': 
    
    _start_time = time()
    style_1 = set_style('Times New Roman', 240, 3, True, True)
    style_2 = set_style('Times New Roman', 220, 3, True, True)
    style_3 = set_style('Times New Roman', 200, 3, True, True)
    style_4 = set_style('Times New Roman', 200, 3, False, True)
    style_5 = set_style('Times New Roman', 200, 3, False, True)
    
    field_list = ["ID", "保证人名称", "对应合同编号", "（一）本次检查时间、地点、走访单位、主要接待人员", "（二）收集、查阅资料", "（三）本行结算流水、存款情况", "情况说明", "（四）保证人银行授信及或有负债情况", "是否有违约记录情况(必输项)", "如有违约记录情况，请详细分析说明", "是否有或有负债", "或有负债对象及规模", "或有负债风险分析", "1、宏观经济政策变动", "2、对受信人经营是否存在影响（人工单选）", "具体情况说明", "1、保证人重大经营事件 ", "2、对保证人偿债能力是否存在影响（人工单选）", "具体情况说明", "", "如有，则详细说明"]
    field_number = len(field_list)
    
    #遍历所有word文档（置顶文件夹名称）
#     word_folder = "folder"
#     result_excel_file = "result.xls"
#     word_folder_abspath = os.path.abspath(word_folder)
#     word_list = os.listdir(word_folder)
#     word_list = [word_folder_abspath + "\\" + word_name for word_name in word_list if not word_name.startswith("~") and (word_name.endswith("doc") or word_name.endswith("docx"))]
#     word_number = len(word_list)

    #遍历所有word文档（默认当前文件夹名称）
    word_folder_abspath = os.getcwd()
    result_excel_file = "result.xls"
    word_list = os.listdir(word_folder_abspath)
    word_list = [word_folder_abspath + "\\" + word_name for word_name in word_list if not word_name.startswith("~") and (word_name.endswith("doc") or word_name.endswith("docx"))]
    word_number = len(word_list)
    
    _str = "共有" + str(word_number) + "个文档需要处理."
    print getWinWord(_str)
    print 
    
    #准备excel文件
    out_file = xlwt.Workbook(encoding = 'UTF-8')
    out_sheet1 = out_file.add_sheet("sheet1", cell_overwrite_ok=True)
    for i in range(field_number):
        field = field_list[i]
        out_sheet1.write(2, i, field, style_3)
    out_sheet1.write_merge(0, 1, 3, 12, "一 保证人基本情况分析", style_1)
    out_sheet1.write_merge(0, 0, 13, 20, "二、保证人经营情况分析", style_1)
    out_sheet1.write_merge(1, 1, 13, 14, "（一）宏观经济变动对保证人经营是否有影响", style_2)
    out_sheet1.write_merge(1, 1, 16, 18, "（二）保证人有无重大经营事件发生", style_2)
    out_sheet1.write_merge(1, 1, 19, 20, "（三）特别事项说明", style_1)
    out_sheet1.write_merge(0, 2, 21, 21, "三、保证人检查结论", style_1)
    out_sheet2 = out_file.add_sheet("sheet2", cell_overwrite_ok=True)
    out_sheet2.write_merge(0, 0, 1, 6, "（四）保证人银行授信及或有负债情况", style_1)
    out_sheet2.write_merge(0, 0, 8, 13, "或有负债对象及规模", style_1)

    #初始环境设置
    word = win32.Dispatch("Word.Application")
    word.Visible = 0
    word.DisplayAlerts = 0
    count = 0
    
    #遍历所有word并存入excel中
    error_list = []
    for word_name in word_list:
        try:
            count += 1
            word_name_short = word_name[word_name.rfind("\\") + 1:]
            print str(count) + "/" + str(word_number) + ": " + word_name_short
            doc = word.Documents.Open(word_name)
            table = doc.Tables(1)
            row_number = table.Rows.Count
            #递归至最内层表
            while(row_number == 1):
                table = table.Tables(1)
                row_number = table.Rows.Count
            
            #将所有的有限行保存至列表中
            text_list = []
            for i in range(1, row_number + 1):
                text = table.Cell(Row = i, Column= 1).Range.Text.replace("\x07","").replace("\x0b", "").replace("\r", "\n")
                text = text.encode("UTF-8")
                text_list.append(text)
                if "（四）保证人银行授信及或有负债情况" in text:
                    bank_credit = i + 1
                    table_small = table.Cell(Row = bank_credit, Column= 1).Tables
                    table_small_number = len(table_small)
                    bank_credit_table = table_small(table_small_number)
                if "或有负债对象及规模：" in text:
                    liability_object = i
                    table_small = table.Cell(Row = liability_object, Column= 1).Tables
                    table_small_number = len(table_small)
                    liability_object_table = table_small(table_small_number)
            
            #逐行进行处理    
            text_number = len(text_list)
            v = {}
            for i in range(text_number):
                this_text = text_list[i]
                if i < text_number - 1:
                    next_text = text_list[i + 1]
                if "保证人名称：" in this_text:
                    v[1] = extractor(this_text, "保证人名称：")[1]
                if "对应合同编号：" in this_text:
                    v[2] = extractor(this_text, "对应合同编号：")[1]
                if "（一）本次检查时间、地点、走访单位、主要接待人员：" in this_text:
                    v[3] = next_text
                if "（二）收集、查阅资料：" in this_text:
                    v[4] = next_text
                if "（三）本行结算流水、存款情况：" in this_text:
                    temp = extractor(this_text, ["（三）本行结算流水、存款情况："])[1]
                    v[5] = chooseYes(temp)
                    v[6] = extractor(next_text, ["情况说明："])[1]
                if "（四）保证人银行授信及或有负债情况" in this_text:
                    v[7] = ""
                    next_text = text_list[i + 2]
                    v[8] = extractor(next_text, ["是否有违约记录情况：(必输项)", "如有违约记录情况，请详细分析说明："])[0]
                    v[9] = extractor(next_text, ["如有违约记录情况，请详细分析说明："])[1]
                    next_text = text_list[i + 3]
                    temp = extractor(next_text, ["是否有或有负债：", "（如果选择有，必须输入内容）"])[0]
                    v[10] = "是否有或有负债：" + chooseYes(temp)
                    next_text = text_list[i + 3]
                    v[11] = ""
                    v[12] = extractor(next_text, ["或有负债风险分析："])[1]
                if "（一）宏观经济变动对保证人经营是否有影响：(必输项)" in this_text:
                    next_text = text_list[i + 1]
                    temp = extractor(next_text, ["1、宏观经济政策变动：", "2、对受信人经营是否存在影响（人工单选）："])[0]
                    v[13] = chooseYes(temp)
                    temp = extractor(next_text, ["2、对受信人经营是否存在影响（人工单选）：", "具体情况说明："])[0]
                    v[14] = chooseYes(temp)
                    v[15] = extractor(next_text, ["具体情况说明："])[1]
                if "（二）保证人有无重大经营事件发生：(必输项)" in this_text:
                    next_text = text_list[i + 1]
                    temp = extractor(next_text, ["1、保证人重大经营事件：", "2、对保证人偿债能力是否存在影响（人工单选）："])[0]
                    v[16] = chooseYes(temp)
                    temp = extractor(next_text, ["2、对保证人偿债能力是否存在影响（人工单选）：", "具体情况说明："])[0]
                    v[17] = chooseYes(temp)
                    v[18] = extractor(next_text, ["具体情况说明："])[1]
                if "（三）特别事项说明：" in this_text:
                    temp = extractor(this_text, ["（三）特别事项说明："])[1]
                    v[19] = chooseYes(temp)
                    v[20] = extractor(next_text, ["如有，则详细说明："])[1]
                if "三、保证人检查结论" in this_text:
                    v[21] = next_text
            v[0] = count
            key_number = len(v)
            for i in range(key_number):
                out_sheet1.write(2 + count, i, v[i], style_4)
            
            #对两个Table进行处理 
            row_number_1 = bank_credit_table.Rows.Count
            column_number_1 = bank_credit_table.Columns.Count
            
            line_number = 1 + (row_number_1 + 1) * (count - 1)
            out_sheet2.write_merge(line_number, line_number + row_number_1 - 1, 0, 0, v[1], style_5)
            for i in range(1, row_number_1 + 1):
                text_list = []
                for j in range(1, column_number_1 + 1):
                    try:
                        text = bank_credit_table.Cell(Row = i, Column= j).Range.Text.replace("\x07","").replace("\x0b", "").replace("\r", "\n")
                        text = text.encode("UTF-8")
                        text = cleanStr(text)
                        text_list.append(text)
                    except:
                        pass
                text_number = len(text_list)
                line_number = 1 + (row_number_1 + 1) * (count - 1) + i - 1
                if i == 1:
                    out_sheet2.write(line_number, 1, text_list[0], style_2)
                    out_sheet2.write_merge(line_number, line_number, 2, 4, text_list[1], style_2)
                    out_sheet2.write_merge(line_number, line_number, 5, 6, text_list[2], style_2)
                else:
                    if i == 2:
                        _style = style_2
                    else:
                        _style = style_5
                    for j in range(text_number):
                        out_sheet2.write(line_number, j + 1, text_list[j], _style)
    
            row_number_2 = liability_object_table.Rows.Count
            column_number_2 = liability_object_table.Columns.Count
            for i in range(1, row_number_2 + 1):
                text_list = []
                for j in range(1, column_number_2 + 1):
                    try:
                        text = liability_object_table.Cell(Row = i, Column= j).Range.Text.replace("\x07","").replace("\x0b", "").replace("\r", "\n")
                        text = text.encode("UTF-8")
                        text = cleanStr(text)
                        text_list.append(text)
                    except:
                        pass
                text_number = len(text_list)
                line_number = 1 + (row_number_1 + 1) * (count - 1) + i
                if i == 1:
                    for j in range(text_number):
                        out_sheet2.write_merge(line_number - 1, line_number, j + 1 + column_number_1 + 1, j + 1 + column_number_1 + 1, text_list[j], style_2)
                else:
                    for j in range(text_number):
                        out_sheet2.write(line_number, j + 1 + column_number_1 + 1, text_list[j], style_5)
            doc.Close()
        except:
            error_list.append(word_name_short)
            _str = "文档有误，忽略."
            print getWinWord(_str)
    word.Quit()
    out_file.save(result_excel_file)
    
    error_file = open("err_list.txt", "w")
    for word_name in error_list:
        error_file.write(word_name + "\n")
    error_file.close()
    
    _end_time = time()
    print 
    _str = "全部完成."
    print getWinWord(_str)
    _str =  "共耗时 " + str(_end_time - _start_time) + " 秒."
    print getWinWord(_str)
    print 
    _str = "'result.xls'文件中记录了所有的输出结果."
    print getWinWord(_str)
    _str = "'err_list.txt'文件中记录了所有不符合标准模板的文件名." 
    print getWinWord(_str)
    print 
    content = raw_input(getWinWord("按回车键退出..."))
    if (content != ""):
        exit(0)