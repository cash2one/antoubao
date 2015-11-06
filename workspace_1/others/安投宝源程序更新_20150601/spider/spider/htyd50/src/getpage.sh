#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
	BID1=$(echo "${ID}" | tr "-" "/")
	BID2=`echo ${ID} | cut -d '-' -f 3`


    URL1="${DETAILPAGE1}${BID1}.html"
    eval "${GETPAGE}" -O - "\"${URL1}\"" > html/"${ID}"
	URL2="${DETAILPAGE2}${BID2}"
	eval "${GETPAGE}" -O - "\"${URL2}\"" > html/"${ID}.breco"
	URL3="${DETAILPAGE3}${BID2}"
	eval "${GETPAGE}" -O - "\"${URL3}\"" > html/"${ID}.brect"
	bash apage.sh ${ID}
    sleep 2
done
exit 0

