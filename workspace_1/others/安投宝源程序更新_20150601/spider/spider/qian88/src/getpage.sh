#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    
    #eval "${GETPAGE}" -O - "\"${INVESTORPAGE}\"" "--post-data=\"${POSTDATA}\"" >>html/${ID}.brec
    eval "${GETPAGE}" -O "html/${ID}.brec" "\"${INVESTORPAGE}\"" --post-data="${POSTDATA}"

    bash apage.sh ${ID}

    sleep 2
done

exit 0
