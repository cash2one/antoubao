#!/bin/bash

source ./conf.sh

>data/id.list.tmp

for s in ${INDEXPAGE}
do
    for ((i=1; i<=2; i++))
    do
        eval "${GETPAGE}" -O - "\"${s}${i}\"" \
            | awk '{s=$0; while (match(s, "onclick=\"get_detail\([0-9]+\)\">")) {print substr(s, RSTART+21, RLENGTH-24); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
    sheep 1;
    done
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0
