#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=3;i++))
do
     eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" --post-data="\"isPaginPage=1&currentPage=${i}&borrowType=0&borrowPeriod=0&orderBy=&orderType=&isOnlyDisplayBidding=0\"" \
          | awk '{s=$0; while (match(s, "subjectId\":\"[0-9]+")) {print substr(s, RSTART+12, RLENGTH-12); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list      
    sleep 1
done

exit 0

