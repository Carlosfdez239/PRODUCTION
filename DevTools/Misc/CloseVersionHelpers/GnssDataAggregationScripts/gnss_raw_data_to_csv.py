#!/usr/bin/env python3

"""
Script used to receive GNSS Raw Data from the serial port and store it in a CSV file.
This scripts just listens to the serial port, so you have to start the GNSS Raw Data recovery process
with RecoverData devtool.
Execute this script with the following command:
./gnss_raw_data_to_csv.py /dev/ttyUSB0

It is stored in the gnss_raw_data.csv file.
"""

import csv
import datetime
import json as _json
import logging as _logging
import struct as _struct
import sys
from collections import defaultdict

import ls_message_parsing

ls_message_parsing.SHOW_HIDDEN_FIELDS = True
from ls_message_parsing.ls_message_parsing import decode_msg as _decode_msg

sys.path.append("../../../lib/")
import serialbsc as serialbsc


def set_prcode_nodeid(prcode, moteid):
    global PRCODE, NODEID
    PRCODE = prcode
    NODEID = moteid


def msg2json(binary_msg):
    msg = None
    # It will be required to pass radio metadata if no changes are done in the parsing library
    # meta = RadioMetadata.RadioMetadata(12345, "12345", 1547200203000, -73, 11, "ETSIV1", 68157505, 869.525, 7, "01")
    try:
        out = _decode_msg(binary_msg)
        msg = out.get_decoded_message_dict()
        # Hack to be able to differentiate health v2 and v3
        if msg["type"] == "healthV2":
            amtype = int(binary_msg[5])
            if amtype == 79:
                msg["type"] = "healthV3"
    except Exception:
        # _logging.error(binary_msg)
        # _logging.error(e)
        # raise NameError("Could not parse received message")
        pass
    if msg is None:
        assert False  # This should not happen
        # msg = _msg2json_old(binary_msg)
    return msg


def _get_sane_format(msg_type, json_data):
    return None


def _json2string(json_msg, msg_type=None):
    beautified_string = _get_sane_format(msg_type, json_msg)
    if beautified_string:
        return beautified_string
    else:
        for key, value in json_msg.items():
            if isinstance(value, bytes):
                # Decode bytes to string
                json_msg[key] = value.hex()
        json_string = _json.loads(_json.dumps(json_msg))
        return "; ".join([f"{el}: {json_string[el]}" for el in json_string])


def _get_recover_data(msg):
    json_msg = {}
    mote_id_lower_16 = NODEID & 0xFFFF  # Mask the frist 16 bits
    most_significant_4 = (NODEID >> 16) & 0x0F  # Extract bits 16 to 20 (4 bits)
    # Construct the first byte (header + 4 lower bits from NODEID)
    first_byte = 0x40 | most_significant_4
    # Construct the dummy header
    dummy_header_bytes = (
        bytes([first_byte])  # First byte with NODEID bits
        + bytes([PRCODE])  # PRCODE (1 byte)
        + mote_id_lower_16.to_bytes(2, byteorder="big")  # Last 16 bits of NODEID
        + b"\xf8"  # needed for the parsing lib, as here we don't have this part of the message
    )
    unp_msg = _struct.unpack("!BB", msg[:2])
    data_type = unp_msg[1]
    msg_str = "; CaptureId: %u; " % (unp_msg[0])
    decoded_msg_str, json_msg = _get_type_msg_str(data_type, msg[2:])
    if "Unknown" in decoded_msg_str:  # TODO: This should be implemented in the parsing library.
        try:
            json_msg = msg2json(
                dummy_header_bytes + msg[1:]
            )  # we skip the capture id to allow a message to be parsed
            decoded_msg_str = _json2string(json_msg)
        except Exception:
            print("ERROR unpacking message")

    return (msg_str + decoded_msg_str, json_msg)


def _get_response_str(msg):
    unp_msg = _struct.unpack("!H", msg)
    response = unp_msg[0]
    if response == 0:
        response_str = "OK"
    elif response == 1:
        response_str = "ERR_INVALID_MSG_SIZE"
    elif response == 2:
        response_str = "ERR_INVALID_PARAMETER"
    elif response == 3:
        response_str = "ERR_RESET"
    elif response == 4:
        response_str = "ERR_NO_CONFIG"
    elif response == 5:
        response_str = "ERR_UNKNOWN_COMMAND"
    elif response == 6:
        response_str = "ERR_NOT_SUPPORTED"
    elif response == 7:
        response_str = "ERR_CMD_FAILED"
    elif response == 127:
        response_str = "RESTART_RECOVERY"
    elif response == 128:
        response_str = "END_OF_DATA_RECOVERY"
    elif response == 129:
        response_str = "END_OF_LORA_COV_TEST"
    else:
        response_str = "Unknown: %u" % (response)
    return response_str


