#!/bin/bash

source ./conf.sh

# get index page
>data/id.list.tmp
for ((i=1;i<=3;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" \
        | awk '{if (match ($0, "a href=\"project.php.x_id=[0-9]+\"")) {print substr($0, RSTART+25, RLENGTH-26);}}' \
        | sort | uniq >>data/id.list.tmp
    sleep 3
done

sort data/id.list.tmp | uniq >data/id.list

exit 0

