#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    eval "${GETPAGE}" -O -  "\"${BRECPAGE}pid=${ID}&currpage=1\"" >html/${ID}.brec
    TPAGE1=`cat html/${ID}.brec | awk '{s=$0; while (match(s, "\"allnum\":[0-9]+")) {print substr(s, RSTART+9, RLENGTH-9); s=substr(s, RSTART+1);}}'`
    TPAGE=$(((${TPAGE1}+9)/10))
    >html/${ID}.brec
    for ((i=1;i<=${TPAGE};i++))
    do
        eval "${GETPAGE}" -O - "\"${BRECPAGE}pid=${ID}&currpage=${i}\"" >html/${ID}.brec.tmp
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5);}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm -f html/${ID}.brec.tmp
    done

    bash apage.sh ${ID}
    sleep 2
done

exit 0

