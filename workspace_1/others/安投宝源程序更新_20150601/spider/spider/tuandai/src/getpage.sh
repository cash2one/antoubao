#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}?id=${ID}"
    ${GETPAGE} -O "html/${ID}" "${URL}"

    ${GETPAGE} -O "html/${ID}.brec" "${INVESTORPAGE}" --post-data="Cmd=GetSubscribePageList&projectid=${ID}&pageindex=1&pagesize=500"

    bash apage.sh ${ID}
    sleep 2
done

