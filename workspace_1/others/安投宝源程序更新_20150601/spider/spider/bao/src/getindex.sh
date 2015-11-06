#!/bin/bash

source ./conf.sh

# get index page

>data/id.list.tmp
for ((i=1;i<=3;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}.html\"" \
        | awk '{s=$0; while (match(s, "/product/ruyibao/inves/[0-9]+")) {print substr(s, RSTART+23, RLENGTH-23); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
    sleep 1
done


touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

