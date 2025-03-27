i=0
while [ $i -ne 100 ];
do
./ls_send_message_uart "\x02" $1
i=$(($i+1))
sleep 6
done
