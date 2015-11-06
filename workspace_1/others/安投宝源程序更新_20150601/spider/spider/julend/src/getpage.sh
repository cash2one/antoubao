#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	URL="${DETAILPAGE1}${ID}"
	eval "${GETPAGE}" -O - "\"${URL}\"" >>html/${ID}
	BID=$(cat html/${ID} | grep -E "var bidId = \"" | head -n 1 | sed -r 's/^.*var bidId = \"([a-zA-Z0-9]+).*$/\1/g')
	PAGENUM=$(eval "${GETPAGE}" -O - "\"${DETAILPAGE2}\"" --post-data="\"${POSTDATA2}1\"" \
		| grep -E "if\(currPage > [0-9]+\)" | head -n 1 | sed -r 's/^.*if\(currPage > ([0-9]+)\).*$/\1/g')
	PAGENUM=$((${PAGENUM} + 0))
	if [ ${PAGENUM} -eq 0 ]
	then
		PAGENUM=1
	fi
	for((i=1;i<=${PAGENUM};i++))
	do
		URL="${DETAILPAGE2}"
		eval "${GETPAGE}" -O "html/${ID}.brec.tmp" "\"${URL}\"" --post-data="\"${POSTDATA2}${i}\""
		ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
		cat html/${ID}.brec.tmp >>html/${ID}.brec
		rm html/${ID}.brec.tmp
	done
	bash apage.sh ${ID}
	sleep 2
done
exit 0

