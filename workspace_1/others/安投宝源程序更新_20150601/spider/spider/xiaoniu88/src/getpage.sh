#!/bin/bash

source ./conf.sh

# get html page
MAX_TOTAL=1000
cat data/id.list.1 | while read ID
do
    URL="${INDEXPAGE1}/detail/${ID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""

    > html/${ID}.brec
    URL_INVEST="${HOST}/product/detail/${ID}/invest/0/${MAX_TOTAL}"
    eval "${GETPAGE}" -O "html/${ID}.brec" "\"${URL_INVEST}\""

    bash apage.sh ${ID}
    sleep 2
done

cat data/id.list.2 | while read ID
do
    URL="${INDEXPAGE2}/detail/${ID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""

    > html/${ID}.brec
    URL_INVEST="${HOST}/product/detail/${ID}/invest/0/${MAX_TOTAL}"
    eval "${GETPAGE}" -O "html/${ID}.brec" "\"${URL_INVEST}\""
    
    bash apage.sh ${ID}
    sleep 2
done

exit 0

