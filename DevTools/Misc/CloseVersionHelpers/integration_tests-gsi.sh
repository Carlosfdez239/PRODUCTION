#!/bin/bash
TTY="/dev/ttyUSB0"
SCR_SEND="./ls_send_message_uart"
OUT_FOLD="./results/"
SCR_SETTIME="./ls_set_time.sh"
SCR_SEND20GSIDATA="./test_send20GSIData.sh"
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
    sleep 20
}

function IT_Reboot() {
    IT_PrintTimestamp "REBOOT"
    $SCR_SEND "\x09" $TTY
    sleep 20
}
function IT_FactoryReset() {
    IT_PrintTimestamp "FACTORY RESET"
    $SCR_SEND "\x08\x75\xB5\x44\xA2" $TTY
    sleep 20
}
function IT_GetDataInterval() {
    IT_PrintTimestamp "GET DATA INTERVAL"
    $SCR_SEND "\x04" $TTY
    sleep 10
}
function IT_RecoverAllData() {
    IT_PrintTimestamp "RECOVER ALL DATA"
    $SCR_SEND "\x03\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF" $TTY
    sleep 1
}
function IT_SetConfig_Default() {
    IT_PrintTimestamp "SET CONFIG DEFAULT"
    $SCR_SEND "\x91\x00\x00\x42\x00\x00\x00\x20\x00\x00\x03" $TTY
    sleep 2
    $SCR_SEND "\x82\x00\x07\x08" $TTY
    sleep 2
}

function IT_SetConfig_30Minutes() {
    IT_PrintTimestamp "SET CONFIG 30 MINUTES"
    $SCR_SEND "\x91\x00\x00\x42\x00\x00\x00\x20\x00\x00\x03" $TTY
    sleep 2
    $SCR_SEND "\x82\x00\x00\xF0" $TTY
    sleep 2
}
function IT_SetConfig_OneDay() {
    IT_PrintTimestamp "SET CONFIG ONE_DAY"
    $SCR_SEND "\x91\x00\x00\x42\x00\x00\x00\x20\x00\x00\x03" $TTY
    sleep 2
    $SCR_SEND "\x82\x01\x51\x80" $TTY
    sleep 2
}

function IT_SetConfigs_Radio_FCC() {
    IT_PrintTimestamp "SET LoRa Keys Config - 13000"
    $SCR_SEND "\x8D\x80\x35\xB9\x27\xFF\x73\x49\x96\x84\x1D\x69\xD2\x5A\x09\xAA\xE6\xDE\x0D\xAE\x06\xBA\xB2\x38\x73\xF1\x89\x0D\xBC\x77\xB4\x6E\x1F\x00\x00\x32\xC8\x96\x96" $TTY
    sleep 2
    IT_PrintTimestamp "SET LoRa General FCC Config"
    $SCR_SEND "\x84\x02\x58\x14\x0C\x30\xE0\x35\x00\x00\x0F" $TTY
    sleep 2
}

IT_PrintStartTest "DATA STORAGE - Store and retrieve Data"
IT_SetTime 1000
IT_FactoryReset
IT_SetConfig_OneDay
IT_SetConfigs_Radio_FCC

echo 1
IT_GetDataInterval

echo 2
IT_RecoverAllData

echo 3
IT_PrintTimestamp "SEND GET 20 GSI DATA "
$SCR_SEND20GSIDATA $TTY

echo 4
IT_GetDataInterval

echo 5
IT_RecoverAllData

echo 6
IT_PrintTimestamp "RECOVER ALL HEALTH"
$SCR_SEND "\x03\x40\x00\x00\x00\x00\xFF\xFF\xFF\xFF" $TTY
sleep 1

echo 7
IT_PrintTimestamp "RECOVER GSI DATA"
$SCR_SEND "\x03\x42\x00\x00\x00\x00\xFF\xFF\xFF\xFF" $TTY
sleep 10

echo 8
IT_PrintTimestamp "RECOVER ALL DATA 900-1300"
$SCR_SEND "\x03\x00\x00\x00\x03\x84\x00\x00\x05\x14" $TTY
sleep 10

echo 9
IT_PrintTimestamp "RECOVER ALL DATA 1200-1500"
$SCR_SEND "\x03\x00\x00\x00\x04\xb0\x00\x00\x05\xdc" $TTY
sleep 20

echo 10 
IT_PrintTimestamp "RECOVER ALL DATA 1400-INF"
$SCR_SEND "\x03\x00\x00\x00\x05\x78\xff\xff\xff\xff" $TTY
sleep 20

echo 11
IT_SetTime 800

sleep 12
IT_PrintTimestamp "SEND GET 20 GSI DATA "
$SCR_SEND20GSIDATA $TTY

echo 13
IT_SetTime 1300

sleep 14
IT_PrintTimestamp "SEND GET 20 GSI DATA "
$SCR_SEND20GSIDATA $TTY

echo 15
IT_GetDataInterval

echo 16
IT_PrintTimestamp "RECOVER ALL DATA 700-1300"
$SCR_SEND "\x03\x00\x00\x00\x02\xbc\x00\x00\x05\x14" $TTY
sleep 20

echo 17
IT_PrintTimestamp "RECOVER ALL DATA 1200-1500"
$SCR_SEND "\x03\x00\x00\x00\x04\xb0\x00\x00\x05\xdc" $TTY
sleep 20

echo 18
IT_PrintTimestamp "RECOVER ALL DATA 1450-INF"
$SCR_SEND "\x03\x00\x00\x00\x05\xaa\xff\xff\xff\xff" $TTY
sleep 20




#IT_FactoryReset

