#!/bin/bash

if [ "$1" == "reset" ]
then
    arg="reset"
fi

_start=`date +%s`

echo "获得waiting list."
python getWaitingList.py $arg
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi

echo "List筛选."
python filtrateList.py $arg
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi

echo "指数计算."
python calculateIndex.py $arg
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi

echo "线性插值."
python f_LinearInsert.py
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi

echo "计算历史指标."
python calculateHistoryIndex.py
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`


echo "完成！用时${_runtime}秒。"
