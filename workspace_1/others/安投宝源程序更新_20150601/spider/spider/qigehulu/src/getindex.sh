#!/bin/bash

source ./conf.sh

# get index page
for ((i=1;i<=4;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" --post-data="\"${POSTDATA}${i}\"" \
        | awk '{if (match($0, "a href=\"creditBidinfoList\?bidinfoId=[0-9a-z]+\"")) {print substr($0, RSTART+36, RLENGTH-37)}}' \
        | sort | uniq >>data/id.list.tmp
    sleep 1
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

