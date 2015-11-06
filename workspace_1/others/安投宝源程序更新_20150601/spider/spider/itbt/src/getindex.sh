#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=2;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" --post-data="\"${INDPOSTDATA}${i}${INDPOSTDATA1}\""\
        | awk '{s=$0; while (match(s, "\"id\":\"[0-9]+")) {print substr(s, RSTART+6, RLENGTH-6); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    sleep 1
done

exit 0

