#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}.html"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""

    URL="${INVESTORPAGE}${ID}-pageid_1.html"
    PAGENUM=`eval "${GETPAGE}" -O - "\"${URL}\"" | awk '{if (match($0, "共 [0-9]+ 条 [0-9]+ 页")) {print substr($0,RSTART,RLENGTH);}}' | sed -r 's/^.+条 ([0-9]+) 页/\1/g'`
    >html/${ID}.brec
    for ((j=1;j<=${PAGENUM};j++))
    do
        URL="${INVESTORPAGE}${ID}-pageid_${j}.html"
        eval "${GETPAGE}" -O "html/${ID}.brec.tmp" "\"${URL}\""
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm html/${ID}.brec.tmp
    done

    bash apage.sh ${ID}
    sleep 2
done

exit 0

