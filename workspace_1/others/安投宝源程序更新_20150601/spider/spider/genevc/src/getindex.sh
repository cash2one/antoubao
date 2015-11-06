#!/bin/bash

source ./conf.sh

>data/id.list
   eval "${GETPAGE}" -O - "\"${INDEXPAGE}\"" \
        | awk '{s=$0; while (match(s, "m=invest&action=detail&id=[0-9]+")) {print substr(s, RSTART+26, RLENGTH-26); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    

exit 0

