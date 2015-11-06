#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}"
    PAGENUM=`eval "${GETPAGE}" -O - "\"${URL}\"" | awk '{s=$0; while (match(s, "<option.value=.[0-9]+")) {print substr(s, RSTART+15, RLENGTH-15); s=substr(s, RSTART+1);}}' | uniq | tail -n 1`
    for ((j=1;j<=${PAGENUM};j++))
    do
    URL="${DETAILPAGE}${ID}&page=${j}"
    eval "${GETPAGE}" -O "html/${ID}.tmp" "\"${URL}\""
    ls -l html/${ID}.tmp | awk '{printf("%08X", $5)}' >>html/${ID}
    cat html/${ID}.tmp >>html/${ID}
    rm html/${ID}.tmp
    sleep 1
     done

    bash apage.sh ${ID}
    sleep 2 
done    

exit 0

