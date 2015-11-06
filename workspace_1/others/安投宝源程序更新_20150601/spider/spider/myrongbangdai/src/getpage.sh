#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID

do
	URL="${DETAILPAGE1}${ID}"
	eval "${GETPAGE}" -O - "\"${URL}\"" >>html/${ID}
	URL="${DETAILPAGE2}"
	eval "${GETPAGE}" -O "html/${ID}.brec" "\"${URL}\"" "--post-data=\"${POSTDATA2}\""
	bash apage.sh ${ID}
	sleep 2
done
exit 0

