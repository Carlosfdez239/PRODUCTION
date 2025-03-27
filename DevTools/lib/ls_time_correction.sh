#!/bin/bash

if [ $# -ne 4 ]; then
    echo "Usage: $0 <sign> <correction> <token> <tty of the serial device>"
    echo "       example: "
    echo "           $0 `date +%s` /dev/ttyUSB0"
fi

#echo date +%s|xargs printf '%08x'|sed 's/\(..\)/\\x\1/g'
TIME_IN_HEXA=$(printf '%02x%08x%08x' $1 $2 $3| sed 's/\(..\)/\\x\1/g')
echo "#$TIME_IN_HEXA#" > /tmp/kkk.$$

cd `dirname $0`
./ls_send_message_uart "\x0C"$TIME_IN_HEXA $4



