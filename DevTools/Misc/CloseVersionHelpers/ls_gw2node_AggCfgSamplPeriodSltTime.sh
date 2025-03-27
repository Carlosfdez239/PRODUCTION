#!/bin/bash
GW_ID=$1
NODE_MAC_ADDR=$2
SAMPLING_PERIOD=$3
SLOT_TIME=$4

if [ $# -ne 4 ]; then
   echo "Usage $0 <gw_id> <node_mac> <sampling_period> <slot_time>"
   exit 1
fi

HEXPARAM1=$(java -jar InMsgs/jars/SamplingPeriodSlotTimeAggCfg.jar "${SAMPLING_PERIOD}" "${SLOT_TIME}")
PAYLOAD=$(echo -ne ${HEXPARAM1} | base64)
./ls_ssh_gw ${GW_ID} root "/mnt/fsuser-1/ws/bin/python /root/send_udp.py ${NODE_MAC_ADDR} ${PAYLOAD}"
