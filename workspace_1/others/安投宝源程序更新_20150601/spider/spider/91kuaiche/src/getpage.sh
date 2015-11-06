#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	BID=$(echo ${ID} | cut -d '/' -f 2)
	URL="${DETAILPAGE1}${ID}.html"
	eval "${GETPAGE}" -O - "\"${URL}\"" >>html/${BID}
	NUM=$(cat html/${BID} | grep -E "investCount\"\).html\(" | head -n 1 | sed -r 's/^.*investCount\"\).html\(([0-9]+).*$/\1/g')
	PAGENUM=$(((${NUM} + 11) / 12))
	PAGENUM=$((${PAGENUM} + 0))

	if [ ${PAGENUM} -eq 0 ]
	then
		PAGENUM=1
	fi
	URL=${DETAILPAGE2}
	for((i=0;i<${PAGENUM};i++))
	do
		startnum=$((${i} * 12))
		eval "${GETPAGE}" -O "html/${BID}.brec.tmp" "\"${URL}\"" "--post-data=\"${POSTDATA2}\""
		ls -l html/${BID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${BID}.brec
		cat html/${BID}.brec.tmp >>html/${BID}.brec
		rm html/${BID}.brec.tmp
	done
	bash apage.sh ${BID}
	sleep 2
done
exit 0
