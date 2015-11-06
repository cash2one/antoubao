#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    eval "${GETPAGE}" -O - "\"${BRECPAGE}?borrowid=${ID}&page=1\"" >html/${ID}.brec
    TPAGE=`grep -E ',\"pages\":[0-9]+,' html/${ID}.brec | head -n 1 | sed -r 's/^.+,"pages":([0-9]+),.+$/\1/'`
    >html/${ID}.brec
    for ((i=1;i<=${TPAGE};i++))
    do
        eval "${GETPAGE}" -O - "\"${BRECPAGE}?borrowid=${JID}&page=${i}\"" >html/${ID}.brec.tmp
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5);}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm -f html/${ID}.brec.tmp
    done

    bash apage.sh ${ID}

    sleep 2
done

exit 0

