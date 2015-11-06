#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}.html"
    eval "${GETPAGE}" -O - "\"${URL}\"" | iconv -f gbk -t utf-8 >html/${ID}
    TTOTAL=`eval "${GETPAGE}" -O - "\"${DETAILPAGE}${ID}.html\"" | awk '{if (match($0,"id=\"people\">[0-9]+")) {print substr($0, RSTART+12, RLENGTH-12);}}'`
    TPAGE=$(((${TTOTAL}+9)/10))
    
    >html/${ID}.brec
    for ((i=1;i<=${TPAGE};i++))
    do
        eval "${GETPAGE}" -O - "\"http://www.dtd365.com/invest/a${ID}.html?&in_ajax=1&page=${i}\"" | iconv -f gbk -t utf-8 >html/${ID}.brec.tmp
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5);}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm -f html/${ID}.brec.tmp
    done

    bash apage.sh ${ID}
    sleep 2
done

exit 0

