#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=3;i++))
do
   eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}${INDEXPAGE1}\"" \
        | awk '{s=$0; while (match(s, "/productDetail.do\?prodId=[0-9]+")) {print substr(s, RSTART+25, RLENGTH-25); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    
    sleep 1
done

exit 0

