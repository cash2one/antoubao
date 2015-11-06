#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=2;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" \
        | awk '{s=$0; while (match(s, "\"project_no\":\"[A-Z0-9]+-[0-9]+")) {print substr(s, RSTART+14, RLENGTH-14); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
 
    sleep 1
done

exit 0

