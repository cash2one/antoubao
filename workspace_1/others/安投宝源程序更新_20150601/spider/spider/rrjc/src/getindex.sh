#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<3;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" --post-data="\"pageNum=${i}&pageBean.pageNum=${i}\"" \
        | awk '{s=$0; while (match(s, "planDetail\([0-9]+")) {print substr(s, RSTART+11, RLENGTH-11); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    sleep 1
done

exit 0

