#!/bin/bash

if [ "$1" == "reset" ]
then
    arg="reset"
fi

cd score

echo -n "开始计算：核心数据库遴选[E2] ... "
_start=`date +%s`
python computeTableE2.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"

echo -n "开始计算：统计学参数合成[IJKLMNO] ... "
_start=`date +%s`
python computeTableIJKLMNO.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！已时${_runtime}秒。"

echo -n "开始计算：一级参数模块化[E3] ... "
_start=`date +%s`
python computeTableE3.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"

echo -n "开始计算：二级参数模块化[G] ... "
_start=`date +%s`
python computeTableG.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"

echo -n "开始计算：终端参数模块化[H] ... "
_start=`date +%s`
python computeTableH.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"

echo -n "开始计算：截断式参数反馈[P] ... "
_start=`date +%s`
python computeTableP.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"


echo -n "开始计算：非线性差值预警[Q1] ... "
_start=`date +%s`
#python computeAlertQ1.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"

echo -n "开始计算：历史平滑处理[S] ... "
_start=`date +%s`
python computeTableS.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"

echo -n "开始计算：关键值降级惩罚[T] ... "
_start=`date +%s`
python computeTableT.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"

echo -n "开始计算：推荐平台候选[U] ... "
_start=`date +%s`
#python computeTableU.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"

echo -n "开始计算：终端数据可视化[VIEW] ... "
cd ../view
_start=`date +%s`
python view.py
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"

echo -n "开始计算：多向度数据解读[ANNOTATION] ... "
_start=`date +%s`
python annotation.py
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"

echo -n "开始计算：问题平台解读[STATUS] ... "
_start=`date +%s`
python status.py
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
