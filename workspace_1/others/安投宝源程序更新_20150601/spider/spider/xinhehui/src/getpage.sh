#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	TYPE=`echo $ID | cut -d '_' -f 1`
	BID=`echo $ID | cut -d '_' -f 2`

	if [ "$TYPE" != "3" ]
	then
		URL="${DETAILPAGE1}${BID}"
		eval "${GETPAGE}" -O - "\"${URL}\"" >html/${BID}
		URL="${DETAILPAGE_1}"
		PAGENUM=$((`eval "${GETPAGE}" -O - "\"${URL}\"" | awk '{if (match($0, "[0-9]+</a> <a href.*下一页")) {print substr($0,RSTART,RLENGTH);}}' | cut -d '<' -f 1 ` +0)) 
		if [ ${PAGENUM} -eq 0 ]
		then
			PAGENUM=1
		fi
		for((i=1;i<=${PAGENUM};i++))
		do
			URL="${DETAILPAGE}${i}"
			eval "${GETPAGE}" -O "html/${BID}.brec.tmp" "\"${URL}\""
			ls -l html/${BID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${BID}.brec
			cat html/${BID}.brec.tmp >>html/${BID}.brec
			rm html/${BID}.brec.tmp
		done

	else
		URL="${DETAILPAGE2}${BID}"
		eval "${GETPAGE}" -O - "\"${URL}\"" >html/${BID}
		URL="${DETAILPAGE_1}"
		PAGENUM=$((`eval "${GETPAGE}" -O - "\"${URL}\"" | awk '{if (match($0, "[0-9]+</a> <a href.*下一页")) {print substr($0,RSTART,RLENGTH);}}' | cut -d '<' -f 1 ` +0))
		if [ ${PAGENUM} -eq 0 ]
		then
			PAGENUM=1
		fi
		for((i=1;i<=${PAGENUM};i++))
		do
			URL="${DETAILPAGE}${i}"
			eval "${GETPAGE}" -O "html/${BID}.brec.tmp" "\"${URL}\""
			ls -l html/${BID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${BID}.brec
			cat html/${BID}.brec.tmp >>html/${BID}.brec
			rm html/${BID}.brec.tmp
		done

	fi

   
    bash apage.sh ${BID}
    sleep 2
done
exit 0

