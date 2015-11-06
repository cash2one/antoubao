#!/bin/bash

source ./conf.sh

# get html page
cat data/id.list | while read ID
do
    ID1=`echo ${ID} | sed 's/_/\//g'`
    TYPE=`echo ${ID1} |  awk '{if (match($0, "[a-z]+\/[a-z]+\/[a-z0-9]+")) {print substr($0,RSTART,RLENGTH);}}' | sed -r 's/^[a-z]+\/[a-z]+\/([0-9a-z]+)$/\1/g'`
    URL="${DETAILPAGE}/${ID1}"
    eval "${GETPAGE}" -O "html/${ID}" "\"${URL}\""
    BID=`echo ${ID1} |  awk '{if (match($0, "[a-z]+\/[a-z]+\/[a-z0-9]+")) {print substr($0,RSTART,RLENGTH);}}' | sed -r 's/^([a-z]+)\/[a-z]+\/[0-9a-z]+$/\1/g'`
    if [ ${BID} = trade ]
    then
       BID=4
    fi
    if [ ${BID} = loan ] 
    then
       BID=2
    fi
    if [ ${BID} = project ]
    then
        BID=1
    fi
    URL="${INVESTORPAGE}${BID}"
    PAGENUM=$((`eval "${GETPAGE}" -O - "\"${URL}\"" --post-data="\"page=1&encrypt_id=${TYPE}\"" | awk '{if (match($0, "共([0-9]+)页")) {print substr($0,RSTART,RLENGTH);}}' | sed -r 's/^共([0-9]+)页$/\1/g' | sort -g`))
     if [ $PAGENUM -lt 1 ]
     then
         PAGENUM=1
     fi
     >html/${ID}.brec
     for ((j=1;j<=${PAGENUM};j++))
     do
         URL="${INVESTORPAGE}${BID}"
         eval "${GETPAGE}" -O - "\"${URL}\"" --post-data="\"page=${PAGENUM}&encrypt_id=${TYPE}\"" >html/${ID}.brec.tmp
         ls -l html/${ID}.brec.tmp | awk '{printf("%08X", $5)}' >>html/${ID}.brec
         cat html/${ID}.brec.tmp >>html/${ID}.brec
         rm html/${ID}.brec.tmp
     done

     bash apage.sh ${ID}
     sleep 2
 done

 exit 0
