#!/bin/bash

_sleeptime=3
punishment_list=(01 021 022 031 032 041 042 051 052 061 062 07 081 082 091 092 093 094 10 111 112 121 122 13 )
punishment_list=(13 031 021 041 051 081 091 093 111 121 01 022 032 042 052 07 082 092 094 10 112 122)
max_p_list=(10 10 5 5 5 5 5 5 5 5 3 3 3 3 3 3 3 3 3 3 3 3)
min_p=0
if [ ${#punishment_list[@]} -ne ${#max_p_list[@]} ]; then 
    echo "数组长度不同."
    exit 1
fi
#for ((i=0;i<${#punishment_list[@]};i++))
for ((i=0;i<1;i++))
    do
    punishment=\#PU${punishment_list[${i}]}\#
    echo ${punishment}
    max_p=${max_p_list[${i}]}
    space=1
    if [ ${max_p} -gt 6 ]; then
        space=2
    fi
    for deduction in `seq ${min_p} ${space} ${max_p}`
        do
        echo ${deduction}
        sed -r 's/^(.*<'${punishment}' deduction).*/\1 = "'${deduction}'"\/>/' atbmodel_punish.xml > atbmodel_punish_final.xml
        bash start.sh -all "${punishment}=${deduction}" > start_${deduction}.txt
        if [ $? -ne 0 ];then
            echo "计算模型失败！"
            exit 1
        fi
        sleep $_sleeptime
    done
done
