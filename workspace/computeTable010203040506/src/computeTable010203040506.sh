#!/bin/bash

_start_whole_time=`date +%s`
_sleeptime=1
PLATFORMDIVISION=4

function runPython(){
    echo "########################################################################"
    _start=`date +%s`
    if [ "$3" == "" ];then
        python $1 $2
        wait
    else
        python $1 $2 &> $3 &  #replace 'echo' with 'python' when you are really ready!
        wait
    fi
    if [ $? -ne 0 ];then
        echo "$1 失败！"
        exit 1
    fi
    _end=`date +%s`
    _runtime=`expr $_end - $_start`
    echo "完成！用时${_runtime}秒。"
    echo "########################################################################"
    echo ""
    sleep $_sleeptime
    wait
}

function cleanDate(){
    sed "3c 	<clean_date_lasttime>0</clean_date_lasttime>" clean_date.xml > clean_date_temp.xml
    mv clean_date_temp.xml clean_date.xml
}

if [ "$1" == "" ];then
    echo "必须指定参数: 'reset' 或者 'update'."
    exit
elif [ "$1" == "reset" ];then
    _start=`date +%s`
    echo "RESET."
    echo ""
    echo "1.开始清理数据..."
    echo "1.0 校验各个project_info."
    #python /home/xiebo/atbtools/checkProject_infos.py
    if [ $? -ne 0 ];then
        echo "校验project_infos失败！"
        exit 1
    fi

    echo "1.1 校验还款方式."
    #python /home/xiebo/atbtools/checkPaymentMethod.py
    if [ $? -ne 0 ];then
        echo "校验还款方式失败！"
        exit 1
    fi

    echo "1.2 将project_info按照各个库的标数分片."
    python divideProject_infos.py ${PLATFORMDIVISION}
    if [ $? -ne 0 ];then
        echo "id分片失败！"
        exit 1
    fi

    echo "1.3 重置上次清理结果."
    python /home/xiebo/atbtools/truncateTable.py project_info_clean
    if [ $? -ne 0 ];then
        echo "重置清理结果失败！"
        exit 1
    fi

    echo "1.4 分进程对每一个片进行清理."
    for ((i=1;i<=${PLATFORMDIVISION};i++));do
        {
        sed -r 's/^(.*project_info_list = getListByTxt.*)\.txt"\)/\1_'${i}'\.txt"\)/' cleanproject_info_small.py > cleanproject_info_small_${i}.py
        runPython cleanproject_info_small_${i}.py blank clean_${i}.txt &
        wait
        } &
    done
    echo "批量计算中..."
    wait
    echo "批量计算结束..."
    echo "1.5 汇总清理结果."
    _end=`date +%s`
    _runtime=`expr $_end - $_start`
    echo "完成！整个清理工作用时${_runtime}秒。"

    echo ""
    echo "2.开始全量计算Tables..."
    echo "将多个平台进行分库..."
    python dividePlatform.py project_info_clean ${PLATFORMDIVISION}
	
    echo "开始重置Table01至Table06..."
    python truncateTable010203040506.py
	
    echo "开始全量计算Table01至Table06..."
    for ((i=1;i<=${PLATFORMDIVISION};i++));do
        {
        sed -r 's/^(.*platform_id_list = getListByTxt.*)\.txt"\)/\1_'${i}'\.txt"\)/' computeTable010203040506_whole.py > computeTable010203040506_whole_${i}.py
        runPython computeTable010203040506_whole_${i}.py ${1} 0106_whole_${i}.txt &
        wait
	} &
    done
    echo "批量计算中..."
    wait 
    echo "批量计算结束..."

    echo "开始重新计算MarketShareGrowth..."
    runPython /home/xiebo/atbtools/computeMarketShareGrowth.py Table_06_parameter_quantitative
	
    echo "Table01至Talbe06重置完毕."

    _end_whole_time=`date +%s`
    _runtime_whole=`expr $_end_whole_time - $_start_whole_time`
    sendEmail -f xiebo@antoubao.cn -t xiebo@antoubao.cn -s smtp.ym.163.com -u "compute123456 has finished" -o message-charset=utf-8 -xu xiebo@antoubao.cn -xp ac86207022 -m "cost ${_runtime_whole} seconds."

else
    echo "UPDATE."
    echo ""
    runPython filterNewPlatform.py

    echo "开始清理数据..."
    cleanDate
    runPython cleanproject_info.py ${1} clean.txt

    echo "开始计算新增站的全量数据010203040506..."
    runPython computeTable010203040506_whole_new.py ${1} 0106_new.txt
	
    echo "开始计算增量Talbe01、03..."
    runPython computeTable0103.py ${1} 0103.txt

    echo "开始计算增量Talbe02、04..."
    runPython computeTable0204.py ${1} 0204.txt

    echo "开始计算增量Talbe05..."
    runPython computeTable05.py ${1} 05.txt

    echo "开始计算增量Talbe06..."
    runPython computeTable06.py ${1} 06.txt
	
    echo "开始计算MarketShareGrowth..."
    runPython computeMarketShareGrowth.py
	
    echo "重新分库..."
    runPython dividePlatform.py
	
    echo "Table01至Talbe06计算增量完毕."
fi
