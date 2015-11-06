#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=2;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}#pagenav\"" \
        | awk '{s=$0; while (match(s, "https://www.yscf.com/trade/borrow/[0-9/]+")) {print substr(s, RSTART+34, RLENGTH-34); s=substr(s, RSTART+1);}}'  | sed -r 's/\//_/g'| sort | uniq>>data/id.list
    sleep 1
done

exit 0

