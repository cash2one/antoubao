#!/bin/bash

echo $$ >spider.running

source ./conf.sh

bash getindex.sh
sleep 5

bash getpage.sh
sleep 5

rm spider.running

exit 0

