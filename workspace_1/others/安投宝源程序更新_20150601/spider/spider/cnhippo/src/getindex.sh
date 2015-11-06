#!/bin/bash

source ./conf.sh

>data/id.list.tmp
for ((i=1;i<=3;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}#d\"" \
        | awk '{s=$0; while (match(s, "borrow/Borrowing_the_details\.aspx\?TID=[0-9]+")) {print substr(s, RSTART+38, RLENGTH-38); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
    sleep 1
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

