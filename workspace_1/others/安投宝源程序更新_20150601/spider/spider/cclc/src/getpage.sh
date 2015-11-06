#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	BID=$(echo $ID | cut -d '>' -f 1)
	echo "${ID}" | cut -d '>' -f 2 >html/${BID}
	URL="${DETAILPAGE1}${BID}"
	eval "${GETPAGE}" -O - "\"${URL}\"" >>html/${BID}
	value=$(cat html/${BID} | grep -E "id=\"_csrf" | head -n 1 | sed -r 's/^.*value=\"(.+)\".*type=.*$/\1/g' \
		| sed -r 's/\+/%2B/g' | sed -r 's;/;%2F;g'| sed -r 's/=/%3D/g')
	URL="${DETAILPAGE2}"
	TOTAL=$(eval "${GETPAGE}" -O - "\"${URL}\"" "--post-data=\"${POSTDATA1}\"" | awk '{if (match($0, "total\":[0-9]+")){printf("%s", substr($0,RSTART+7,RLENGTH-7));}}')
#	TOTAL=`cat html/${BID}.tmp | awk '{if (match($0, "total\":[0-9]+")){printf("%s", substr($0,RSTART+7,RLENGTH-7));}}'`
#	SIZE=`cat html/${BID}.tmp | awk '{if (match($0, "pagesize\":[0-9]+")){printf("%s", substr($0,RSTART+10,RLENGTH-10));}}'`
	PAGENUM=$(((${TOTAL} + 9) / 10))
	if [ ${PAGENUM} -eq 0 ]
	then
		PAGENUM=1
	fi
	for((i=1;i<=${PAGENUM};i++))
	do
		URL="${DETAILPAGE2}"
		eval "${GETPAGE}" -O "html/${BID}.brec.tmp" "\"${URL}\"" "--post-data=\"${POSTDATA}\""
		ls -l html/${BID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${BID}.brec
		cat html/${BID}.brec.tmp >>html/${BID}.brec
		rm html/${BID}.brec.tmp
	done
	bash apage.sh ${BID}
	sleep 2
done
exit 0

