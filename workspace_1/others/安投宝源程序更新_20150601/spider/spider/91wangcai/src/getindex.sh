#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=5;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" \
        | awk '{s=$0; while (match(s, "/view/borrow/[0-9]+")) {print substr(s, RSTART+13, RLENGTH-13); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    sleep 1
done

exit 0

