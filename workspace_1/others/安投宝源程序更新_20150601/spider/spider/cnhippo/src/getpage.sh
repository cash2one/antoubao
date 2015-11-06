#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    URL="${INVESTORPAGE}?TID=${ID}&pageindex=1#d"
    PAGENUM=$((`eval "${GETPAGE}" -O - "\"${URL}\"" | awk '{if (match($0, "当前第[0-9+]/[0-9+]页")) {print substr($0,RSTART,RLENGTH);}}' | sed -r 's/^当前第[0-9]+\/([0-9]+)页$/\1/g'`+0))

   for ((j=1;j<=${PAGENUM};j++))
    do
    URL="${INVESTORPAGE}?TID=${ID}&pageindex=${j}#d"
        eval "${GETPAGE}" -O "html/${ID}.brec.tmp" "\"${URL}\""      
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm html/${ID}.brec.tmp
done 
    bash apage.sh ${ID}
    sleep 2
done

exit 0

