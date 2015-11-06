#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""

    URL="${INVESTORPAGE}"
    eval "${GETPAGE}" -O - "\"${URL}\"" --post-data="\"loanId=${ID}\"" >>html/${ID}

    bash apage.sh ${ID}
    sleep 2
done

exit 0

