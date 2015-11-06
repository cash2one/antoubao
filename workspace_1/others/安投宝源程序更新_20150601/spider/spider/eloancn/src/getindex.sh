#!/bin/bash

source ./conf.sh

>data/id.list.tmp

for ((i=1;i<=3;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" \
        | awk '{s=$0; while (match(s, "/loan/loandetail.action\?tenderid=[0-9]+")) {print substr(s, RSTART+33, RLENGTH-33); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
    sleep 1
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

