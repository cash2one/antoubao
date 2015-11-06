#!/bin/bash

source ./conf.sh

>data/id.list.tmp

for ((i=1;i<=3;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" --post-data="\"${POSTDATA}${i}\"" \
        | awk '{s=$0; while (match(s, "/borrow/detail.do\?bId=[0-9]+")) {print substr(s, RSTART+22, RLENGTH-22); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
    sleep 1
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

