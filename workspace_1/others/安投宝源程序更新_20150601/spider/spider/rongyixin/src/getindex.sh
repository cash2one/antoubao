#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=2;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" \
        | awk '{s=$0; while (match(s, "/invest/[0-9]+.html")) {print substr(s, RSTART+8, RLENGTH-13); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    sleep 1
done

exit 0