def _get_type_msg_str(msg_type, msg):
    msg_dic = {}
    if msg_type == 0:
        type_msg_str = "Response " + _get_response_str(msg)
    elif msg_type == 1:
        type_msg_str, msg_dic = _get_recover_data(msg)
        type_msg_str = "Recover Data " + type_msg_str
    else:
        type_msg_str = "Unknown   "

    return type_msg_str, msg_dic


def _msg2string_old(msg):
    msg_str = ""
    msg_dic = {}
    try:
        unp_header_and_type = _struct.unpack("!BBHBB", msg[:6])

        if (unp_header_and_type[0] & 0x40) != 0x40:
            _logging.error("Invalid header")
        else:
            prcode = unp_header_and_type[1]
            mote_id = ((unp_header_and_type[0] & 0x0F) << 16) + unp_header_and_type[2]
            set_prcode_nodeid(prcode, mote_id)
            num_seq = unp_header_and_type[3]

            type_msg_str, msg_dic = _get_type_msg_str(unp_header_and_type[4], msg[6:])

            msg_str = (
                "PrCode: "
                + str(prcode)
                + "; ID: "
                + str(mote_id)
                + "; #Seq: "
                + str(num_seq)
                + "; "
                + type_msg_str
            )

    except _struct.error:
        print("ERROR unpacking message")
        _logging.error("Parsing msg")
        msg_str = ""
        for i in msg:
            msg_str += "%02x " % (ord(i))
        _logging.debug(msg_str)

    return (msg_str, msg_dic)


timestamp_data = defaultdict(list)


def store_reading(msg_dic):
    # For now reserved=0 means rtk fix. reserved=1 means gps fix. It should be handled properly by the parsing library.
    if msg_dic["reserved"] != 0:
        return

    read_timestamp = msg_dic["readTimestamp"]
    if "1970-" in read_timestamp:
        return
    frame_number = msg_dic["frameNumber"]
    readings = msg_dic["readings"]

    timestamp_data[read_timestamp].append({"frameNumber": frame_number, "readings": readings})


def generate_csv():
    # Prepare rows for CSV
    rows = []

    # Create the CSV header
    header = ["readTimestamp"]
    raw_sample_num = 0
    while True:
        raw_data_header = [
            f"raw{raw_sample_num}_lat",
            f"raw{raw_sample_num}_lon",
            f"raw{raw_sample_num}_alt",
        ]
        header.extend(raw_data_header)
        raw_sample_num += 1
        if raw_sample_num >= 100:
            break

    # Aggregate readings and determine max readings count per timestamp
    for read_timestamp, frames in timestamp_data.items():
        row = [read_timestamp]

        total_readings = 0
        for frame in frames:
            total_readings += len(frame["readings"])

        print(f"{read_timestamp}: {len(frames)} frames. {total_readings} readings.")

        for frame in frames:
            readings = frame["readings"]
            for i in range(len(readings)):
                row.extend(
                    [readings[i]["latitude"], readings[i]["longitude"], readings[i]["altitude"]]
                )

        rows.append(row)

    # Write data to CSV
    with open("gnss_raw_data.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)  # Write header
        writer.writerows(rows)  # Write rows

    print("CSV file 'gnss_raw_data.csv' has been generated.")


def main():
    dev_tty = sys.argv[1]
    try:
        ser = serialbsc.open_serial(dev_tty, baudrate=115200)
    except Exception as e:
        print("ERROR: Opening serial port " + str(e))
        _logging.error("Opening serial port")
        return 1

    while True:
        msg_dict = serialbsc.rcv_message_from_mote(ser)
        msg = msg_dict["Data"]
        msg_str = "\n[" + str(datetime.datetime.now()) + "] "
        msg_str, msg_dic = _msg2string_old(msg)
        if "readings" in msg_dic:
            store_reading(msg_dic)
            # print("")
            # print(msg_dic)
            print(".", end="", flush=True)

        if "END_OF_DATA_RECOVERY" in msg_str:
            print("")
            break

    generate_csv()


if __name__ == "__main__":
    sys.exit(main())
