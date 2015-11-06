#!/bin/bash

source ./conf.sh

# get index page
for ((i=1;i<=10;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" \
        | grep -E 'a href="/invest/[0-9]+.html"' \
        | sed -r 's/^.+a href="\/invest\/([0-9]+)\.html".+$/\1/' \
        | sort | uniq >>data/id.list.tmp
    sleep 1
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

