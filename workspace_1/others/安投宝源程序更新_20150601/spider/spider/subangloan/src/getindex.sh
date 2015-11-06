#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<3;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" --post-data="\"${POSTDATA}${i}\"" \
        | awk '{s=$0; while (match(s, "/ScatterBid/LoanDetail\?LoanId=[0-9]+")) {print substr(s, RSTART+30, RLENGTH-30); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    sleep 1
done

exit 0

