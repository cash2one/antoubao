#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    TYPE=`echo ${ID} | cut -d '_' -f 1`
    BID=`echo ${ID} | cut -d '_' -f 2`

    URL="${DETAILPAGE}${TYPE}/detail?id=${BID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""

    >html/${ID}.brec
    URL="${INVESTORPAGE}"

    eval "${GETPAGE}" -O - "\"${URL}\"" --post-data="\"borrow_id=${BID}&user_id=552614&isAll=false&debtType=${TYPE}\"" >"html/${ID}.brec.tmp"      

    ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
    cat html/${ID}.brec.tmp >>html/${ID}.brec
    rm html/${ID}.brec.tmp

    bash apage.sh ${ID}
    sleep 2
done

exit 0

