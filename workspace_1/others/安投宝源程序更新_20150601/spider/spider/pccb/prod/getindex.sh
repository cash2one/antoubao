#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=5;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE1}${i}.html\"" \
        | awk '{s=$0; while (match(s, "/invest/[0-9]+")) {print substr(s, RSTART+8, RLENGTH-8); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
     eval "${GETPAGE}" -O - "\"${INDEXPAGE2}${i}.html\"" \
          | awk '{s=$0; while (match(s, "/invest/[0-9]+")) {print substr(s, RSTART+8, RLENGTH-8); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
      eval "${GETPAGE}" -O - "\"${INDEXPAGE5}${i}.html\"" \
          | awk '{s=$0; while (match(s, "/invest/[0-9]+")) {print substr(s, RSTART+8, RLENGTH-8); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
          
    sleep 1
done

exit 0

