#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	BID=$(echo ${ID} | cut -d '/' -f 2)
	URL="${DETAILPAGE}${ID}"
	eval "${GETPAGE}" -O - "\"${URL}\"" >html/${BID}
	bash apage.sh ${BID}
	sleep 2
done
exit 0

