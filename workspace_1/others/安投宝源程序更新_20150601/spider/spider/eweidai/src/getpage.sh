#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}.html"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    eval "${GETPAGE}" -O -  "\"http://www.eweidai.com/invst/queryInvestPageInvestspd3.action?&currentPage=1&productid=${ID}\"" >html/${ID}.brec
    #TPAGE1=`grep -E '\"recordCounts\":[0-9]+' html/${ID}.brec | head -n 1 | sed -r 's/^.\"recordCounts\":([0-9]+).+$/\1/'`
    TPAGE1=`cat html/${ID}.brec | awk '{s=$0; while (match(s, "\"recordCounts\":[0-9]+")) {print substr(s, RSTART+15, RLENGTH-15); s=substr(s, RSTART+1);}}'`
    TPAGE=$(((${TPAGE1}+9)/10))
    >html/${ID}.brec
    for ((i=1;i<=${TPAGE};i++))
    do
        eval "${GETPAGE}" -O - "\"http://www.eweidai.com/invst/queryInvestPageInvestspd3.action?currentPage=${i}&productid=${ID}\"" >html/${ID}.brec.tmp
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5);}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm -f html/${ID}.brec.tmp
    done

    bash apage.sh ${ID}
    sleep 2
done

exit 0

