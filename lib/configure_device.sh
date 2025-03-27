#!/bin/bash

configure_device() {
    local device_name="$1"
    local prefix=""
    
    case "$device_name" in
        "VIB")
            prefix="\x13\x20\x85\x5E\x14\x00\x56"
            ;;
        "TIL")
            prefix="\x13\x20\x85\x5E\x14\x00\x58"
            ;;
        *)
            printf "Invalid device name\n"
            exit 1
            ;;
    esac

    read -p "Introduce el número de serie: " serial_number
    echo "Configurando $device_name con serial number $serial_number ..."

    # Convert to hexadecimal and pad it with zeros to reach 8 characters
    serial_number_hexa=$(printf '%08x\n' "$serial_number")

    # Get the string size
    size=${#serial_number_hexa}

    # This check is probably unnecessary now as the size will always be 8, 
    # but I'll keep it just in case.
    if [ "$size" -lt 1 ] || [ "$size" -gt 8 ]; then
        printf "Invalid number\n"
        exit 1
    fi

    # Build the message
    local message="$prefix"
    
    for ((i=1; i<=$size; i+=2)); do
        message+="\x${serial_number_hexa:$i-1:2}"
    done

    echo $message
    sleep 1
    ./lib/ls_send_message_uart "$message" /dev/ttyUSB0
    sleep 1
    printf "Message: "

    for ((i = 1; i <= "$size"; i+=2)); do
        printf "0x${serial_number_hexa:$i-1:2} "
    done

    printf "\nSeteando ID...\n"
    sleep 1
}

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <device_name>"
    exit 1
fi

configure_device "$1"


