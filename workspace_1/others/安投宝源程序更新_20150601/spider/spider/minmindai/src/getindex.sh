#!/bin/bash

source ./conf.sh

# get index page
>data/id.list.tmp
for ((i=1; i<=3; i++))
do
    "${GETPAGE}" -O - "${INDEXPAGE}/${i}.html" \
        | grep -E "a href=\"\/Lend\/detailpage\/debtid\/[^\"]+\" class=" \
        | sed -r 's/^.+a href=\"\/Lend\/detailpage\/debtid\/([^\"]+)\".+$/\1/' \
        | sort | uniq >>data/id.list.tmp
    sleep 1
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

