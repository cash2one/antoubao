#!/bin/bash

_sleeptime=10
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

_start_whole=`date +%s`
if [ "$1" == "reset" ]
then
    echo "0. 重置坏站列表..."
    runPython getBadplatform.py
fi

echo "1. 校验各个project_info."
#python /home/xiebo/atbtools/checkProject_infos.py
if [ $? -ne 0 ];then
    echo "校验project_infos失败！"
    exit 1
fi

echo "2. 校验还款方式."
#python /home/xiebo/atbtools/checkPaymentMethod.py
if [ $? -ne 0 ];then
    echo "校验还款方式失败！"
    exit 1
fi

echo "3. 将坏站按照标数分片以备清理数据."
python divideBadplatformForClean.py ${PLATFORMDIVISION}
if [ $? -ne 0 ];then
    echo "id分片失败！"
    exit 1
fi

echo "4. 重置上次清理结果."
python createTempCleanInfo.py
if [ $? -ne 0 ];then
    echo "重置清理结果失败！"
    exit 1
fi

echo "5. 分进程对每一个片进行清理."
for ((i=1;i<=${PLATFORMDIVISION};i++));do
    {
        sed -r 's/^(.*platform_id_list = getListByTxt.*)\.txt"\)/\1_'${i}'\.txt"\)/' cleanProjectInfo.py > cleanProjectInfo_${i}.py
        #sed -r "43 s/^(.*)\.txt\"\)/\1_${i}\.txt\"\)/g" cleanProjectInfo.py > cleanProjectInfo_${i}.py
        runPython cleanProjectInfo_${i}.py blank clean_${i}.txt &
        wait
    } &
done
wait

echo "6. 坏站按照标数分片以备更新E1."
python divideBadplatformForUpdate.py project_info_clean_temp ${PLATFORMDIVISION}
if [ $? -ne 0 ];then
    echo "id分片失败！"
    exit 1
fi

echo "7. 开始更新坏站到E1表..."
for ((i=1;i<=${PLATFORMDIVISION};i++));do
    {
        sed -r 's/^(.*platform_id_list = getListByTxt.*)\.txt"\)/\1_'${i}'\.txt"\)/' updateTableE1.py > updateTableE1_${i}.py
        #sed -r "28 s/^(.*)\.txt\"\)/\1_${i}\.txt\"\)/g" updateTableE1.py > updateTableE1_${i}.py
        runPython updateTableE1_${i}.py blank clean_${i}.txt &
        wait
    } &
done
wait

#python delTempCleanInfo.py

echo "8. 统一计算market_share_growth..."
runPython /home/xiebo/atbtools/computeMarketShareGrowth.py platform_quantitative_data_E1

echo "9. 数据初步筛选..."
runPython /home/xiebo/maintenance_daily_db/basedata/filterDataSource.py reset

echo "10. 统计结果..."
runPython getBadPlatformFromE1.py 

_end_whole=`date +%s`
_runtime_whole=`expr ${_end_whole} - ${_start_whole}`

echo "cost ${_runtime_whole} seconds"

#sendEmail -f xiebo@antoubao.cn -t xiebo@antoubao.cn -s smtp.ym.163.com -u "updateE1.sh has finished." -o message-charset=utf-8 -xu xiebo@antoubao.cn -xp ac86207022 -m "cost ${_runtime_whole} seconds. " -a "bad_platform_name.txt"
