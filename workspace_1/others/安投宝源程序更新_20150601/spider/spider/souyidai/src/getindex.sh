#!/bin/bash

source ./conf.sh
# get index page
>data/id.list.tmp
for((t=0;t<=1;t++))
do
	for((i=0;i<=2;i++))
	do
		POSTDATA1=$(eval echo \${POSTDATA1_${t}})
		POSTDATA2=$(eval echo \${POSTDATA2_${t}})
		eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" --post-data="\"${POSTDATA1}\""| awk '{s=$0; if (match(s, "/bid/detail/[0-9]+")) {printf("%s_",substr(s, RSTART+12, RLENGTH-12));} if (match(s,"【.*】[^0-9A-Za-z]*[0-9a-zA-Z]+")) {printf("%s\n",substr(s,RSTART,RLENGTH));}}' | sort | uniq>>data/id.list.tmp
		eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" --post-data="\"${POSTDATA2}\""| awk '{s=$0; if (match(s, "/bid/detail/[0-9]+")) {printf("%s_",substr(s, RSTART+12, RLENGTH-12));} if (match(s,"【.*】[^0-9A-Za-z]*[0-9a-zA-Z]+")) {printf("%s\n",substr(s,RSTART,RLENGTH));}}' | sort | uniq>>data/id.list.tmp
		sleep 1
	done
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

