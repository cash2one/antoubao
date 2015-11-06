#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    eval "${GETPAGE}" -O "html/${ID}" "\"${DETAILPAGE}${ID}\""

    bash apage.sh ${ID}

    sleep 5
done

exit 0

