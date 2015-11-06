#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    sleep 1
    URL="${INVESTORPAGE}${ID}?account=0&wait=0.0&page=1"
    PAGENUM=$((`eval "${GETPAGE}" -O - "\"${URL}\"" | awk '{if (match($0, "共分<em>[0-9]+</em>页显示")) {print substr($0,RSTART,RLENGTH);}}' | sed -r 's/^共分[^0-9]+([0-9]+)[^0-9]+页显示$/\1/g'`+0))
    for ((j=1;j<=${PAGENUM};j++))
    do
        URL="${INVESTORPAGE}${ID}?account=0&wait=0.0&page=${j}"
        eval "${GETPAGE}" -O "html/${ID}.brec.tmp" "\"${URL}\""      
        sleep 1
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm html/${ID}.brec.tmp
    done

    bash apage.sh ${ID}
    sleep 2
done

exit 0

