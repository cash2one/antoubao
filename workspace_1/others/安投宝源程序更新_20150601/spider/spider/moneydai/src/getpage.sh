#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	URL="${DETAILPAGE1}${ID}.html"
	eval "${GETPAGE}" -O - "\"${URL}\"" >>html/${ID}
	PAGENUM=$(cat html/${ID} | awk '{s=$0;if(match(s,"data-count=\"[0-9]+\"")) {printf("%s",substr(s,RSTART+12,RLENGTH-13));}}')
	PAGENUM=$((${PAGENUM} + 0))
	if [ $PAGENUM -eq 0 ]
	then
		PAGENUM=1
	fi
	URL="${DETAILPAGE2}"
	for((i=1;i<=${PAGENUM};i++))
	do
		URL="${DETAILPAGE2}"
		eval "${GETPAGE}" -O "html/${ID}.brec.tmp" "\"${URL}\"" "--post-data=\"${POSTDATA}\""
		ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
		cat html/${ID}.brec.tmp >>html/${ID}.brec
		rm html/${ID}.brec.tmp
	done
	bash apage.sh ${ID}
	sleep 2
done
exit 0

