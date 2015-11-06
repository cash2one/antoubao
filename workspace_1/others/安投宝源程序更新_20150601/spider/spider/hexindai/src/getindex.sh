#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=3;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}.html\"" \
        | awk '{s=$0; while (match(s, "/invest/detail-bid_[0-9]+.html")) {print substr(s, RSTART+19, RLENGTH-24); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    sleep 1
done

exit 0

