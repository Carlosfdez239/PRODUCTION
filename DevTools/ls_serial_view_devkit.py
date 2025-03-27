#!/usr/bin/env python3
import logging
import sys

import serial

msg2string = None  # TODO remove when exec changed
exec(open("lib/ls_msg2string.py").read())

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


def recv_message_from_mota(ser):
    rcv_state = SERIAL_RCV_STOPPED_STATE
    packet_buffer = ""
    data_read = ""

    while True:
        data_read = ser.read()
        if rcv_state == SERIAL_RCV_STOPPED_STATE:  # Next expected char: DLE
            if SERIAL_DLE == ord(data_read):
                rcv_state = SERIAL_RCV_FIRST_DLE_STATE
            # else:
            #    print "SerialRcvTask: Unexpected char in state %u. Reset message" % rcv_state
        elif rcv_state == SERIAL_RCV_FIRST_DLE_STATE:  # Next expected char: STX
            if SERIAL_STX == ord(data_read):
                packet_buffer = ""
                rcv_state = SERIAL_RCV_IN_MESSAGE_STATE
            else:
                # print "SerialRcvTask: Unexpected char in state %u. Reset message" % rcv_state
                rcv_state = SERIAL_RCV_STOPPED_STATE
        elif rcv_state == SERIAL_RCV_IN_MESSAGE_STATE:  # Next expected char: STX
            # - DLE if control sequence is present
            # - Data character otherwise
            if SERIAL_DLE == ord(data_read):
                rcv_state = SERIAL_RCV_IN_MESSAGE_DLE_STATE  # First DLE found, change state. */
            else:
                packet_buffer += data_read
        elif rcv_state == SERIAL_RCV_IN_MESSAGE_DLE_STATE:  # Next expected char:
            #  - ETX if end of message
            #  - DLE if DLE is present in the data
            if SERIAL_DLE == ord(data_read):
                # Second DLE found: DLE present in data
                rcv_state = SERIAL_RCV_IN_MESSAGE_STATE
                packet_buffer += data_read
            elif SERIAL_ETX == ord(data_read):
                # DLE ETX found, end of message
                rcv_state = SERIAL_RCV_STOPPED_STATE
                return packet_buffer
            else:
                # print "SerialRcvTask: Unexpected char in state %u. Reset message" % rcv_state
                rcv_state = SERIAL_RCV_STOPPED_STATE
        else:
            logging.error("SerialRcvTask")
            packet_buffer = ""
            return packet_buffer


def main():
    dev_tty = sys.argv[1]
    try:
        ser = serial.serial_for_url(dev_tty, 9600)
    # happens when the installed pyserial is older than 2.5. use the Serial class directly then.
    except AttributeError:
        ser = serial.Serial(dev_tty, 9600)
        try:
            ser.open()
        except Exception as e:
            print(f"ERROR: Opening serial port {e}")
            logging.error("Opening serial port")
            return 1
    while True:
        msg = recv_message_from_mota(ser)
        msg_str = "\n"
        for i in msg:
            msg_str += "%02x " % (ord(i))
        print(msg_str)

        print(msg2string(msg))

        sys.stdout.flush()


if __name__ == "__main__":
    sys.exit(main())
