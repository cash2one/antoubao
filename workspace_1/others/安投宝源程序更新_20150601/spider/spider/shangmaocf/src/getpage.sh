#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}.html"
    eval "${GETPAGE}" -O - "\"${URL}\"" | iconv -f gbk -t utf-8 >html/${ID}
    #eval "${GETPAGE}" -O - "\"${INVESTORPAGE}${ID}\"" "--post-data=\"\"" >>html/${ID}

    bash apage.sh ${ID}
    sleep 2
done

exit 0

