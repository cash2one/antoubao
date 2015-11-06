#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=2;i++))
do
   eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}-s-0-q-0\"" \
        | awk '{s=$0; while (match(s, "/b-[0-9]+")) {print substr(s, RSTART+3, RLENGTH-3); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    
    sleep 1
done

exit 0

