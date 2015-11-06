#!/bin/bash

source ./conf.sh

>data/id.list
  NUM=`eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" | awk '{if (match($0, "<span id=\"totalPages\">[0-9]+</span>")) {print substr($0,RSTART,RLENGTH);}}' | sed -r 's/^[^0-9]+([0-9]+)[^0-9]+$/\1/g'`
  ANUM=`eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" | awk '{if (match($0, "<span id=\"totalRecords\">[0-9]+</span>")) {print substr($0,RSTART,RLENGTH);}}' | sed -r 's/^[^0-9]+([0-9]+)[^0-9]+$/\1/g'`
for ((i=1;i<=5;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" --post-data="\"page_count=${NUM}&page_size=10&record_count=${ANUM}&page=${i}\"" \
        | awk '{s=$0; while (match(s, "/item/[0-9]+")) {print substr(s, RSTART+6, RLENGTH-6); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    sleep 1
done

exit 0

