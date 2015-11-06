#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}/${ID}.html"
    eval "${GETPAGE}" -O "html/${ID}" "${URL}"

    URL="${DETAILPAGE}/${ID}.html"
    INVEST_PAGE=`"${GETPAGE}" -O - "${URL}" \
        | awk '{s=$0; while (match(s, "class=\"pages\" style=\"width:930px; margin-left:0;\">共 ([0-9]+)")) {print substr(s, RSTART+54, RLENGTH-54); s=substr(s, RSTART+1);}}' | sort | uniq`

    >"html/${ID}.brec"
    for ((i=1; i<=${INVEST_PAGE}; i++))
    do
        URL="${INVESTPAGE}${ID}&p=${ID}"
        "${GETPAGE}" -O - "${URL}" >> "html/${ID}.brec"
    done

    bash apage.sh ${ID}

    sleep 2
done

exit 0

