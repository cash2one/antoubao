#!/bin/bash

source ./conf.sh

# get index page
>html/indexsrc.tmp
for ((i=1; i<=2; i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" >>html/indexsrc.tmp
    sleep 1
done

cat html/indexsrc.tmp | awk '{if (match($0, "href=\"/Project/Index/[^\"]+\"")) {print substr($0, RSTART+21, RLENGTH-22);}}' | sort | uniq >data/id.list.tmp
cat html/indexsrc.tmp | awk '{if (match($0, "href=\"/Project/ProjectSet/[^\"]+\"")) {print substr($0, RSTART+6, RLENGTH-7);}}' \
    | sort | uniq | while read SETURL
do
    eval "${GETPAGE}" -O - "\"${HOST}${SETURL}\"" \
        | awk '{if (match($0, "href=\"/Project/Index/[^\"]+\"")) {print substr($0, RSTART+21, RLENGTH-22);}}' | sort | uniq >>data/id.list.tmp
    sleep 1
done

sort data/id.list.tmp | uniq >data/id.list

rm html/indexsrc.tmp
rm data/id.list.tmp

exit 0

