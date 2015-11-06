#!/bin/bash

source ./conf.sh

>data/id.list.tmp
for x in ${INDEXPAGE}
do
    for ((i=1;i<=2;i++))
    do
        eval "${GETPAGE}" -O - "\"${x}${i}\"" \
            | awk '{s=$0; while (match(s, "/invest/a[0-9]+")) {print substr(s, RSTART+9, RLENGTH-9); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
        sleep 1
    done
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

