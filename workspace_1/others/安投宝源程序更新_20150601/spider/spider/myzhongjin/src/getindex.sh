#!/bin/bash

source ./conf.sh
# get index page
>data/id.list.tmp
eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" | awk '{s=$0; while (match(s, "IdValue\":[0-9]+")) {printf("%s\n",substr(s, RSTART+9, RLENGTH-9)); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
sleep 1

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

