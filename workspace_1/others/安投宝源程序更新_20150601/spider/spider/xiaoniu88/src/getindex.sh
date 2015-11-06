#!/bin/bash

source ./conf.sh

>data/id.list.tmp.1
for ((i=1; i<=3; i++))
do
    eval "${GETPAGE}" -O - "${INDEXPAGE1}/${i}" \
        | awk '{s=$0; while (match(s, "/product/planning/detail/[0-9]+\" title")) {print substr(s, RSTART+25, RLENGTH-32); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp.1
    sleep 1
done
touch data/id.list.old.1
sort data/id.list.tmp.1 data/id.list.old.1 | uniq >data/id.list.1
mv data/id.list.tmp.1 data/id.list.old.1

>data/id.list.tmp.2
for ((i=1; i<=3; i++))
do
    eval "${GETPAGE}" -O - "${INDEXPAGE2}/${i}" \
        | awk '{s=$0; while (match(s, "/product/listing/detail/[0-9]+\" title")) {print substr(s, RSTART+24, RLENGTH-31); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp.2
    sleep 1
done
touch data/id.list.old.2
sort data/id.list.tmp.2 data/id.list.old.2 | uniq >data/id.list.2
mv data/id.list.tmp.2 data/id.list.old.2

exit 0

