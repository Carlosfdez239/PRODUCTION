#!/bin/bash

# Executes a sql query predefined or custom on a list of gw. and saves the result in csv.
# Beware of the power of this tool. 

LIB="$(dirname "$0")/lib/ls_gw_utils"
source $LIB

# Number of GW that will be run the query in "parallel"
QUERYXGWINPARALLEL=20

COMMAND="sqlite3 -header -csv /mnt/fsuser-1/ws/opt/dataserver/app/database/production.sqlite \
\"select n.gateway_id, n.serial_number, n.model, n.firmware_version, n.created_at, n.updated_at, m.last_message_received_time, \
cast ((julianDay(m.last_message_received_time) - julianDay(n.created_at)) as integer) as uptime, m.status from nodes n, monitorings m \
where n.serial_number = m.node_id;\""

# Clean up function for the trap
function cleanup {
    local rv=$?
    echo "[CLEANUP] EXIT ($rv)"
    trap - SIGINT SIGTERM EXIT && pkill -P $$ > /dev/null 2>&1
    exit ${rv}
}

# This function executes the sql query on the gw and captures the output to a file GW_ID.csv
function get_nodes_csv
{
    local USER="root"
    local GW_ID=$1
    local GW_PASS=$2

    # Check if we need a TUNNEL or an VPN Connection and execute the cmd in the gw.
    if [ $(get_gw_connection_type $GW_ID) == "TUNNEL" ]; then
        create_ssh_tunnel $GW_ID
        IP="localhost"
        sshpass -p$GW_PASS ssh -p $GW_ID -o LogLevel=ERROR -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $USER@$IP "$COMMAND" > $LOGCSVPATH$GW_ID.csv
    else
        IP=$(get_gw_ip $GW_ID)
	    sshcmd_tunnel_server "-t sshpass -p$GW_PASS ssh -o LogLevel=ERROR -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $USER@$IP '$COMMAND'" > $LOGCSVPATH$GW_ID.csv
    fi
    res=$?
    if [ $res -eq 255 ] || [ $res -eq 1 ]; then
        echo $GW_ID > $LOGOUTPUTPATH"disconnected"
        rm $LOGCSVPATH$GW_ID.csv
    fi
}

# Check for arguments
if [[ ! $# -eq 3 && ! $# -eq 4 ]]; then
    echo "This tool will execute a custom sql query on a list of gw."
    echo "It is important that the path you define for Logs has subfolder csv, errors and output."
    echo 'usage:'
    echo './spidergw.sh list_of_gw_file output_name_file.csv /path/to/Logs/ ["CUSTOM_CMD"]'
    echo 'If you want to use a CUSTOM_CMD you can check out the predefined one inside the code as an example.'
    exit 1
fi

# Trap any exit signal to end any subprocess running.
trap cleanup SIGINT SIGTERM EXIT

# Get arguments
input_file=$1
gateways=$(cat $1)
outputcsv=$2
LOGPATH=$3
# Custom command has been given. Use it instead of default.
if [ "$4" ]; then
    echo "command 4 has been given"
    COMMAND=$4
fi

LOGCSVPATH=$LOGPATH"/csv/"
LOGERRORPATH=$LOGPATH"/errors/"
LOGOUTPUTPATH=$LOGPATH"/output/"

# Go through all list and generate all the csv
i=0
for gateway in $gateways; do
    if [[ "$i" -lt $QUERYXGWINPARALLEL ]]; then
        echo $gateway
        GW_PASS_SSH=$(get_gw_pass_ssh "$gateway")
        get_nodes_csv $gateway $GW_PASS_SSH &
        i=$((i+1))
    else
        wait
        i=0
    fi
done

# Let's filter errors in csv
errors=$(grep -rl "Error" $LOGCSVPATH)
for error in $errors; do
    mv $error $LOGERRORPATH
done

# Wait until all pending queries finish
wait

# Build output csv
o=0
files=$(find $LOGCSVPATH -iname "*.csv")
for filename in $files; do
  if [[ $o -eq 0 ]] ; then
    head -1 $filename > $outputcsv
  fi
  tail -n +2 $filename >> $outputcsv
  o=$(( $o + 1 ))
done
mv $outputcsv $LOGOUTPUTPATH
