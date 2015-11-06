#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}.html"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    URL="${INVESTORPAGE}" 
    PAGENUM=$((`eval "${GETPAGE}" -O - "\"${URL}\"" --post-data="\"borrowId=${ID}&page=1\"" | awk '{if (match($0, "<span id=\"totalPages\">[0-9]+</span>")) {print substr($0,RSTART,RLENGTH);}}' | sed -r 's/^[^0-9]+([0-9]+)[^0-9]+$/\1/g'`))
    if [ $PAGENUM -lt 1 ]
    then
        PAGENUM=1
    fi
    >html/${ID}.brec
    for ((j=1;j<=${PAGENUM};j++))
     do
     URL="${INVESTORPAGE}" 
        eval "${GETPAGE}" -O "html/${ID}.brec.tmp" "\"${URL}\"" --post-data="\"borrowId=${ID}&page=${j}\""      
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm html/${ID}.brec.tmp
    done

    bash apage.sh ${ID}
    sleep 2
done

exit 0

