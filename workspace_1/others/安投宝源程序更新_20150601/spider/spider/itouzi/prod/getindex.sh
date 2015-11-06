#!/bin/bash

source ./conf.sh

>data/id.list
for TYPE in 2 5 6 7
do
    for ((i=1;i<=2;i++))
    do
        eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}&type=${TYPE}\"" \
            | awk '{s=$0; while (match(s, "\\\/dinvest\\\/[a-z]+\\\/detail\?id=[0-9a-z]+")) {print substr(s,RSTART,RLENGTH); s=substr(s, RSTART+1);}}' | sed -r 's/^\\\/[a-z]+\\\/([a-z]+)\\\/detail\?id=([0-9a-z]+)$/\1_\2/g'| sort | uniq>>data/id.list
        sleep 1
    done
done

exit 0

