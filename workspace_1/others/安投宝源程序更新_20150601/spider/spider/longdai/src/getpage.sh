#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}"

    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""

    TPAGE=`eval "${GETPAGE}" -O - "\"${INVESTORPAGE}\"" --post-data="\"planId=${ID}&pageBean.pageNum=1\"" | awk '{if (match($0,"\"totalPageNum\":[0-9]+")) {print substr($0, RSTART+15, RLENGTH-15);}}'`
    >html/${ID}.brec
    for ((i=1;i<=${TPAGE};i++))
    do
        eval "${GETPAGE}" -O - "\"${INVESTORPAGE}\"" --post-data="\"planId=${ID}&pageBean.pageNum=${i}\"" >html/${ID}.brec.tmp
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5);}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm -f html/${ID}.brec.tmp
    done
   
    bash apage.sh ${ID}
    sleep 2
done

exit 0

