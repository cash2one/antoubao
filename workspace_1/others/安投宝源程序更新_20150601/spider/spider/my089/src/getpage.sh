#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}"
    wget -O "html/${ID}" "${URL}"

    URL="${INVESTORPAGE}${ID}"
    wget -O "html/${ID}.brec" "${URL}"

    bash apage.sh ${ID}

    sleep 2
done

exit 0

