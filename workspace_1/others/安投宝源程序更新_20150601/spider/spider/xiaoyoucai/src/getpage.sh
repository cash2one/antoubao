#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	URL="${DETAILPAGE1}${ID}"
	eval "${GETPAGE}" -O - "\"${URL}\"" >html/${ID}
	URL="${DETAILPAGE3}"
	eval "${GETPAGE}" -O - "\"${URL}\"" >html/${ID}.tmp
	PAGENUM1=`cat html/${ID}.tmp  | awk '{if (match($0, "total\":[0-9]+")){print substr($0,RSTART+7,RLENGTH-7);}}'`
	PAGENUM2=`cat html/${ID}.tmp  | awk '{if (match($0, "pgCount\":[0-9]+")){print substr($0,RSTART+9,RLENGTH-9);}}'`

	PAGENUM=$(((${PAGENUM1}+${PAGENUM2}-1)/${PAGENUM2}))
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
