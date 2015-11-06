#!/bin/bash

arg=$1

_a=`date +%s`
echo "校验xml文件..."
python checkXmlWeight.py -c
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi

echo "模型数值初始化 ... "
_start=`date +%s`
python initRedis.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
echo ""

echo "开始白名单计算..."
_start=`date +%s`
python RedisToMySQL.py -t 0
python getWhiteList.py
python initRedis.py -f
python initRedis.py -y
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
echo ""

echo "统计学参数合成 ... "
_start=`date +%s`
python computeStatis.py ${arg}
python RedisToMySQL.py -t 3
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！已时${_runtime}秒。"
echo ""

echo "平台指标分数计算 ... "
_start=`date +%s`
python computeE3.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
echo ""

echo "A_level策略计算 ... "
_start=`date +%s`
python alevel.py
python RedisToMySQL.py -t 4
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
#echo ""

echo "平台维度分数计算 ... "
_start=`date +%s`
python computeH.py ${arg}
python RedisToMySQL.py -t 5
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
echo ""

echo "平台纵向惩罚 ... "
_start=`date +%s`
python computePunish.py ${arg}
python RedisToMySQL.py -t 6
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
echo ""

echo "数据平滑处理 ... "
_start=`date +%s`
python computeSmooth.py ${arg}
python RedisToMySQL.py -t 7
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
echo ""

echo "计算平台级别 ... "
_start=`date +%s`
python computeRank.py ${arg}
python RedisToMySQL.py -t 8
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
echo ""

echo "计算平台展示信息 ... "
_start=`date +%s`
python computeView.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
echo ""

echo "计算平台排名 ... "
_start=`date +%s`
python computeSort.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
echo ""

echo "模型分析完毕"
echo ""
echo "向ddpt-data同步数据 ... "
_start=`date +%s`
python RedisToMySQL.py -t 9
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
echo ""

echo "计算按投保偏差 ... "
_start=`date +%s`
python computeDeviation.py origin
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
echo ""

echo "计算报告数据 ... "
_start=`date +%s`
python viewMobile.py ${arg}
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
echo ""

echo "展示数据拼装 ... "
_start=`date +%s`
python viewE2Bad.py
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
echo ""

echo "生成报告配置 ... "
_start=`date +%s`
python viewReport.py
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
echo ""

echo "缓存索引生成 ... "
_start=`date +%s`
python viewCache.py
if [ $? -ne 0 ]
then
    echo "失败！"
    exit 1
fi
_end=`date +%s`
_runtime=`expr $_end - $_start`
echo "完成！用时${_runtime}秒。"
echo ""

_b=`date +%s`
_r=`expr $_b - $_a`
echo "总用时${_r}秒。"
