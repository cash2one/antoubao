
#!/bin/bash

source ./conf.sh

>data/id.list
for ((i=0;i<=3;i++))
do
    a=`expr ${i} \* 5`
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${a}&multiple=true\"" \
        | awk '{s=$0; while (match(s, "/invest/view/[0-9]+")) {print substr(s, RSTART+13, RLENGTH-13); s=substr(s, RSTART+1);}}' | sort | uniq>>data/id.list
    sleep 1
done

exit 0
