#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""

    URL="${INVESTORPAGE}${ID}&page=1"
    PAGENUM=`eval "${GETPAGE}" -O - "\"${URL}\"" | awk '{if (match($0, "\"pcount\":[0-9]+")) print int(substr($0, RSTART+9, RLENGTH-9));}'`
    >html/${ID}.brec
    for ((j=1;j<=${PAGENUM};j++))
    do
        URL="${INVESTORPAGE}${ID}&page=${j}"
        eval "${GETPAGE}" -O "html/${ID}.brec.tmp" "\"${URL}\""
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm html/${ID}.brec.tmp
    done

    bash apage.sh ${ID}
    sleep 2
done

exit 0

