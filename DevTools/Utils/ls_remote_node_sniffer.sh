#!/bin/bash

trap ctrl_c INT

function ctrl_c() { 
    EXIT=1
    kill -9 $SOCAT_PID
}

EXIT=0

if [ $# -ne 1 ]; then
    echo "Usage: $0 TTY_TO_SHARE"
    exit 1 
fi

TTY_TO_SHARE=$1

SHARE_PORT=44400

SOCAT_PID=0
while [ $EXIT -eq 0 ] 
do 
    PIDS_SOCATS_RUNNING=$(ps |grep socat|awk '{print $1;}')
    if [ $(echo $PIDS_SOCATS_RUNNING|grep $SOCAT_PID|wc -l) -eq 0 ]; then
        socat tcp-l:$SHARE_PORT,reuseaddr,fork file:$TTY_TO_SHARE,nonblock,raw,b115200,echo=0 &
        SOCAT_PID=$!
    fi
    sleep 5

done

