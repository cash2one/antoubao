#!/bin/bash

source ./conf.sh

# get html page
cat ${DATADIR}/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}.html"
    eval "${GETPAGE}" -O "${HTMLDIR}/${ID}" "\"${URL}\""
    iconv -f gb2312 -t utf-8 "${HTMLDIR}/${ID}" > "${HTMLDIR}/${ID}.TMP"
        mv "${HTMLDIR}/${ID}.TMP" "${HTMLDIR}/${ID}"

    ./parse ${ID}
    if [ $? -eq 0 ]
    then
        ./store ${ID}
    else
        echo "parse ${ID} failed" >>error.log
    fi
    sleep 2
done

exit 0

