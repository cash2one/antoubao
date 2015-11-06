#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list.1 | while read ID
do
    URL="${DETAILPAGE1}${ID}"
    "${GETPAGE}" -O "html/${ID}" "${URL}"

    bash apage.sh ${ID}

    sleep 2
done

cat data/id.list.2 | while read ID
do
    URL="${DETAILPAGE2}${ID}"
    "${GETPAGE}" -O "html/${ID}" "${URL}"

    bash apage.sh ${ID}

    sleep 2
done

exit 0

