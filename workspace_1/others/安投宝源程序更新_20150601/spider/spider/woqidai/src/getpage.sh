#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    BID=`echo -n ${ID} | base64`    

    URL="${DETAILPAGE}${ID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""

    URL="http://www.woqidai.com/api/Investment/ProjectInfoV2?project_no=${ID}"
    PROID=`eval "${GETPAGE}" -O - "\"${URL}\"" | awk '{s=$0; while (match(s, "\"project_id\":\"[0-9a-z]+.[0-9a-z]+.[0-9a-z]+.[0-9a-z]+.[0-9a-z]+")) {print substr(s, RSTART+14, RLENGTH-14); s=substr(s, RSTART+1);}}'`
    URL="${INVESTORPAGE}${PROID}"
    eval "${GETPAGE}" -O "html/${ID}.brec" "\"${URL}\""
#    eval "${GETPAGE}" -O "html/${ID}.brec" "\"${INVESTORPAGE}borrowInfo.id=${ID}\""    
#    eval "${GETPAGE}" -O - "\"\"" "--post-data=\"\"" >>html/${ID}
    

    bash apage.sh ${ID}
    sleep 2
done

exit 0

