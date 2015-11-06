#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}.html"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    >html/${ID}.brec
    for ((j=1;j<=50;j++))
     do
     URL="${INVESTORPAGE}"
    eval "${GETPAGE}" -O - "\"${URL}\"" --post-data="\"page=${j}&id=${ID}\"" >"html/${ID}.brec.tmp"    
     ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm html/${ID}.brec.tmp
    done

    bash apage.sh ${ID}
    sleep 2
done

exit 0

