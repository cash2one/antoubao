#!/bin/bash

source ./conf.sh
# get index page
>data/id.list.tmp
>data/id.message.tmp
URL="${INDEXPAGE}"
eval "${GETPAGE}" -O - "${URL}" >>data/id.message.tmp
pagecount=$(cat data/id.message.tmp | grep -E "pageCount" | head -n 1 | sed -r 's/^.*pageCount[^0-9]+([0-9]+)[^0-9]+.*$/\1/g')
pagesize=$(cat data/id.message.tmp | grep -E "pageSize" | head -n 1 | sed -r 's/^.*pageSize[^0-9]+([0-9]+)[^0-9]+.*$/\1/g')
recordcount=$(cat data/id.message.tmp | grep -E "recordCount" | head -n 1 | sed -r 's/^.*recordCount[^0-9]+([0-9]+)[^0-9]+.*$/\1/g')
rm data/id.message.tmp
for((i=1;i<=2;i++))
do
	eval "${GETPAGE}" -O - "${URL}" "--post-data=\"${POSTDATA_INDEX}\"" \
		| awk '{s=$0;while(match(s,"/yuexitong.*/detail/[0-9]+.html")) {printf("%s\n",substr(s,RSTART,RLENGTH));\
		s=substr(s,RSTART+1);}}' | sort | uniq>>data/id.list.tmp
	sleep 1
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0
