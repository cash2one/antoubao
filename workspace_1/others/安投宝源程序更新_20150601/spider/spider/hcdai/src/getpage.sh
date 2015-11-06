#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    BID=`echo -n ${ID} | base64`    
    
    URL="${BORROWINFO}"
    INFOTIME=`eval "${GETPAGE}" -O - "\"${URL}\"" --post-data="\"borrowInfo.id=${ID}\"" | awk '{if (match($0, "[0-9]+\\\\\\\\/[0-9]+\\\\\\\\/[0-9]+\\\\\\\\/")) {print substr($0,RSTART,RLENGTH);}}' | sed -r 's/\\\\//g'`
    URL="https://www.hcdai.com/file/lend_detail/${INFOTIME}${ID}.html"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    eval "${GETPAGE}" -O html/${ID}.brec "\"${INVESTORPAGE}borrowInfo.id=${ID}\""    
#    eval "${GETPAGE}" -O - "\"\"" "--post-data=\"\"" >>html/${ID}
    

    bash apage.sh ${ID}
    sleep 2
done

exit 0

