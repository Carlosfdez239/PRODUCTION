#!/usr/bin/python
import datetime
import logging
import os
import signal
import sys
import threading
import time

import serial

sys.path.append("../lib/")
from ls_msg2string import inputmsg2string, msg2string

"""
SerialRcvTask.
Reads messages from serial port. The messages are packetized using the BSC protocol:
  - A DLE STX sequence marks the beginning of the message.
  - A DLE ETX sequence marks the end of the message.
  - Any DLE in the data is doubled.

4 states are defined to control the reception of the messages:
  - STOPPED: nothing is being received. Next expected char DLE.
  - FIRST DLE: Starting DLE received, waiting for a STX.
  - IN MESSAGE: Receiving data characters. A DLE changes the state.
  - DLE IN MESSAGE: One DLE in the data has been received, waiting for the next char:
     - A ETX ends the message
     - A second DLE translates into one DLE char in the data and the state is changed
       back to IN MESSAGE.

Relation between the states:
                           _________
        ----------------->|         |-----------------
        |                 | STOPPED |                |
        |     ----------->|_________|<------------   |
     ETX|     |                   ^              |   |DLE
        |     |!ETX && !DLE       |        !STX  |   |
        |     |  (error)          |       (error)|   |
       _|_____|_                  |            __|___v__
      |         |                 ----------  |         |
      | MSG DLE |             (rcv message |  | 1st DLE |
      |_________|               too long)  |  |_________|
        ^     |                            |         |
        |     |                            |         |
        |     |DLE (Put DLE in rcv buffer) |         |
     DLE|     |            _________       |         |STX
        |     ----------->|         |-------         |
        |                 | IN MSG  |                |
        ------------------|_________|<----------------
                            ^     |
                            |     |!DLE (Put read char in rcv buffer)
                            -------
"""
SERIAL_RCV_STOPPED_STATE = 1
SERIAL_RCV_FIRST_DLE_STATE = 2
SERIAL_RCV_IN_MESSAGE_STATE = 3
SERIAL_RCV_IN_MESSAGE_DLE_STATE = 4

SERIAL_DLE = 16
SERIAL_STX = 2
SERIAL_ETX = 3


def recv_message_from_mota(ser_from, ser_to):
    rcv_state = SERIAL_RCV_STOPPED_STATE
    packet_buffer = b""
    data_read = b""

    while 1:
        data_read = ser_from.read()
        ser_to.write(data_read)
        if rcv_state == SERIAL_RCV_STOPPED_STATE:  # Next expected char: DLE
            if SERIAL_DLE == data_read[0]:
                rcv_state = SERIAL_RCV_FIRST_DLE_STATE
            # else:
            #    print "SerialRcvTask: Unexpected char in state %u. Reset message" % rcv_state
        elif rcv_state == SERIAL_RCV_FIRST_DLE_STATE:  # Next expected char: STX
            if SERIAL_STX == data_read[0]:
                packet_buffer = ""
                rcv_state = SERIAL_RCV_IN_MESSAGE_STATE
            else:
                # print "SerialRcvTask: Unexpected char in state %u. Reset message" % rcv_state
                rcv_state = SERIAL_RCV_STOPPED_STATE
        elif rcv_state == SERIAL_RCV_IN_MESSAGE_STATE:  # Next expected char: STX
            # - DLE if control sequence is present
            # - Data character otherwise
            if SERIAL_DLE == data_read[0]:
                rcv_state = SERIAL_RCV_IN_MESSAGE_DLE_STATE  # First DLE found, change state. */
            else:
                packet_buffer += data_read
        elif rcv_state == SERIAL_RCV_IN_MESSAGE_DLE_STATE:  # Next expected char:
            #  - ETX if end of message
            #  - DLE if DLE is present in the data
            if SERIAL_DLE == data_read[0]:
                # Second DLE found: DLE present in data
                rcv_state = SERIAL_RCV_IN_MESSAGE_STATE
                packet_buffer += data_read
            elif SERIAL_ETX == data_read[0]:
                # DLE ETX found, end of message
                rcv_state = SERIAL_RCV_STOPPED_STATE
                return packet_buffer.decode("utf-8")
            else:
                # print "SerialRcvTask: Unexpected char in state %u. Reset message" % rcv_state
                rcv_state = SERIAL_RCV_STOPPED_STATE
        else:
            logging.error("SerialRcvTask")
            packet_buffer = b""
            return packet_buffer.decode("utf-8")


def get_utc_timestamp():
    d = datetime.datetime.utcnow()
    epoch = datetime.datetime(1970, 1, 1)
    t = int((d - epoch).total_seconds())
    return t


def print_with_mutex(msg):
    global mutex
    mutex.acquire()
    print(msg)
    sys.stdout.flush()
    mutex.release()


def dlog_to_node():
    global dlog_ser
    global node_ser
    while True:
        msg = recv_message_from_mota(dlog_ser, node_ser)
        msg_str = "\nDlog says: [" + str(datetime.datetime.now()) + "] "
        for i in msg:
            msg_str += "%02x " % (ord(i))
        print_with_mutex(msg_str + "\n" + inputmsg2string(msg))


def node_to_dlog():
    global dlog_ser
    global node_ser
    while True:
        msg = recv_message_from_mota(node_ser, dlog_ser)

        msg_str = "\nNode says: [" + str(datetime.datetime.now()) + "] "
        # msg_str="\n[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] "
        for i in msg:
            msg_str += "%02x " % (ord(i))
        print_with_mutex(msg_str + "\n" + msg2string(msg))


def main():

    global mutex
    global dlog_ser
    global node_ser
    mutex = threading.Lock()

    if len(sys.argv) != 3:
        print("Usage: dlog_sniffer.py dlog_tty [node_tty|-sIP]")
        print(
            "       -sIP: Use a socket to connect to a node in a remote computer. IP is the IP of the remote computer"
        )
        print("             The remote computer must execute the ls_remote_node_sniffer.sh script")
        return 1

    dlog_tty = sys.argv[1]
    node_tty = sys.argv[2]

    try:
        dlog_ser = serial.serial_for_url(dlog_tty, 115200)
        if node_tty.startswith("-s"):
            node_ser = serial.serial_for_url("socket://" + node_tty[2:] + ":44400", 115200)
        else:
            node_ser = serial.serial_for_url(node_tty, 115200)
    except Exception as e:
        print("ERROR: Opening serial port " + str(e))
        logging.error("Opening serial port")
        return 1

    threads = []
    t = threading.Thread(target=dlog_to_node)
    threads.append(t)
    t.start()
    t = threading.Thread(target=node_to_dlog)
    threads.append(t)
    t.start()

    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        print("Ctrl-c received! Sending kill to threads...")
        os.kill(os.getpid(), signal.SIGTERM)  # killing threads is hard, let's just commit suicide


if __name__ == "__main__":
    sys.exit(main())
