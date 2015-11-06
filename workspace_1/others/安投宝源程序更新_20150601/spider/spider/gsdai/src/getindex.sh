#!/bin/bash

source ./conf.sh

# get index page
>data/id.list.tmp
for ((i=0; i<=20; i=i+10))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" \
        | grep -E "href=\"/borrow/obj/[^\"]+\"" \
        | sed -r 's/^.+a href=\"\/borrow\/obj\/([^\"]+)\".+$/\1/' \
        | sort | uniq >>data/id.list.tmp
    sleep 1
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old


exit 0

