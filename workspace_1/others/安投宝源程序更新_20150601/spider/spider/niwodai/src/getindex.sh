#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=25;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" \
        | awk '{s=$0; while (match(s, "href=\"/xiangmu/[^.]+.html\"")) {print substr(s, RSTART+15, RLENGTH-21); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    sleep 1
done

exit 0

