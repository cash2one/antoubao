#!/bin/bash

source ./conf.sh

>data/id.list.tmp
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" \
        | awk '{s=$0; while (match(s, "/index.php/home/fund/day_[a-z]+")) {print substr(s, RSTART+25, RLENGTH-25); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
    sleep 1 

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

