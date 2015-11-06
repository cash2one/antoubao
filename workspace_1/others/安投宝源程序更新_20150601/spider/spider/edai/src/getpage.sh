#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}.html"
    eval "${GETPAGE}" -O - "\"${URL}\"" | iconv -f gbk -t utf-8 >html/${ID}

    TTOTAL=`eval "${GETPAGE}" -O - "\"${INVESTORPAGE}\"" --post-data="\"page=1&epage=20&borrow_nid=${ID}&order=tender_addtime\"" | awk '{if (match($0,"\"total\":[0-9]+")) {print substr($0, RSTART+8, RLENGTH-8);}}'`
    TPAGE=$(((${TTOTAL}+19)/20))

    >html/${ID}.brec
    for ((i=1;i<=${TPAGE};i++))
    do
        eval "${GETPAGE}" -O - "\"${INVESTORPAGE}\"" --post-data="\"page=${i}&epage=20&borrow_nid=${ID}&order=tender_addtime\"" >html/${ID}.brec.tmp
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5);}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm -f html/${ID}.brec.tmp
    done
   
    bash apage.sh ${ID}
    sleep 2
done

exit 0

