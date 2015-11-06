#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=2;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}&data=%E5%85%A8%E9%83%A8%2C%E5%85%A8%E9%83%A8%2C%E5%85%A8%E9%83%A8%2C%E5%85%A8%E9%83%A8\"" \
        | awk '{s=$0; while (match(s, "id\":\"[0-9]+")) {print substr(s, RSTART+5, RLENGTH-5); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}&data=%E5%85%A8%E9%83%A8%2C%E5%85%A8%E9%83%A8%2C%E5%85%A8%E9%83%A8%2C%E5%85%A8%E9%83%A8\"" \
        | awk '{s=$0; while (match(s, "id\":\"[0-9]+")) {print substr(s, RSTART+5, RLENGTH-5); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    
    sleep 1
done

exit 0

