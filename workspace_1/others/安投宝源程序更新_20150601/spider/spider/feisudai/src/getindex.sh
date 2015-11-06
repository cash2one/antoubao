#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=0;i<=2;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}&borrow_style=0&borrow_period=0&award_status=0&type=0\"" \
        | awk '{s=$0; while (match(s, "/invest/a[0-9]+")) {print substr(s, RSTART+9, RLENGTH-9); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    sleep 1
done

exit 0

