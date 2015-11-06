#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	URL="${DETAILPAGE1}${ID}"
	eval "${GETPAGE}" -O - "\"${URL}\"" >>html/${ID}
	value=$(cat html/${ID} | grep -E "name=\"loanId\" value=\"[0-9a-zA-Z]+\">" | sed -r "s/^.*name=\"loanId\" value=\"([0-9a-zA-Z]+)\">.*$/\1/g")
	TOTAL=$(cat html/${ID} | grep -E "id=\"creditTotalCnt\" value=\"[0-9]+\">" | sed -r 's/^.*id="creditTotalCnt" value="([0-9]+)">.*$/\1/g')
	PAGESIZE=$(cat html/${ID} | grep -E "id=\"creditPageSize\" value=\"[0-9]+\">" | sed -r 's/^.*id="creditPageSize" value="([0-9]+)">.*$/\1/g')
	if [ -z ${value} ] || [ -z ${TOTAL} ] || [ -z ${PAGESIZE} ]
	then
		continue
	fi
	PAGENUM=$(((${TOTAL} + ${PAGESIZE} - 1) / ${PAGESIZE}))
	if [ ${PAGENUM} -eq 0 ]
	then
		PAGENUM=1
	fi
	for((i=1;i<=${PAGENUM};i++))
	do
		URL="${DETAILPAGE2}"
		eval "${GETPAGE}" -O "html/${ID}.brec.tmp" "\"${URL}\"" "--post-data=\"${POSTDATA2}\""
		ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
		cat html/${ID}.brec.tmp >>html/${ID}.brec
		rm html/${ID}.brec.tmp
	done
	bash apage.sh ${ID}
	sleep 2
done
exit 0

