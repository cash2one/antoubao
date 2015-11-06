#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}/"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    >html/${ID}.brec
    URL="${INVESTORPAGE}${ID}/" 
    eval "${GETPAGE}" -O "html/${ID}.brec.tmp" "\"${URL}\""
    ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
    cat html/${ID}.brec.tmp >>html/${ID}.brec
    rm html/${ID}.brec.tmp

    bash apage.sh ${ID}
    sleep 2
done

exit 0

