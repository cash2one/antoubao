#!/bin/bash

source ./conf.sh

# get html page
MAX_TOTAL=200
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}/${ID}"
    eval "${GETPAGE} --no-check-certificate" -O "html/${ID}" "\"${URL}\""

    > html/${ID}.brec
    eval "${GETPAGE} --no-check-certificate" -O "html/${ID}.brec" --post-data="\"lid=${ID}&p=1&size=${MAX_TOTAL}\"" "\"${INVESTORPAGE}\""

    bash apage.sh ${ID}
    sleep 2
done

