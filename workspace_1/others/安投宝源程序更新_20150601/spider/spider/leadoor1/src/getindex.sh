#!/bin/bash

source ./conf.sh

>data/id.list
#for ((i=1;i<394;i++))
#do
    eval "${GETPAGE}" -O - "${INDEXPAGE}" | iconv -f gbk -t utf-8 \
        | awk '{s=$0; while (match(s, "/invest/a[0-9]+")) {print substr(s, RSTART+8, RLENGTH-8); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
#    sleep 1
#done

exit 0

