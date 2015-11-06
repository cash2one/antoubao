#!/bin/bash

source ./conf.sh

# get index page
>data/id.list.tmp
for URL in ${INDEXPAGE}
do
    wget -O - "${URL}" | awk '{if (match($0, "Detail\.aspx\?sid=[0-9]+")) {print substr($0, RSTART+16, RLENGTH-16);}}' >>data/id.list.tmp
done

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

