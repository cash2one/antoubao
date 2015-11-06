#!/bin/bash

source ./conf.sh

>data/id.list.tmp

for ((t=0; t<3; t++))
do
	for ((i=0; i<=2; i++))
	do
		eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" --post-data="\"${POSTDATA[$t]}\"" \
			| awk '{s=$0; while (match(s, "loanId\":\"[0-9]+")){printf("%s_%s\n", "'${t}'", substr(s, RSTART+9, RLENGTH-9)); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
		sleep 1
	done
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0
