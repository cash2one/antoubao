#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=0;i<2;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" "--post-data=\"pager.pageNumber=${ID}\"" \
        | awk '{s=$0; while (match(s, "/borrow/detail.do\?bId=[0-9]+")) {print substr(s, RSTART+22, RLENGTH-22); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    
    sleep 1
done

exit 0

