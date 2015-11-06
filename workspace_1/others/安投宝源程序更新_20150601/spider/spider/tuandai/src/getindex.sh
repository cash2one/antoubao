#!/bin/bash

source ./conf.sh

>data/id.list.tmp

TYPES="1 2 4 5"
for t in ${TYPES}
do
    for ((i=1;i<=3;i++))
    do
        ${GETPAGE} -O - "${INDEXPAGE}" --post-data="Cmd=GetInvest_List&RepaymentTypeId=0&pagesize=5&projectType=0&pageindex=${i}&type=${t}&status=1&DeadLine=0&beginDeadLine=0&endDeadLine=0&rate=0&beginRate=0&endRate=0&strkey=&orderby=0" \
            | awk '{s=$0; while (match(s, "\"ID\":\"[0-9a-z\-]+")) {print substr(s, RSTART+6, RLENGTH-6); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
    done
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

