#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	BID=$(echo ${ID} | cut -d '/' -f 2)
	URL="${DETAILPAGE1}${ID}"
	eval "${GETPAGE}" -O - "\"${URL}\"" >>html/${BID}
	PAGENUM=`eval "${GETPAGE}" -O - "\"${URL}\"" | awk '{s=$0;if (match(s, "countpage=\"[0-9]+\"")){printf("%s", substr(s,RSTART+11,RLENGTH-12));}}'`
	PAGENUM=$((${PAGENUM} + 0))
	if [ ${PAGENUM} -eq 0 ]
	then
		PAGENUM=1
	fi
	for((i=1;i<=${PAGENUM};i++))
	do
		URL="${DETAILPAGE2}${i}"
		eval "${GETPAGE}" -O "html/${BID}.brec.tmp" "\"${URL}\"" 
		ls -l html/${BID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${BID}.brec
		cat html/${BID}.brec.tmp >>html/${BID}.brec
		rm html/${BID}.brec.tmp
	done
	bash apage.sh ${BID}
	sleep 2
done
exit 0

