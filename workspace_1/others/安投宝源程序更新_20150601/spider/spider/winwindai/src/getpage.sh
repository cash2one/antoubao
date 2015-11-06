#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list.1 | while read ID
do
    URL="${DETAILPAGE1}${ID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    eval "${GETPAGE}" -O - "${INVESTORPAGE}" --post-data="paramMap.id=${ID}" >html/${ID}.brec

    bash apage.sh ${ID}

    sleep 2
done

cat data/id.list.2 | while read ID
do
    URL="${DETAILPAGE2}${ID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    #eval "${GETPAGE}" -O - "${INVESTORPAGE}" --post-data="paramMap.id=${ID}" >html/${ID}.brec

    bash apage.sh ${ID}

    sleep 2
done

exit 0

