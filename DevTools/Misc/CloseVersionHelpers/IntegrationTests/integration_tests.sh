#!/bin/bash
TTY="/dev/ttyUSB0"
SCR_SEND="./ls_send_message_uart"
OUT_FOLD="./results/"
SCR_SETTIME="./ls_set_time.sh"
function IT_PrintTimestamp() {
TIMESTAMP=$(date +[%D-%T])
    echo $TIMESTAMP $1:
}
function IT_PrintStartTest() {
TIMESTAMP=$(date +[%D' '%T.%6N])
    echo "#####################################################"
    echo $TIMESTAMP $1
}
function IT_SetTime() {
if [ $# = 1 ]; then
    TIME=$1
else
    TIME=$(date +%s)
fi
    IT_PrintTimestamp "SET TIME $TIME"
    $SCR_SETTIME $TIME $TTY
    sleep 10
}

function IT_Reboot() {
    IT_PrintTimestamp "REBOOT"
    $SCR_SEND \x09 $TTY
    sleep 10
}
function IT_FactoryReset() {
    IT_PrintTimestamp "FACTORY RESET"
    $SCR_SEND \x08\x75\xB5\x44\xA2 $TTY
    sleep 10
}
function IT_GetDataInterval() {
    IT_PrintTimestamp "GET DATA INTERVAL"
    $SCR_SEND \x04 $TTY
    sleep 1
}
function IT_SetConfig_Default() {
    IT_PrintTimestamp "SET CONFIG DEFAULT"
    $SCR_SEND \x81\x42\x00\x00\x00\x20\x00\x00\x03 $TTY
    $SCR_SEND \x82\x00\x00\xF0 $TTY
    sleep 1
}


REBOOT="$SCR_SEND \x09 $TTY; sleep 10"
FACTORY_RESET="$SCR_SEND \x08\x75\xB5\x44\xA2 $TTY; sleep 10"

IT_PrintTimestamp "DATA STORAGE - Store and retrieve Data"
IT_SetTime 1000
IT_SetTime
#IT_FactoryReset

