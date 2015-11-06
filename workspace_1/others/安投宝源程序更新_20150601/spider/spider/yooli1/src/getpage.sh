#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	URL="${DETAILPAGE1}"
	eval "${GETPAGE}" -O - "\"${URL}\"" >>html/${ID}
	BID=$(cat html/${ID} | grep -E "^.*currentProductId\"[^0-9]+[0-9]+[^0-9]+.*$" | head -n 1 | sed -r 's/^.*currentProductId[^0-9]+([0-9]+)[^0-9]+.*$/\1/g')
	URL="${DETAILPAGE2}"
	PAGENUM=$(eval "${GETPAGE}" -O - "\"${URL}\"" "--post-data=\"${POSTDATA1}\"" | awk '{s=$0;if(match(s,"pageCount\":[0-9]+")) {printf("%s\n",substr(s,RSTART+11,RLENGTH-11));}}')

	for((i=1;i<=${PAGENUM};i++))
	do
		eval "${GETPAGE}" -O "html/${ID}.brec.tmp" "\"${URL}\"" "--post-data=\"${POSTDATA2}\""
		ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
		cat html/${ID}.brec.tmp >>html/${ID}.brec
		rm html/${ID}.brec.tmp
	done
	bash apage.sh ${ID}
	sleep 2
done
exit 0

