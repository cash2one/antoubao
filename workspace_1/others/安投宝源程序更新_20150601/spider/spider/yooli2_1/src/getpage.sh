#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	BID1=$(echo ${ID} | sed -r 's;^.*/dingcunbao/detail/[0-9]+.html.*定存宝 ([a-zA-Z0-9]+).*$;\1;g')
	BID2=$(echo ${ID} | sed -r 's;^.*/dingcunbao/detail/([0-9]+).html.*$;\1;g')
	URL="${DETAILPAGE1}${BID2}.html"
	eval "${GETPAGE}" -O - "\"${URL}\"" >>html/${BID1}
	VID=$(cat html/${BID1} | grep -E "^.*\"financePlanId\"[^0-9]+[0-9]+.*$" | head -n 1 | sed -r 's/^.*\"financePlanId\"[^0-9]+([0-9]+).*$/\1/g')
	PSIZE=$(cat html/${BID1} | grep -E "pageSize.*=.*[0-9]+" | head -n 1 | sed -r 's/^.*pageSize.*=[^0-9]*([0-9]+).*$/\1/g')
	URL="${DETAILPAGE2}"
	PAGENUM=$(eval "${GETPAGE}" -O - "\"${URL}\"" "--post-data=\"${POSTDATA2}1\"" | awk '{s=$0;if(match(s,"pageCount\":[0-9]+")) {printf("%s\n",substr(s,RSTART+11,RLENGTH-11));}}')
	PAGENUM=$((${PAGENUM} + 0))
	if [ ${PAGENUM} -eq 0 ]
	then
		PAGENUM=1
	fi

	for((i=1;i<=${PAGENUM};i++))
	do
		eval "${GETPAGE}" -O "html/${BID1}.brec.tmp" "\"${URL}\"" "--post-data=\"${POSTDATA2}${i}\""
		ls -l html/${BID1}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${BID1}.brec
		cat html/${BID1}.brec.tmp >>html/${BID1}.brec
		rm html/${BID1}.brec.tmp
	done
	bash apage.sh ${BID1}
	sleep 2
done
exit 0
