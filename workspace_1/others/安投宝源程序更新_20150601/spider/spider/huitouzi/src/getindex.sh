#!/bin/bash

source ./conf.sh

>data/id.list.tmp

        eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" \
            | awk '{s=$0; while (match(s, "project/htzxprojectdetail/[0-9]+")) {print substr(s, RSTART+26, RLENGTH-26); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list.tmp
    sheep 2;

    touch data/id.list.old
sort data/id.list.tmp data/id.list.old | uniq >data/id.list
mv data/id.list.tmp data/id.list.old

exit 0
