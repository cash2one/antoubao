#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=3;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}loanlist/p/${i}.html\"" \
        | awk '{s=$0; while (match(s, "\\\/loan\\\/loanInfo\\\/id\\\/[0-9]+")) {print substr(s, RSTART+22, RLENGTH-22); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}loanlist/newhand/1/p/${i}.html\"" \
        | awk '{s=$0; while (match(s, "\\\/loan\\\/loanInfo\\\/id\\\/[0-9]+")) {print substr(s, RSTART+22, RLENGTH-22); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
   eval "${GETPAGE}" -O - "\"${INDEXPAGE}transferlist/p/${i}.html\"" \
        | awk '{s=$0; while (match(s, "\\\/loan\\\/loanInfo\\\/id\\\/[0-9]+")) {print substr(s, RSTART+22, RLENGTH-22); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    
    sleep 1
done

exit 0

