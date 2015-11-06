#!/bin/bash

source ./conf.sh

# get index page
>data/id.list.tmp
for((i=1;i<=3;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" \
        | awk '{s=$0; while (match(s, "http://www.firstp2p.com/deal/[0-9]+")) {print substr(s, RSTART+29, RLENGTH-29);s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
    sleep 1
done

sort data/id.list.tmp | uniq >data/id.list

exit 0

