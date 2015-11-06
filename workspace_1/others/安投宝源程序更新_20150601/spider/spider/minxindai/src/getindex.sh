#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=4;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE1}${i}\"" \
        | awk '{s=$0; while (match(s, "http://www.minxindai.com/\?m=invest&c=info&borrowid=[0-9]+")) {print substr(s, RSTART+51, RLENGTH-51); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    sleep 1
done

for ((i=1;i<=2;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE2}${i}\"" \
        | awk '{s=$0; while (match(s, ""http://www.minxindai.com/\?m=invest&c=info&borrowid=[0-9]+")) {print substr(s, RSTART+51, RLENGTH-51); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    sleep 1
done

exit 0

