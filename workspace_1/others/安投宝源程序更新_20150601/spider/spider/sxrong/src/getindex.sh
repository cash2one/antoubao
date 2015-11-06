#!/bin/bash

source ./conf.sh

# get index page
>data/id.list.tmp
for ((i=1; i<=3; i++))
do
    "${GETPAGE}" -O - "${INDEXPAGE}" --post-data="page=${i}&ps=10&loantype=0&loanlimit=0&loanstatus=0" \
        | awk '{s=$0; while (match(s, "\"No\":\"([0-9]+)\"")) {print substr(s, RSTART+6, RLENGTH-7); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
    sleep 1
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

