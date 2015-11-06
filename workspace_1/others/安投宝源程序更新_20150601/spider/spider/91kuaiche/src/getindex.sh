#!/bin/bash

source ./conf.sh
# get index page
>data/id.list.tmp
for((t=0;t<=1;t++))
do
	for((i=1;i<=2;i++))
	do
		URL="${INDEXPAGE}${i}.html"
		eval "${GETPAGE}" -O - "${URL}" | awk '{s=$0;while(match(s,"http://w8.91kuaiche.com/.*.html")) {printf("%s\n",substr(s,RSTART+24,RLENGTH-29));s=substr(s,RSTART+1);}}' | sort | uniq>>data/id.list.tmp
		sleep 1
	done
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0
