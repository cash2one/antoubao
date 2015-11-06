#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	URL="${DETAILPAGE1}${ID}"
	eval "${GETPAGE}" -O - "\"${URL}\"" >html/${ID}
	PAGENUM=`eval "${GETPAGE}" -O - "\"${URL}\"" | awk '{if (match($0, "加入人次[^0-9]+[0-9]+")){print substr($0,RSTART,RLENGTH);}}' | cut -d '(' -f 2` 
	PAGENUM=$(((${PAGENUM}+24)/25))
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
