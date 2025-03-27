while :
do
	../lib/ls_send_message_uart "\x01" /dev/ttyUSB0
	sleep 0.1
done
