#!/bin/bash

source ./conf.sh

# get index page
>data/id.list.tmp
for((i=1;i<=2;i++))
do
	eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" --post-data="\"${POSTDATA}\""\
		| awk '{s=$0; while (match(s, "queryBidInfo\.do\?borrowId=[0-9a-zA-Z]+")) {print substr(s, RSTART+25, RLENGTH-25); \
		s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
    sleep 1
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

