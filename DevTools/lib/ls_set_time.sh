#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 <seconds since epoch> <tty of the serial device>"
    echo "       example: "
    echo "           $0 `date +%s` /dev/ttyUSB0"
fi

#echo date +%s|xargs printf '%08x'|sed 's/\(..\)/\\x\1/g'
TIME_IN_HEXA=$(printf '%08x' $1 | sed 's/\(..\)/\\x\1/g')

cd `dirname $0`
./ls_send_message_uart "\x05"$TIME_IN_HEXA $2



