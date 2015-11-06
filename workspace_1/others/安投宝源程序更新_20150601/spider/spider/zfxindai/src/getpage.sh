#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do

	TYPE=`echo ${ID} | cut -d '_' -f 1`
	BID=`echo ${ID} | cut -d '_' -f 2`
	eval "${GETPAGE}" -O html/${ID} "\"${DETAILPAGE[${TYPE}]}${BID}.html\""

    bash apage.sh ${ID}
    sleep 2
done
exit 0


