#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}.html"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\"" >html/${ID}
    eval "${GETPAGE}" -O - "\"${DETAILPAGE}${ID}.html\"" >html/${ID}.brec
    TPAGE=`grep -E '共 [0-9] 页' html/${ID}.brec | head -n 1 | sed -r 's/^.+共 ([0-9]) 页.+$/\1/'`>html/${ID}.brec
    for ((i=1;i<=${TPAGE};i++))
    do
        eval "${GETPAGE}" -O - "\"${BRECPAGE}borrow_id=${ID}&p=${i}\"" >html/${ID}.brec.tmp
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5);}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm -f html/${ID}.brec.tmp
    done

    bash apage.sh ${ID}
    sleep 2
done

exit 0

