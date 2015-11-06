#!/bin/bash

source ./conf.sh

>data/id.list.tmp

for s in ${INDEXPAGE}
do
    for ((i=1; i<=2; i++))
    do
        eval "${GETPAGE}" -O - "${s}${i}" \
            | awk '{s=$0; while (match(s, "http://www.ppdai.com/list/[0-9]+\?loanlist")) {print substr(s, RSTART+26, RLENGTH-35); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
    done
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0
