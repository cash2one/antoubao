#!/bin/bash

source ./conf.sh

>data/id.list.tmp

eval "${GETPAGE}" -O - "\"${INDEXPAGE1}\"" "\"${INDEXPAGE9}\"" \
    | awk '{s=$0; while (match(s, "investment-details[0-9]+.html")) {print substr(s, RSTART+18, RLENGTH-23); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp

#for ((i=1;i<=45;i++))
#do
#    eval "${GETPAGE}" -O - "\"${INDEXPAGE9}\"" --post-data="\"${POSTDATA}${i}\"" \
#        | awk '{s=$0; while (match(s, "investment-details[0-9]+.html")) {print substr(s, RSTART+18, RLENGTH-23); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
#    sleep 1
#done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

