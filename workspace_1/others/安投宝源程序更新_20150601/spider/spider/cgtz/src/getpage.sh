#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	URL="${DETAILPAGE1}${ID}"
	eval "${GETPAGE}" -O - "\"${URL}\"" >>html/${ID}
	BID=$(cat html/${ID} | grep -E "id\":[0-9]+" | sed -r 's/^.+id\":([0-9]+).+$/\1/')
	PAGENUM=`eval "${GETPAGE}" -O - "\"${DETAILPAGE2}1\"" | grep  "尾页" | sed -r 's/^.*loadTransaction\(([0-9]+)\).*$/\1/g'`
	if test -z "${PAGENUM}"
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

