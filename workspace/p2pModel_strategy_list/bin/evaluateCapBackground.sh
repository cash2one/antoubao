#!/bin/bash

_sleeptime=1
fix_field="cap_background"
N=20
for ((i=0;i<=${N};i++))
    do
    weight=`echo " scale=2; 0.05 * $i " | bc -l | awk '{printf "%.2f", $0}'`
    echo ${weight}
    sed -r "s/^(.*\<${fix_field} weight).*/\1 = \"$weight\"\/\>/g" atbmodel_grade_initial.xml > atbmodel_grade.xml
    python checkXmlWeight.py -r ${fix_field}
    if [ $? -ne 0 ];then
        echo "重置指标权重失败！"
        exit 1
    fi
    bash start.sh -all "cap_background=${weight}+contributed_capital+punishment_origin+alevel" > start_${i}.txt
    if [ $? -ne 0 ];then
        echo "计算模型失败！"
        exit 1
    fi
    sleep $_sleeptime
done
