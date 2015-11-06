#!/bin/bash

source ./conf.sh

# get index page
>data/id.list.tmp
for((i=1;i<=2;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" | iconv -f gbk -t utf-8 \
        | awk '{s=$0; while (match(s, "/\?invest&article_id=[0-9]+")) {print substr(s, RSTART+20, RLENGTH-20); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
    sleep 1
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

