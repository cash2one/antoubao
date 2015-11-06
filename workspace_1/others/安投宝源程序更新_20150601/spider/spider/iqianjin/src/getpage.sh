#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    python getpage.py ${ID}
    bash apage.sh ${ID}
    sleep 2
done

exit 0

