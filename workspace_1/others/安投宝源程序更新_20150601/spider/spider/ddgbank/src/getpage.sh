#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}/${ID}.html"
    eval "${GETPAGE1}" -O "html/${ID}" "${URL}"

    URL="${INVESTPAGE}${ID}"
    eval "${GETPAGE1}" -O "html/${ID}.brec" "${URL}"

    bash apage.sh ${ID}

    sleep 2
done

exit 0

