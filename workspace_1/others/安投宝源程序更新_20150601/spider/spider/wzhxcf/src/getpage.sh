#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	URL="${DETAILPAGE}${ID}"
	eval "${GETPAGE}" -O - "\"${URL}\"" >html/${ID}
    eval "${GETPAGE}" -O - "\"${DETAILPAGE1}\"">html/${ID}.brec
	bash apage.sh ${ID}
	sleep 2
done
exit 0

