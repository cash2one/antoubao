#!/bin/bash

source ./conf.sh

# get index page
>data/id.list.tmp.1
for ((i=1; i<=3; i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE1}&curPage=${i}\"" \
        | grep -E "a href=\"financeDetail\.do\?id=[^\"]+\"" \
        | sed -r 's/^.+a href=\"financeDetail\.do\?id=([^\"]+)\".+$/\1/' \
        | sort | uniq >>data/id.list.tmp.1
    sleep 1
done

touch data/id.list.old.1
sort data/id.list.tmp.1 data/id.list.old.1 | uniq >data/id.list.1
mv data/id.list.tmp.1 data/id.list.old.1


>data/id.list.tmp.2
for ((i=1; i<=3; i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE2}&curPage=${i}\"" \
        | grep -E "a href=\"currentInvestInit\.do\?id=[^\"]+\"" \
        | sed -r 's/^.+a href=\"currentInvestInit\.do\?id=([^\"]+)\".+$/\1/' \
        | sort | uniq >>data/id.list.tmp.2
    sleep 1
done

touch data/id.list.old.2
sort data/id.list.tmp.2 data/id.list.old.2 | uniq >data/id.list.2
mv data/id.list.tmp.2 data/id.list.old.2


exit 0

