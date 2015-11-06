#!/bin/bash

source ./conf.sh

>data/id.list.tmp
#for ((i=1;i<5;i++))
#do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" \
        | awk '{s=$0; while (match(s, "http://www.dddai.cn/plan/detail/[0-9]+")) {print substr(s, RSTART+32, RLENGTH-32); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
#    sleep 1
#done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

