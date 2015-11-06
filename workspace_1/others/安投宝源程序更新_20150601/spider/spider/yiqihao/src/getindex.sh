#!/bin/bash

source ./conf.sh

>data/id.list.tmp

eval "${GETPAGE} --no-check-certificate" -O - "${INDEXPAGE}" --post-data="\"size=30\"" \
    | awk '{s=$0; while (match(s, "\"lid\":\"[0-9]+")) {print substr(s, RSTART+7, RLENGTH-7); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp

eval "${GETPAGE} --no-check-certificate" -O - "${INDEXPAGE}" --post-data="\"size=30&is_newbie=1\"" \
    | awk '{s=$0; while (match(s, "\"lid\":\"[0-9]+")) {print substr(s, RSTART+7, RLENGTH-7); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

