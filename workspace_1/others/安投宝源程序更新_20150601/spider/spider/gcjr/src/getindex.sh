#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=2;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}&pageSize=10&borrowType=&limitTime=isTendering&orderType=&isShowNewBorrow=1\"" \
        | awk '{s=$0; while (match(s, "goToInvest[^0-9][0-9]+")) {print substr(s, RSTART+11, RLENGTH-11); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    sleep 1
done

exit 0

