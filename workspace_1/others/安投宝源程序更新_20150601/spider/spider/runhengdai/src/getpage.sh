#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}.html"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    
    URL="https://member.runhengdai.com/invest/profile-bid_${ID}.html"
    eval "${GETPAGE}" -O "html/${ID}.borrower" "\"${URL}\""
    
    eval "${GETPAGE}" -O - "\"https://member.runhengdai.com/invest/investrecord-bid_${ID}-pageid_1.html\"" >html/${ID}.brec
    TPAGE=`grep -E '条 [0-9]+ 页' html/${ID}.brec | head -n 1 | sed -r 's/^.+条 ([0-9]+) 页.+$/\1/'`
    >html/${ID}.brec
    for ((i=1;i<=${TPAGE};i++))
    do
        eval "${GETPAGE}" -O - "\"https://member.runhengdai.com/invest/investrecord-bid_${ID}-pageid_${i}.html\"" >html/${ID}.brec.tmp
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5);}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm -f html/${ID}.brec.tmp
    done

    bash apage.sh ${ID}
    sleep 2
done

exit 0

