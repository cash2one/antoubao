#!/bin/bash

source ./conf.sh

# get index page
#for((i=1;i<=3;i++))
#do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" \
        | awk '{s=$0; while (match(s, "http://www.anxin.com/invest/detail[^.]+.html")) {print substr(s, RSTART+34, RLENGTH-39);s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
    sleep 1    
    
#done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

