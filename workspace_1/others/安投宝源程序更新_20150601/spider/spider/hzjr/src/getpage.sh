#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}.html"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    URL="${INVESTORPAGE}${ID}/p/1.html"
    PAGENUM=$((`eval "${GETPAGE}" --header="\"X-Requested-With: XMLHttpRequest\"" -O - "\"${URL}\"" | awk '{if (match($0, "/invest/getrecord/id/[0-9]+/p/[0-9]+.html")) {print substr($0,RSTART,RLENGTH);}}' | sed -r 's/^[^0-9]+[0-9]+[^0-9]+([0-9]+)[^0-9]+$/\1/g' | sort -g | tail -n 1`+0))
    if [ $PAGENUM -lt 1 ]
    then
        PAGENUM=1
    fi
    >html/${ID}.brec
    for ((j=1;j<=${PAGENUM};j++))
    do
        URL="${INVESTORPAGE}${ID}/p/${j}.html"
        eval "${GETPAGE}" -O "html/${ID}.brec.tmp" --header="\"X-Requested-With: XMLHttpRequest\"" "\"${URL}\""      
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm html/${ID}.brec.tmp
        sleep 1
    done

    bash apage.sh ${ID}
    sleep 2
done

exit 0

