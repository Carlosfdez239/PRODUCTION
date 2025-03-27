#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 <bin to upload> <tty of the serial device>"
    echo "       example: "
    echo "           $0 LoadSensingG_encrypted.bin /dev/ttyUSB0"
else
    FILE2UPLOAD=$1
    TTY=$2
    #echo Force Reboot
    #./ls_send_message_uart "\x09" $TTY
    #sleep 2
    echo Send Password
    echo worldsensing > $TTY
    echo Upload FW by XCOMM
    sx -vv -t 10  $FILE2UPLOAD  < $TTY   > $TTY
fi





