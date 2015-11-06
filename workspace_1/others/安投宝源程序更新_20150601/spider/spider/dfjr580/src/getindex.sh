#!/bin/bash

source ./conf.sh

# get index page

>data/id.list.tmp

for((i=1;i<=2;i++))
do

    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}_0_1_0.html\"" \
    | awk '{s=$0; while (match(s, "http://www.dfjr580.com/borrow/[0-9]+")) {print substr(s, RSTART+30, RLENGTH-30); s=substr(s, RSTART+1);}}' | sort -r | uniq>>data/id.list.tmp
    sleep 5

done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

