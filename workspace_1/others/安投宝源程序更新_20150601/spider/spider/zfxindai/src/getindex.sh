#!/bin/bash

source ./conf.sh

>data/id.list.tmp

for ((i=0; i<=2; i++))
do
	eval "${GETPAGE}" -O - "\"${INDEXPAGE1}${i}.html\"" \
		| awk '{s=$0; while (match(s, "/invest/show/bid/[0-9]+.html")){printf("%s_%s\n", "0", substr(s, RSTART+17, RLENGTH-22)); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
	eval "${GETPAGE}" -O - "\"${INDEXPAGE2}${i}.html\"" \
		| awk '{s=$0; while (match(s, "/product/show/id/[0-9]+.html")){printf("%s_%s\n", "1", substr(s, RSTART+17, RLENGTH-22)); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp  

	sleep 1
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0
