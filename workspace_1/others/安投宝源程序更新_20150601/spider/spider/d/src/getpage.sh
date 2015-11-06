#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	eval "${GETPAGE}" -O - "\"${DETAILPAGE2}1\"" >>html/${ID}.tmp
	PAGENUM=`cat html/${ID}.tmp| awk '{s=$0;if (match(s, "page_total\":[0-9]+")){printf("%s", substr(s,RSTART+12,RLENGTH-12));}}'`
	TOTAL=`cat html/${ID}.tmp| awk '{s=$0;if (match(s, "total\":\"[0-9]+")){printf("%s", substr(s,RSTART+8,RLENGTH-8));}}'`
	LASTPAGENUM=$((${TOTAL} - (${PAGENUM} - 1) * 100))
	echo ${LASTPAGENUM} | awk '{printf("%08X",$0)}' >>html/${ID}
    echo ${PAGENUM} | awk '{printf("%08X",$0)}' >>html/${ID}
	echo "%#%" >>html/${ID}
	eval "${GETPAGE}" -O - "\"${DETAILPAGE_MONEY}\"" | awk '{s=$0;if(match(s,"tendermoney\":\"[0-9]+")) {printf("%s\n",substr(s,RSTART+14,RLENGTH-14));}}' >>html/${ID}
	URL="${DETAILPAGE1}${ID}.html"
	eval "${GETPAGE}" -O - "\"${URL}\"" >>html/${ID}


	if [ ${PAGENUM} -eq 0 ]
	then
		PAGENUM=1
	fi
	for((i=1;i<=${PAGENUM};i++))
	do
		URL="${DETAILPAGE2}${i}"
		eval "${GETPAGE}" -O "html/${ID}.brec.tmp" "\"${URL}\"" 
		ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
		cat html/${ID}.brec.tmp >>html/${ID}.brec
		rm html/${ID}.brec.tmp
	done
	bash apage.sh ${ID}
	sleep 2
done
exit 0

