#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	URL="${DETAILPAGE1}${ID}"
	eval "${GETPAGE}" -O - "\"${URL}\"" >html/${ID}
	URL="${DETAILPAGE2}1"
	PAGENUM=`eval "${GETPAGE}" -O - "\"${URL}\"" | awk '{if (match($0, "共有[0-9]+页")){printf("%s", substr($0,RSTART,RLENGTH));}}' | sed -r 's/共有([0-9]+)页/\1/g'`
	
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

