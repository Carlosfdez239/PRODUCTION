#!/bin/bash
# Share a node connected to a computer with another one through a socket using socat.
# On the computer that has the node connected execute this script.
# On the computer that wants to use the node, execute the ls_serial_view or 
# ls_serial_view_continuous_reconnect and the desired InMsgs scripts with the option
# -s ip_of_the_server.

trap ctrl_c INT

function ctrl_c() { 
    EXIT=1
    kill -9 $INPUT_PID
    kill -9 $OUTPUT_PID
}

EXIT=0

if [ $# -ne 1 ]; then
    echo "Usage: $0 TTY_TO_SHARE"
    exit 1 
fi

TTY_TO_SHARE=$1

TTY_NUM=$(echo $TTY_TO_SHARE|sed 's/.*[^0-9]\([0-9]*\)$/\1/')
SHARE_PORT_INPUT=$((54400+$TTY_NUM))
SHARE_PORT_OUTPUT=$((54500+$TTY_NUM))

INPUT_PID=0
OUTPUT_PID=0
while [ $EXIT -eq 0 ] 
do 
    PIDS_SOCATS_RUNNING=$(ps |grep socat|awk '{print $1;}')
    if [ $(echo $PIDS_SOCATS_RUNNING|grep $INPUT_PID|wc -l) -eq 0 ]; then
        socat -u tcp-l:$SHARE_PORT_INPUT,reuseaddr,fork file:$TTY_TO_SHARE,nonblock,raw,b115200,echo=0 &
        INPUT_PID=$!
    fi
    if [ $(echo $PIDS_SOCATS_RUNNING|grep $OUTPUT_PID|wc -l) -eq 0 ]; then
        socat -U tcp-l:$SHARE_PORT_OUTPUT,reuseaddr,fork file:$TTY_TO_SHARE,nonblock,raw,echo=0 &
        OUTPUT_PID=$!
    fi
    sleep 5

done

exit 0
