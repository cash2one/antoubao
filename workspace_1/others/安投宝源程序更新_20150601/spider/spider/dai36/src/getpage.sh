#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}"
    eval "${GETPAGE1}" -O "html/${ID}" "${URL}"

    # get invest page num
    invest_num=`cat "html/${ID}" | awk '{s=$0; if (match(s, "<i class=\"toinvslC\">([0-9]+)</i>")) {print substr(s, RSTART+20, RLENGTH-24);}}'`
    page_num=`echo "${invest_num}/10+1" | bc`

    # get invest detail
    > "html/${ID}.brec"
    for ((i=1; i<=$page_num; i++))
    do
        eval "${GETPAGE1}" -O - "\"${INVESTORPAGE}\"" --post-data="\"beginDate=&endDate=&currentPage=${i}&summaryState=-1&bidRequestId=${ID}\"" \
            | awk '{if(match($0, "<td>.+</td>")) {print substr($0, RSTART, RLENGTH);}}' >> "html/${ID}.brec"
    done

    bash apage.sh ${ID}

    sleep 2
done

exit 0

