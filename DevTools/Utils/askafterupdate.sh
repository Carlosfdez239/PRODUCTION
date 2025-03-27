
FILE_TO_MONITOR="20240605_humidity7h.txt"
CHECK_INTERVAL=10

# Get the initial modification time
LAST_MODIFIED_TIME=$(stat -c %y "$FILE_TO_MONITOR")

while true; do
  # Sleep for the check interval
  sleep $CHECK_INTERVAL

  # Get the current modification time
  CURRENT_MODIFIED_TIME=$(stat -c %y "$FILE_TO_MONITOR")

  # Check if the modification time has changed
  if [[ "$LAST_MODIFIED_TIME" != "$CURRENT_MODIFIED_TIME" ]]; then
    # File has been updated! Take an action (e.g., print message)
    echo "File '$FILE_TO_MONITOR' has been updated!"
    sleep 5
    ../lib/ls_send_message_uart "\x01" /dev/ttyUSB0
    # You can add additional actions here, like processing the file
    LAST_MODIFIED_TIME=$CURRENT_MODIFIED_TIME
  fi
done
