#!/bin/bash

source ./conf.sh
# get index page
>data/id.list.tmp
for((i=1;i<=2;i++))
do
	eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" | awk '{s=$0; while (match(s, "/plan/detail/[a-zA-Z0-9]+.html\">立即加入")) {printf("%s\n",substr(s, RSTART+13, RLENGTH-13)); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
	sleep 1
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

