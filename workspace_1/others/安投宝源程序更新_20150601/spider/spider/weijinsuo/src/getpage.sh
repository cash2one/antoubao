#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do

	TYPE=`echo ${ID} | cut -d '_' -f 1`
	BID=`echo ${ID} | cut -d '_' -f 2`
	eval "${GETPAGE}" -O html/${ID} "\"${DETAILPAGE1[$TYPE]}\"" "--post-data=\"${DETAILPOST[$TYPE]}\""
    eval "${GETPAGE}" -O html/${ID}.brec "\"${DETAILPAGE2[$TYPE]}\"" "--post-data=\"${DETAILPOST[0]}\""

    bash apage.sh ${ID}
    sleep 2
done
exit 0


