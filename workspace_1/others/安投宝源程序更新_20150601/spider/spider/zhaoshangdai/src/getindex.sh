#!/bin/bash

source ./conf.sh

# get index page
eval "${GETPAGE}" -O - "\"${INDEXPAGE1}\"" "\"${INDEXPAGE2}\"" \
    | grep -E 'a href=\"/invest/detail\.html\?borrowid=[^\"]+\"' \
    | sed -r 's/^.+a href=\"\/invest\/detail\.html\?borrowid=([^\"]+)\".+$/\1/' \
    | sort | uniq >data/id.list.tmp
touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

