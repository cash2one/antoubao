#!/bin/bash

source ./conf.sh

>data/id.list
eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" \
    | awk '{s=$0; while (match(s, "Details.aspx\\?borrowId=[0-9]+")) {print substr(s, RSTART+22, RLENGTH-22); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list


exit 0

