i=0
while [ $i -ne 100 ];
do
    if [ 0 -eq `expr $i % 10` ];
    then
        echo $i
    fi
#./ls_send_message_uart "\xd1\x15\x59\xad\x01" /dev/ttyUSB1
./ls_send_message_uart "\x01" /dev/ttyUSB0
i=$(($i+1))
done
