#!/usr/bin/python
#encoding=utf-8

from atbtools.header import * 
from atbtools.mysqlTools import *
from atbtools.computeTools import *
from atbtools.spiderTools import *
import chardet
import xlrd
import xlwt
import xlutils.copy

#定义文本格式
def set_style(name, height, pattern_fore_colour, bold=False):
    style = xlwt.XFStyle() # 初始化样式
    
    font = xlwt.Font() # 为样式创建字体
    font.name = name # 'Times New Roman'
    font.bold = bold
    font.color_index = 4
    font.height = height
    
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    alignment.vert = xlwt.Alignment.VERT_CENTER
    
    pattern = xlwt.Pattern()
    pattern.pattern_fore_colour = pattern_fore_colour
    # borders= xlwt.Borders()
    # borders.left= 6
    # borders.right= 6
    # borders.top= 6
    # borders.bottom= 6
    
    style.font = font
    style.alignment = alignment
    style.pattern = pattern
    # style.borders = borders
    
    return style   
  
if __name__ == '__main__':
    
    srcdb_F = "platform_qualitative_F"

    conn_db = getConn(DBHOST, USERNAME, PASSWORD, DB, PORT)
    cur_db = getCursors(conn_db)
    initializeCursors(cur_db)
    
    in_file = xlrd.open_workbook('in.xls', formatting_info=True)
    in_sheet = in_file.sheet_by_index(0)
    row_number = in_sheet.nrows
    column_index = 0
    platform_name_list_in = []
    for i in range(row_number):
        platform_name_list_in.append(in_sheet.cell_value(i, column_index).encode("utf-8"))
    platform_name_list_F = getDifferentFieldlist(srcdb_F, cur_db, "platform_name")
    platform_name_list = list(set(platform_name_list_in) & set(platform_name_list_F))
    index_field = []
    for i in range(len(platform_name_list_in)):
        platform_name = platform_name_list_in[i]
        if platform_name in platform_name_list_F:
            index_field.append(i)
            
    out_file = xlutils.copy.copy(in_file)
    out_sheet = out_file.get_sheet(0)   
    for index in index_field:
        print index
        out_sheet.write(index, 1, 1)
    out_file.save('out.xls')
    
    closeCursors(cur_db)
    closeConns(conn_db)  