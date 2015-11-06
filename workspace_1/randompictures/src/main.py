#!/use/bin/python
#coding=utf-8

import matplotlib.pyplot as plt
import Image
import random

#返回随机区域index，注意只在第二个维度上进行随机
def getRandomBoxIndexList(row_nunmber,column_nunmber):
    box_list = []
    for i in range(row_nunmber):
        column_list = random.sample(range(column_nunmber),column_nunmber)
        for j in column_list:
            box_list.append([i,j])
    return box_list

#通过随机index_list和图片尺寸分出区域box_list
def getBoxListFromIndexList(box_index_list, img_size):
    (row_number, column_number) = max(box_index_list)
    row_number += 1
    column_number += 1
    (row_size, column_size) = img_size
    small_box_row = row_size / row_number
    small_box_column = column_size / column_number 
    box_list_initial = []
    for i in range(row_number):
        for j in range(column_number):
            box_list_initial.append([small_box_row * i, small_box_column * j, small_box_row * (i + 1), small_box_column * (j + 1)])
    box_list_new = []
    for box_index in box_index_list:
        box_list_new.append([small_box_row * box_index[0], small_box_column * box_index[1], small_box_row * (box_index[0]+1), small_box_column * (box_index[1] + 1)])
    return box_list_initial,box_list_new

if __name__ == '__main__':
    row_nunmber = 10
    column_nunmber = 10
    img = Image.open('test.jpg')        #读取图像
    img.show()
    img_size = img.size
    box_index_list = getRandomBoxIndexList(row_nunmber,column_nunmber)
    (box_list_initial, box_list_new) = getBoxListFromIndexList(box_index_list, img_size)
    img_new = Image.new("RGB", img_size)
    for i in range(len(box_list_initial)):
        img_part = img.crop(box_list_new[i])
        img_new.paste(img_part, box_list_initial[i])
    img_new.show()