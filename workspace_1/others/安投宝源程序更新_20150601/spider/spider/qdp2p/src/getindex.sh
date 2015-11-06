#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=1;i<=2;i++))
do
     eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}&statusName=&pageSize=20&startBorrowPeriod=&endstartBorrowPeriod=&startRpr=&endRpr=&startBorrowAmount=&endBorrowAmount=&repaymentWayId=\"" \
         | awk '{s=$0; while (match(s, "/borrow/content/[0-9/]+")) {print substr(s, RSTART+16, RLENGTH-16); s=substr(s, RSTART+1);}}'  | sed -r 's/\//_/g' | sort | uniq>>data/id.list
    sleep 1
done

exit 0

