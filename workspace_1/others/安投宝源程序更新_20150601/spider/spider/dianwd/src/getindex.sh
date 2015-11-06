#!/bin/bash

source ./conf.sh
# get index page
>data/id.list.tmp
for((t=0;t<=1;t++))
do
	for((i=1;i<=2;i++))
	do
		eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" | awk '{s=$0; while (match(s, "/invest/item/[0-9]+.html")) {printf("%s\n",substr(s, RSTART+12, RLENGTH-17));s=substr(s,RSTART+1);}}' | sort | uniq>>data/id.list.tmp
		sleep 1
	done
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

