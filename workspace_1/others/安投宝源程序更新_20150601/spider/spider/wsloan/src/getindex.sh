#!/bin/bash

source ./conf.sh

# get index page
>data/id.list.tmp
for ((t=1; t<=3; t++))
do
    for ((i=1; i<=3; i++))
    do
        "${GETPAGE}" -O - "${INDEXPAGE}${t}.aspx?page=${i}&px=" \
            | awk '{s=$0; while (match(s, "a href=\"jkxq\.aspx\?id=([0-9]+)\"")) {print substr(s, RSTART+21, RLENGTH-22); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
        sleep 1
    done
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

