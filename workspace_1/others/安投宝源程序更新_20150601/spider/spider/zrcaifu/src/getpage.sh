#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    URL="${INVESTORPAGE}1&id=${ID}"
    PAGENUM=$((`eval "${GETPAGE}" -O - "\"${URL}\"" | awk '{s=$0; while (match(s, "id=[0-9]+\">[0-9]+")) {print substr(s, RSTART+8, RLENGTH-8); s=substr(s, RSTART+1);}}' | sort -g | tail -n 1`+0))
    if [ $PAGENUM -lt 1 ]
    then
        PAGENUM=1
    fi
    >html/${ID}.brec
    for ((j=1;j<=${PAGENUM};j++))
     do
     URL="${INVESTORPAGE}${j}&id=${ID}"
        eval "${GETPAGE}" -O "html/${ID}.brec.tmp" "\"${URL}\""      
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm html/${ID}.brec.tmp
    done

    bash apage.sh ${ID}
    sleep 2
done

exit 0

