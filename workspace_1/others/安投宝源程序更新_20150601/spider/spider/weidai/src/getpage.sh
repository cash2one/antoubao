#!/bin/bash
source ./conf.sh

# get html page
cat data/id.list | while read ID
do

    URL="${DETAILPAGE}${ID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\"" >html/${ID}
    
    bash apage.sh ${ID}

    sleep 5
done

exit 0

