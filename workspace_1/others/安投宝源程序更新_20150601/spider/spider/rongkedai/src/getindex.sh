#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=2;i++))
do
   eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" --post-data="\"${POSTDATA}${i}${POSTDATA1}\"" \
        | awk '{s=$0; while (match(s, "/borrow/borrow-detail/[0-9]+")) {print substr(s, RSTART+22, RLENGTH-22); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    
    sleep 1
done

exit 0

