#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}`echo ${ID} | sed 's/_/\//g'`.html"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    id=`eval "${GETPAGE}" -O - "\"${URL}\"" | awk '{if (match($0, "nid:[0-9]+")) {print substr($0,RSTART,RLENGTH);}}' | head -n 1 | sed -r 's/^[^0-9]+([0-9]+).*$/\1/g'`
    URL="${INVESTORPAGE}${id}&pageNumber=1&pageSize=10"
    PAGENUM=$((`eval "${GETPAGE}" -O - "\"${URL}\"" | awk '{if (match($0, "\"totalPages\": [0-9]+")) {print substr($0,RSTART,RLENGTH);}}' | sed -r 's/^[^0-9]+([0-9]+).*$/\1/g'`))
    if [ $PAGENUM -lt 1 ]
    then
        PAGENUM=1
    fi
    >html/${ID}.brec
    for ((j=1;j<=${PAGENUM};j++))
    do
        URL="${INVESTORPAGE}${id}&pageNumber=${j}&pageSize=10"
        eval "${GETPAGE}" -O "html/${ID}.brec.tmp" "\"${URL}\""
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm html/${ID}.brec.tmp
    done
    bash apage.sh ${ID}
    sleep 2
done
    exit 0


