#!/bin/bash

source ./conf.sh
# get index page
>data/id.list.tmp
for((t=0;t<=3;t++))
do
	for((i=1;i<=2;i++))
	do
		if [ $t -lt "3" ]
		then
			eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" | awk '{s=$0; while (match(s, "/Financing/Invest/view\?id=[0-9]+")) {printf("%s_%s\n","'${t}'",substr(s, RSTART+26, RLENGTH-26)); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
			sleep 1
		else
			eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" | awk '{s=$0; while (match(s, "/Financing/Invest/fastCash\?id=[0-9]+")) {printf("%s_%s\n","'${t}'",substr(s, RSTART+30, RLENGTH-30)); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
		fi
	done
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

