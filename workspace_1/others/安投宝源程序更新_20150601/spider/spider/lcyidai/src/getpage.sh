#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""

    eval "${GETPAGE}" -O -  "\"${INVESTPAGE}?id=${ID}\"" >html/${ID}.brec
    TPAGE1=`cat html/${ID}.brec | awk '{s=$0; while (match(s, "total\".value=\"[0-9]+")) {print substr(s, RSTART+14, RLENGTH-14); s=substr(s, RSTART+1);}}'`
    TPAGE=$(((${TPAGE1}+9)/10))
    >html/${ID}.brec
    for ((i=0;i<=${TPAGE};i++))
    do
        eval "${GETPAGE}" -O - "\"${INVESTPAGE}\"" --post-data="\"id=${ID}&page.size=10&page.total=${TPAGE1}&page.current=${i}\"" >html/${ID}.brec.tmp
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5);}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm -f html/${ID}.brec.tmp
    done

    bash apage.sh ${ID}
    sleep 2
done

exit 0

