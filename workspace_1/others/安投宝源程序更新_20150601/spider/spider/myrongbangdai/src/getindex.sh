#!/bin/bash

source ./conf.sh
# get index page
>data/id.list.tmp
for((i=1;i<=2;i++))
do
	eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" | awk '{s=$0; while(match(s, "/Credit/Project/[0-9]+")) {printf("%s\n",substr(s, RSTART+16, RLENGTH-16));s=substr(s,RSTART+1)}}' | sort | uniq>>data/id.list.tmp
	sleep 1
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

