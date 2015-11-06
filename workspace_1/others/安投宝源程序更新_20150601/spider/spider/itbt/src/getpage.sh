#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    URL="${DETAILPAGE}${ID}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    URL="${INVESTORPAGE}"
    SNUM=`cat html/${ID} | awk '{if (match($0, "编号# [0-9]+")) {print substr($0,RSTART,RLENGTH);}}' | sed -r 's/^[^0-9]+([0-9]+)/\1/g'`
    ALLNUM=$((`eval "${GETPAGE}" -O - "\"${URL}\"" --post-data="\"${INVPOSTDATA}1${INVPOSTDATA1}${SNUM}\"" | awk '{s=$0; while (match(s, "\"Total\":\"[0-9]+")) {allnum=substr(s,RSTART,RLENGTH); s=substr(s, RSTART+1);}}END{print allnum;}' | sed -r 's/^[^0-9]+([0-9]+)$/\1/g'`))
    PAGENUM=$(((${ALLNUM}+9)/10))
    if [ $PAGENUM -lt 1 ]
    then
        PAGENUM=1
    fi
    >html/${ID}.brec
    for ((j=1;j<=${PAGENUM};j++))
     do
     URL="${INVESTORPAGE}" 
     eval "${GETPAGE}" -O - "\"${URL}\""  --post-data="\"${INVPOSTDATA}${j}${INVPOSTDATA1}${SNUM}\"" >>html/${ID}.brec.tmp      
        ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
        cat html/${ID}.brec.tmp >>html/${ID}.brec
        rm html/${ID}.brec.tmp
    done

    bash apage.sh ${ID}
    sleep 2
done

exit 0

