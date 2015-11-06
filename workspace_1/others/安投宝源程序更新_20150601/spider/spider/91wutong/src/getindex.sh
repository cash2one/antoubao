#!/bin/bash

source ./conf.sh
# get index page
>data/id.list.tmp
for((t=1;t<=2;t++))
do
	for((i=0;i<=2;i++))
	do
		eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" | awk '{s=$0; while (match(s, "/index.php/anyinvest/(zichan|any)/[0-9]+")) {printf("%s\n",substr(s, RSTART+21, RLENGTH-21)); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
		sleep 1
	done
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

