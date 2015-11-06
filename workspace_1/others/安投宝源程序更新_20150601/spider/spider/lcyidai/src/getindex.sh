#!/bin/bash

source ./conf.sh

# get index page
>data/id.list.tmp

    eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" --header="\"Referer:http://www.lcyidai.com:81/website/borrowInvestMainList.action\?borrowLoanMain.status=\"" --post-data="\"${POSTDATA}\""\
		| awk '{s=$0; while (match(s, "id=\"spanLjtbID[0-9]+")) {print substr(s, RSTART+14, RLENGTH-14); \
		s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
    sleep 1

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

