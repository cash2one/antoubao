
#!/bin/bash

source ./conf.sh

>${DATADIR}/id.list
for ((i=1;i<3;i++))
do
    eval "${GETPAGE}" -O - "\"${INDEXPAGE}${i}.html\"" \
        | awk '{s=$0; while (match(s, "/invest/[0-9|a-z]+")) {print substr(s, RSTART+8, RLENGTH-8); s=substr(s, RSTART+1);}}' | sort | uniq>>${DATADIR}/id.list
    sleep 1
done

exit 0
