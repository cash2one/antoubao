#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=2;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}.jhtml?bt=1&per=0&st=0\"" \
        | awk '{s=$0; while (match(s, "/debt/[0-9]+")) {print substr(s, RSTART+6, RLENGTH-6); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}.jhtml?bt=2&per=0&st=0\"" \
        | awk '{s=$0; while (match(s, "/debt/[0-9]+")) {print substr(s, RSTART+6, RLENGTH-6); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}.jhtml?bt=4&per=0&st=0\"" \
        | awk '{s=$0; while (match(s, "/debt/[0-9]+")) {print substr(s, RSTART+6, RLENGTH-6); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
        sleep 1
done

exit 0

