#!/bin/bash

source ./conf.sh
# get index page
>data/id.list.tmp

echo "jijin" >>data/id.list.tmp

touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0

