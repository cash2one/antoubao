#!/bin/bash

source ./conf.sh

# get index page

for x in ${INDEXPAGE}
do

    for((i=1;i<=3;i++))
    do
        eval "${GETPAGE}" -O - "\"${x}${i}.html\"" \
            | awk '{s=$0; while (match(s, "/invest/details/[a-z0-9A-Z]+.html")) {print substr(s, RSTART+16, RLENGTH-21);s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
        sleep 1    
    
    done
done
touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

