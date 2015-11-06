#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    eval "${GETPAGE}" -O "html/${ID}" "\"${DETAILPAGE}\""
    TPAGE=$((`grep -E '共 [0-9]+ 页' html/${ID} | sed -r 's/^.+共 ([0-9]+) 页.+$/\1/'`+0))
    if [ $TPAGE -lt 1 ]
    then
        TPAGE="1"
    fi
    >html/${ID}.brec
    for ((i=1;i<=${TPAGE};i++))
    do
        eval "${GETPAGE}" -O - "\"${BRECPAGE}${i}\"" >html/${ID}.brec.tmp
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5);}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm -f html/${ID}.brec.tmp
    done

    bash apage.sh ${ID}

    sleep 2
done

exit 0

