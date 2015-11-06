#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}.html"
    eval "${GETPAGE}" -O - "\"${URL}\"" | iconv -f gb2312 -t utf-8 >html/${ID}
    #    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    bash apage.sh ${ID}

    sleep 2
done

exit 0

