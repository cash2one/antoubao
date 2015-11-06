#!/bin/bash

if [ $# -lt 1 ]
then
    echo "Usage: $0 id"
    exit 0
fi

source ./conf.sh

ID=$1

./parse ${ID}
if [ $? -ne 0 ]
then
    echo "`/bin/date "+%Y-%m-%d %H:%M:%S"`, parse ${ID} failed" >>error.log
else
    spi_store data/${ID}
    if [ $? -ne 0 ]
    then
        echo "`/bin/date "+%Y-%m-%d %H:%M:%S"`, store ${ID} faield" >>error.log
    fi
fi

exit 0

