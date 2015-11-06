#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	URL="${DETAILPAGE1}${ID}"
	eval "${GETPAGE}" -O - "\"${URL}\"" >>html/${ID}
	PAGENUM=$(eval "${GETPAGE}" -O - "\"${DETAILPAGE2}1\"" | awk '{s=$0;if(match(s,"totalPage\":[0-9]+")) {printf("%s\n",substr(s,RSTART+11,RLENGTH-11));}}')
	PAGENUM=$((${PAGENUM} + 0))

	if [ ${PAGENUM} -eq 0 ]
	then
		PAGENUM=1
	fi

	for((i=1;i<=${PAGENUM};i++))
	do
		eval "${GETPAGE}" -O "html/${ID}.brec.tmp" "\"${DETAILPAGE2}${i}\""
		ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
		cat html/${ID}.brec.tmp >>html/${ID}.brec
		rm html/${ID}.brec.tmp
	done
	bash apage.sh ${ID}
	sleep 2
done
exit 0
