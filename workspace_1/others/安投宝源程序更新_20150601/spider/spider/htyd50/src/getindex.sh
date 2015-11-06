#!/bin/bash

source ./conf.sh

# get index page
>data/id.list.tmp


for ((i=1; i<=1; i++))
do
	eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\""\
		| awk '{s=$0; while (match(s, "/trade/borrow/[0-9]+/[0-9]+/[0-9]+.html")){print substr(s, RSTART+14, RLENGTH-19); s=substr(s, RSTART+1);}}' | sort | uniq | tr "/" "-">>data/id.list.tmp
	sleep 1
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

