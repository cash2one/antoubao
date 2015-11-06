#!/bin/bash

source ./conf.sh

# get index page
>data/id.list.tmp
for ((i=1; i<=3; i++))
do
    "${GETPAGE}" -O - "${INDEXPAGE}" --post-data="type=wantinvest&currentPage=${i}&pageSize=20&cmd=listDetail&status=2&bidRequestType=-1"  \
        | grep -E "href=\"borrowinfo\.htm\?fromUrl=&jid=[^\"]+\"" \
        | sed -r 's/^.+href=\"borrowinfo\.htm\?fromUrl=&jid=([^\"]+)\".+$/\1/' \
        | sort | uniq >>data/id.list.tmp
    sleep 1

    "${GETPAGE}" -O - "${INDEXPAGE}" --post-data="type=wantinvest&currentPage=${i}&pageSize=20&cmd=listDetail&status=0,6,12&bidRequestType=-1" \
        | grep -E "href=\"borrowinfo\.htm\?fromUrl=&jid=[^\"]+\"" \
        | sed -r 's/^.+href=\"borrowinfo\.htm\?fromUrl=&jid=([^\"]+)\".+$/\1/' \
        | sort | uniq >>data/id.list.tmp
    sleep 1

    "${GETPAGE}" -O - "${INDEXPAGE}" --post-data="type=wantinvest&currentPage=${i}&pageSize=20&cmd=listDetail&status=8,9&bidRequestType=-1" \
        | grep -E "href=\"borrowinfo\.htm\?fromUrl=&jid=[^\"]+\"" \
        | sed -r 's/^.+href=\"borrowinfo\.htm\?fromUrl=&jid=([^\"]+)\".+$/\1/' \
        | sort | uniq >>data/id.list.tmp
    sleep 1
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

