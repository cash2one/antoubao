#!/bin/bash

if [ "$1" == "reset" ]
then
    arg="reset"
fi

_start=`date +%s`
echo -n "开始计算：本周列表初始化[PlatformId] ... "
python computePlatformId.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"

echo -n "开始计算：宽口径数据梳理[E1] ... "
_start=`date +%s`
python computeTableE1.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"

echo -n "开始计算：缺口数据估值[E1patch] ... "
_start=`date +%s`
python computeTableE1patch.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"

#echo -n "开始计算：问题平台库刷新[Y] ... "
#_start=`date +%s`
#python computeTableY.py ${arg}
#if [ $? -ne 0 ]
#then
#    echo "失败！"
#    exit 1
#fi
#_end=`date +%s`
#_runtime=`expr $_end - $_start`
#echo "完成！用时${_runtime}秒。"

echo -n "开始计算：异常数据遴选[BLACKLIST] ... "
_start=`date +%s`
python filterDataSource.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
