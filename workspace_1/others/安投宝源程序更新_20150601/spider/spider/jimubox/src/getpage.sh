#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""

    SKIP=0
    IVNUM=`eval "${GETPAGE}" -O - "\"${BRECPAGE}\"" | awk '{if (match($0, "\"total\":[0-9]+")) {print int(substr($0, RSTART+8, RLENGTH-8));}}'`
    TPAGE=$(((${IVNUM}+19)/20))
    >html/${ID}.brec
    for ((i=0;i<${TPAGE};i++))
    do
        SKIP=$((${i}*20))
        eval "${GETPAGE}" -O - "\"${BRECPAGE}\"" >html/${ID}.brec.tmp
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5);}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm -f html/${ID}.brec.tmp
        sleep 1
    done

    bash apage.sh ${ID}

    sleep 2
done

exit 0

