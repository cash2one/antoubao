#!/bin/bash

source ./conf.sh
# get index page
>data/id.list.tmp
for((i=1;i<=2;i++))
do
	eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" --post-data="\"${POSTDATA}\""| awk '{s=$0; if (match(s, "/loan/loan_detail.bl\?loanNo=[0-9]+")) {printf("%s\n",substr(s, RSTART+28, RLENGTH-28));}}' | sort | uniq>>data/id.list.tmp
	sleep 1
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

