#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	URL="${DETAILPAGE1}${ID}.html"
	eval "${GETPAGE}" -O - "\"${URL}\"" >>html/${ID}
	PAGENUM=`cat html/${ID} | grep -E '共[^0-9]*[0-9]+[^0-9]*页' | head -n 1 | sed -r 's/^.*共[^0-9]*([0-9]+)[^0-9]*页.*$/\1/g'`
	PAGENUM=$((${PAGENUM} + 0))
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

