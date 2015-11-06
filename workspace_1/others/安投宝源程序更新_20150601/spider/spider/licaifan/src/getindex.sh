#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<3;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" --post-data="\"${POSTDATA}${i}&project_type=0&months=0&apr=0&status=0\"" \
        | awk '{s=$0; while (match(s, "url\":\"\\\/[a-z]+\\\/[a-z]+\\\/[a-z0-9]+")) {print substr(s, RSTART+8, RLENGTH-8); s=substr(s, RSTART+1);}}' | sed -r 's/\//_/g' | sort | uniq>>data/id.list
         sleep 1
done

exit 0

