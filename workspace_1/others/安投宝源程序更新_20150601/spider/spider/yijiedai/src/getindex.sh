#!/bin/bash

source ./conf.sh

# get index page
>data/id.list.tmp
for((i=1;i<=2;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}\"" \
        | awk '{if (match($0, "http://www.yijiedai.com/invest/view/[0-9]+")) {proj=substr($0, RSTART+36, RLENGTH-36); a[proj]="";} if (match($0, "剩余时间")) {if (match($0, "data=\"[0-9]+\"")) {"date +%s" | getline cts; a[proj]=int(substr($0, RSTART+6, RLENGTH-7))+int(cts);}}}END{for (proj in a) print proj"_"a[proj];}' >>data/id.list.tmp
    sleep 1
done

sort data/id.list.tmp | uniq | grep -E -v '^$' >data/id.list

exit 0

