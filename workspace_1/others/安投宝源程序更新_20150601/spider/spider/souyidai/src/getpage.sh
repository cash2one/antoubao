#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	BID=$(echo ${ID} | cut -d '_' -f 1)
	VID=$(echo ${ID} | sed -r 's/[0-9]+_[^0-9a-zA-Z]+([0-9a-zA-Z]+)/\1/g')
	URL="${DETAILPAGE}${BID}"
	eval "${GETPAGE}" -O - "\"${URL}\"" >html/${VID}
	bash apage.sh ${VID}
	sleep 2
done
exit 0

