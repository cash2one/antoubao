#!/bin/bash

source ./conf.sh

# get index page
for LTYPE in ${LOANTYPE[@]}
do
    for((i=1;i<=3;i++))
    do
        eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" \
            | awk '{s=$0; while (match(s, "/'${LTYPE}'/Details/[0-9]+")) {print substr(s, RSTART, RLENGTH);s=substr(s, RSTART+1);}}' \
            | sed -r 's/\/(.+)\/Details\/([0-9]+)/\1_\2/g' | sort | uniq>>data/id.list.tmp
        sleep 1    
    done  
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

