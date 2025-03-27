#!/usr/bin/env python3
import datetime
import logging
import re
import sys

sys.path.append("./lib/")
import ls_msg2string as ls_msg2string
import serial  # from pyserial, avoid installing just 'serial' package (errors)
import serialbsc as serialbsc


def get_utc_timestamp():
    d = datetime.datetime.utcnow()
    epoch = datetime.datetime(1970, 1, 1)
    t = int((d - epoch).total_seconds())
    return t


def main():
    dev_tty = sys.argv[1]
    one_line_flag = False
    use_socket = False
    if len(sys.argv) == 3:
        if "-l" == sys.argv[2]:
            one_line_flag = True
    if len(sys.argv) == 4:
        if "-s" == sys.argv[2]:
            use_socket = True
            server_ip = sys.argv[3]
    if len(sys.argv) == 5:
        if "-l" == sys.argv[2]:
            one_line_flag = True
        if "-s" == sys.argv[3]:
            use_socket = True
            server_ip = sys.argv[4]
    if use_socket is False:
        try:
            ser = serialbsc.open_serial(dev_tty, baudrate=115200)
        except Exception as e:
            print("ERROR: Opening serial port " + str(e))
            logging.error("Opening serial port")
            return 1
    else:  # use socket instead of serial device
        port_num = str(int(re.search(r"(\d+)$", dev_tty).group(0)) + 54500)
        ser = serial.serial_for_url("socket://" + server_ip + ":" + port_num, 115200)

    while True:
        msg_dict = serialbsc.rcv_message_from_mote(ser)
        msg = msg_dict["Data"]
        if one_line_flag:
            msg_str = "" + str(get_utc_timestamp()) + ";" + str(datetime.datetime.now()) + "; "
            for i in msg:
                msg_str += "%02x " % (i)
            msg_str += ";" + ls_msg2string.msg2string(msg)
            print(msg_str)
        else:
            msg_str = "\n[" + str(datetime.datetime.now()) + "] "
            # msg_str="\n[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] "
            for i in msg:
                msg_str += "%02x " % (i)
            print(msg_str)
            print(ls_msg2string.msg2string(msg))
        sys.stdout.flush()


if __name__ == "__main__":
    sys.exit(main())
