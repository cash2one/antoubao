#!/bin/bash

source ./conf.sh

# get index page
>data/id.list.tmp
for ((i=1; i<=3; i++))
do
    "${GETPAGE}" -O - "${INDEXPAGE1}" --post-data="page.pageNo=${i}&page.orderBy=&page.order=" \
        | awk '{s=$0; while (match(s, "href=\"/dqb/dqb-project!dqhProjectDetail\.action\?id=([0-9a-z]+)\"")) {print substr(s, RSTART+50, RLENGTH-51); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp 
    sleep 1
done

touch data/id.list.old.1
sort data/id.list.tmp data/id.list.old.1 | uniq >data/id.list.1
mv data/id.list.tmp data/id.list.old.1

>data/id.list.tmp
for ((i=1; i<=3; i++))
do
    "${GETPAGE}" -O - "${INDEXPAGE2}" --post-data="page.pageNo=${i}&page.orderBy=&page.order=" \
        | awk '{s=$0; while (match(s, "href=\"/zj/invest-project!investProjectDetail\.action\?id=([0-9a-z]+)\"")) {print substr(s, RSTART+55, RLENGTH-56); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp 
    sleep 1
done

touch data/id.list.old.2
sort data/id.list.tmp data/id.list.old.2 | uniq >data/id.list.2
mv data/id.list.tmp data/id.list.old.2

exit 0

