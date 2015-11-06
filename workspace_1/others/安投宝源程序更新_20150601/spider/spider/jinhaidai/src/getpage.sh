#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	URL="${DETAILPAGE}""1"
	eval "${GETPAGE}" -O - "\"${URL}\"" >html/${ID}
	PAGENUM=`eval "${GETPAGE}" -O - "\"${URL}\"" | awk '{if (match($0, "CInvest_page=[0-9]+\">末页")){printf("%s", substr($0,RSTART,RLENGTH));}}' | cut -d '=' -f 2 | cut -d '"' -f 1`
	PAGENUM=`expr "${PAGENUM}"`
	if [ ${PAGENUM} -eq 0 ]
	then
		PAGENUM=1
	fi
	for((i=1;i<=${PAGENUM};i++))
	do
		URL="${DETAILPAGE}${i}"
		eval "${GETPAGE}" -O "html/${ID}.brec.tmp" "\"${URL}\""
		ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
		cat html/${ID}.brec.tmp >>html/${ID}.brec
		rm html/${ID}.brec.tmp
	done
	bash apage.sh ${ID}
	sleep 2
done
exit 0

