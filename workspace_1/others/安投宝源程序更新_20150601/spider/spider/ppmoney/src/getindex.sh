#!/bin/bash

source ./conf.sh
# get index page
>data/id.list.tmp
for((t=0;t<=2;t++))
do
	for((i=1;i<=3;i++))
	do
		URL="${INDEXPAGE}${i}"
		eval "${GETPAGE}" -O - "${URL}" \
			| awk '{s=$0;while(match(s,"/Project/[a-zA-Z]+/[0-9]+")) {printf("%s\n",substr(s,RSTART+9,RLENGTH-9));\
			s=substr(s,RSTART+1);}}' | sort | uniq>>data/id.list.tmp
		sleep 1
	done
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0
