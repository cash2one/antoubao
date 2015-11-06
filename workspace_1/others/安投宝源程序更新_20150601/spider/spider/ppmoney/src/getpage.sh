#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	BID=$(echo ${ID} | cut -d '/' -f 2)
	eval "${GETPAGE}" -O - "\"${DETAILPAGE_MONEY}\"" | awk '{s=$0;if(match(s,"CirculationMoney\":\"[0-9]+")) {printf("%s",substr(s,RSTART+19,RLENGTH-19));}}' >>html/${BID}
	URL="${DETAILPAGE1}${ID}"
	eval "${GETPAGE}" -O - "\"${URL}\"" >>html/${BID}
	URL="${DETAILPAGE}"
	TOTAL=$(eval "${GETPAGE}" -O - "\"${URL}\"" | awk '{s=$0;if(match(s,"TotalCount\":[0-9]+")) {printf("%s\n",substr(s,RSTART+12,RLENGTH-12));}}')
	TOTAL=$((${TOTAL} + 0))
	PAGENUM=$(((${TOTAL} + 14) / 15))

	if [ ${PAGENUM} -eq 0 ]
	then
		PAGENUM=1
	fi

	for((i=1;i<=${PAGENUM};i++))
	do
		eval "${GETPAGE}" -O "html/${BID}.brec.tmp" "\"${DETAILPAGE2}\""
		ls -l html/${BID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${BID}.brec
		cat html/${BID}.brec.tmp >>html/${BID}.brec
		rm html/${BID}.brec.tmp
	done
	bash apage.sh ${BID}
	sleep 2
done
exit 0
