#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}.html"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    URL="${INVESTORPAGE}${ID}.html?p=1"
    PAGENUM=$((`eval "${GETPAGE}" -O - "\"${URL}\"" | awk '{if (match($0, "条记录 [0-9]+/[0-9]+")) {print substr($0,RSTART,RLENGTH);}}' | sed -r 's/^[^0-9]+[0-9]+[^0-9]([0-9]+)$/\1/g'`))
    if [ $PAGENUM -lt 1 ]
    then
        PAGENUM=1
    fi
    >html/${ID}.brec
    for ((j=1;j<=${PAGENUM};j++))
     do
     URL="${INVESTORPAGE}${ID}.html?p=${j}"
        eval "${GETPAGE}" -O "html/${ID}.brec.tmp" "\"${URL}\""      
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm html/${ID}.brec.tmp
    done

    bash apage.sh ${ID}
    sleep 2
done

exit 0

