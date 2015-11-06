#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=3;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" \
        | awk '{s=$0; while (match(s, "/Project/Index/[0-9]+")) {print substr(s, RSTART+15, RLENGTH-15); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    sleep 1
done

exit 0

