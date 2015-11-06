#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}.html"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    >html/${ID}.brec
	TOTAL=$(cat html/${ID} | grep -E "投标次数[^0-9]+[0-9]+</span>" | sed -r 's;^.*投标次数[^0-9]+([0-9]+)</span>.*$;\1;g')
	PAGENUM=$(((${TOTAL} + 17) / 18))
	if [ ${PAGENUM} -eq 0 ]
	then
		PAGENUM=1
	fi
    for ((j=1;j<=${PAGENUM};j++))
    do
        URL="${INVESTORPAGE}${j}"
        eval "${GETPAGE}" -O "html/${ID}.brec.tmp" "\"${URL}\""      
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm html/${ID}.brec.tmp
        sleep 1
    done

    bash apage.sh ${ID}
    sleep 2
done

exit 0

