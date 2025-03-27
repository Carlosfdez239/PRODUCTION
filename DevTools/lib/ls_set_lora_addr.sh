#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 <LoRa MAC Address> <tty of the serial device>"
fi

TIME_IN_HEXA=$(printf '%08x' $1 | sed 's/\(..\)/\\x\1/g')

cd `dirname $0`
./ls_send_message_uart "\x83"$TIME_IN_HEXA $2



