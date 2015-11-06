#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    LTYPE=`echo ${ID} | cut -d '_' -f 1`
    LID=`echo ${ID} | cut -d '_' -f 2`
    URL="${DETAILPAGE}${LID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\"" | iconv -f gbk -t utf-8 >html/${ID}
    eval "${GETPAGE}" -O html/${ID}.brec "\"${INVESTORPAGE}${LID}\""    
    
    bash apage.sh ${ID}

    sleep 2
done

exit 0

