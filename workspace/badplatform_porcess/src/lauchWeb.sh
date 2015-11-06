#!/bin/bash

_sleeptime=10
function runPython(){
	echo "########################################################################"
	_start=`date +%s`
	python $1
	if [ $? -ne 0 ]
	then
		echo "$1 失败！"
		exit 1
	fi
	_end=`date +%s`
	_runtime=`expr $_end - $_start`
	echo "完成！用时${_runtime}秒。"
	echo "########################################################################"
	echo ""
	sleep $_sleeptime
}

echo "开始备份..."
runPython backupTables.py

echo "开始上传..."
runPython uploadTables.py

echo "关闭gateway..."
#expect restartGateway.exp

echo "上线完毕!"
echo "请报告给韩总和罗粒检查."
