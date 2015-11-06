#!/bin/bash

source ./conf.sh

# get index page
>data/id.list
for ((i=1;i<=3;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" \
        | grep -E 'a href=\"/invest/[a-zA-Z0-9]+\.html\"' \
        | sed -r 's/^.+a href=\"\/invest\/([a-zA-Z0-9]+)\..+$/\1/' \
        | sort | uniq >>data/id.list
    sleep 1
done

exit 0

