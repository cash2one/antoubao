#!/bin/bash

source ./conf.sh

>data/id.list.tmp
for ((i=1; i<=5; i++))
do
    eval "${GETPAGE}" -O - "${INDEXPAGE}/?pageindex=${i}" \
        | awk '{s=$0; while (match(s, "href=\"/Borrow/Borrow/[0-9a-z]+\" class=\"w150 loantit\"")) {print substr(s, RSTART+21, RLENGTH-43); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
done
touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

