#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read AID
do
    ID=`echo ${AID} | cut -d '_' -f 1`
    T=`echo ${AID} | cut -d '_' -f 2`
    URL="${DETAILPAGE}${ID}"
    echo "${T}|" >html/${ID}
    eval "${GETPAGE}" -O - "\"${URL}\"" >>html/${ID}
   
    bash apage.sh ${ID}
    sleep 2
done
exit 0

