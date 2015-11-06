#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	BID=$(echo ${ID} | sed -r 's;^.*detail/([0-9]+).html.*$;\1;g')
	URL="${DETAILPAGE1}${ID}"
	eval "${GETPAGE}" -O - "\"${URL}\"" >>html/${BID}
	VID=$(cat html/${BID} | grep -E "^.*\"financePlanVId\"[^0-9]+[0-9]+.*$" | head -n 1 | sed -r 's/^.*\"financePlanVId\"[^0-9]+([0-9]+).*$/\1/g')
	PSIZE=$(cat html/${BID} | grep -E "pageSize.*=.*[0-9]+" | head -n 1 | sed -r 's/^.*pageSize.*=.*([0-9]+).*$/\1/g')
	URL="${DETAILPAGE2}"
	PAGENUM=$(eval "${GETPAGE}" -O - "\"${URL}\"" "--post-data=\"${POSTDATA2}1\"" | awk '{s=$0;if(match(s,"pageCount\":[0-9]+")) {printf("%s\n",substr(s,RSTART+11,RLENGTH-11));}}')
	PAGENUM=$((${PAGENUM} + 0))
	if [ ${PAGENUM} -eq 0 ]
	then
		PAGENUM=1
	fi

	for((i=1;i<=${PAGENUM};i++))
	do
		eval "${GETPAGE}" -O "html/${BID}.brec.tmp" "\"${URL}\"" "--post-data=\"${POSTDATA2}${i}\""
		ls -l html/${BID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${BID}.brec
		cat html/${BID}.brec.tmp >>html/${BID}.brec
		rm html/${BID}.brec.tmp
	done
	bash apage.sh ${BID}
	sleep 2
done
exit 0
