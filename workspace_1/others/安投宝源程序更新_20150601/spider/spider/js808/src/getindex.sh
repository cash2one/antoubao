#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=3;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" --post-data="\"${POSTDATA}${i}${POSTDATA1}}\""\
        | awk '{s=$0; while (match(s, "/newSite/Lend/CreateVote_New.aspx\?id=[0-9]+")) {print substr(s, RSTART+37, RLENGTH-37); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    sleep 1
done

exit 0

