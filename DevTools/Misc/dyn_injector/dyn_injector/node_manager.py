#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is a test file to check the data from the benchmark.
"""

import logging
import struct
import time
from warnings import warn

#######################################
# IMPORTS
#######################################
import numpy as np
import serial

#######################################
# Commands
#######################################
UART_CMD_NONE = 0
UART_CMD_ERROR = 1
UART_CMD_RAW = 2
UART_CMD_RAW_READY = 3
UART_CMD_RAW_END = 4
UART_CMD_RAW_COMPLETED = 5
UART_CMD_RAW_ACCEPTED = 6
UART_CMD_UINT16 = 7
UART_CMD_UINT16_READY = 8
UART_CMD_UINT16_END = 9
UART_CMD_UINT16_COMPLETED = 10
UART_CMD_UINT16_ACCEPTED = 11
UART_CMD_UINT8 = 12
UART_CMD_UINT8_READY = 13
UART_CMD_UINT8_END = 14
UART_CMD_UINT8_COMPLETED = 15
UART_CMD_UINT8_ACCEPTED = 16
UART_CMD_SIM_START = 17
UART_CMD_TENSOR_START = 18
UART_CMD_TENSOR_CFG_1 = 19
UART_CMD_TENSOR_CFG_2 = 20
UART_CMD_TENSOR_CFG_OK = 21
UART_CMD_TENSOR_END = 22
UART_CMD_TENSOR_COMP = 23
UART_CMD_MODEL_START = 24
UART_CMD_MODEL_CFG = 25
UART_CMD_MODEL_IFOREST_OK = 26
UART_CMD_MODEL_OCSVM_OK = 27
UART_CMD_MODEL_GMM_MD_OK = 28
UART_CMD_MODEL_ZSCORE_OK = 29
UART_CMD_MODEL_END = 30
UART_CMD_MODEL_COMP = 31
UART_CMD_EVAL_START = 32
UART_CMD_EVAL_READY = 33
UART_CMD_EVAL_RAW_OK = 34
UART_CMD_EVAL_INF = 35
UART_CMD_EVAL_INF_OK = 36
UART_CMD_EVAL_CONTINUE = 37
UART_CMD_EVAL_END = 38
UART_CMD_RESTART = 39
UART_CMD_STRING = 40
UART_CMD_DONE = 41
UART_CMD_CONTINUE = 42
UART_CMD_OK = 43
UART_CMD_END = 44
UART_CMD_DEMO_INIT = 45
UART_CMD_DEMO_DATA = 46
UART_CMD_DEMO_OK = 47
UART_CMD_DEMO_RECON = 48
UART_CMD_DEMO_TRAIN = 49
UART_CMD_DEMO_INFERENCE = 50
UART_CMD_DEMO_AXIS_DATA = 51
UART_CMD_DEMO_WAIT = 52
UART_CMD_DEMO_CONT = 53
UART_CMD_DEMO_RECONNECT = 54
UART_CMD_MAX = 55

SERIAL_STR_SUCCESS = b"OK"
SERIAL_STR_FAIL = b"ERROR"
SERIAL_STR_TRANS_COMPLETE = b"TX_DONE"
SERIAL_STR_REC_COMPLETE = b"RX_DONE1"
SERIAL_STR_REC_COMPLETE_2 = b"RX_DONE2"
SERIAL_STR_READY = b"READY"
SERIAL_STR_CONTINUE = b"CONTINUE"
SERIAL_STR_DONE = b"DONE"

DEFAULT_SERIAL_PORT = "/dev/ttyUSB0"
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 0
SERIAL_RETRIES_S = 20
SERIAL_MAX_TRANSMIT_PAYLOAD = 2500  # this does not includes header or \r\n
SERIAL_MAX_TRANSMIT_OVERHEAD = 7
SERIAL_MAX_TRANSMIT_SIZE = SERIAL_MAX_TRANSMIT_PAYLOAD + SERIAL_MAX_TRANSMIT_OVERHEAD
SERIAL_SIZE_OF_RAW = 4
SERIAL_SIZE_OF_UINT16 = 2
SERIAL_SIZE_OF_UINT8 = 1
SERIAL_TYPE_OF_RAW = "i"  # int32_t is the raw type for the adxl35x

RECOVER_RETIRES = 5
DEFAULT_RETRIES = 5

# --- serial ---
ser = None
logger = None

# --- config ---
DEBUGGING_SERIAL = False


#######################################
# Node management
#######################################
def parse_eval(msg):
    if DEBUGGING_SERIAL:
        print(msg)
    score, prediction = struct.unpack(f"!{SERIAL_TYPE_OF_RAW}B", msg)
    if DEBUGGING_SERIAL:
        print("parse eval", score, prediction)
    return score, prediction


def parse_string(msg):
    s = struct.unpack(f"!{len(msg)}s", msg)
    return s[0]


def parse_header(msg):
    header = msg[:3]
    payload = msg[3:]
    cmd, ln = struct.unpack("!BH", header)
    return cmd, ln, payload


def parse_uint16(x):
    return struct.unpack("!H", x)


def pack_raw_data(x):
    f = "!BH"
    f += SERIAL_TYPE_OF_RAW * len(x)
    msg = struct.pack(f, UART_CMD_RAW, SERIAL_SIZE_OF_RAW * len(x), *x)
    return msg


def pack_uint16_data(x):
    f = "!BH"
    f += "H" * len(x)
    msg = struct.pack(f, UART_CMD_UINT16, SERIAL_SIZE_OF_UINT16 * len(x), *x)
    return msg


def pack_uint8_data(x):
    f = "!BH"
    f += "B" * len(x)
    msg = struct.pack(f, UART_CMD_UINT8, SERIAL_SIZE_OF_UINT8 * len(x), *x)
    return msg


def pack_string(s):
    f = f"!BH{len(s)}s"
    msg = struct.pack(f, UART_CMD_STRING, len(s), s)
    return msg


def pack_cmd(cmd):
    msg = struct.pack("!BH", cmd, 0)
    return msg


def pack_tx_end(msg):
    m = bytearray(msg)
    m.extend(struct.pack("!2s", b"\r\n"))
    return bytes(m)


def pack_tx_head(msg):
    msg_size = len(msg)
    m = bytearray(struct.pack("!H", msg_size))
    m.extend(msg)
    return bytes(m)


def init_serial(serial_port=DEFAULT_SERIAL_PORT):
    global ser
    try:
        ser = serial.Serial(serial_port, baudrate=SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT)
    except serial.serialutil.SerialException:
        if logger is not None:
            logger.error(f"Node Serial: Cannot start the serial port for the node at {serial_port}")
            print(f"Node Serial: error cannot start the serial port at {serial_port}")
        else:
            print(f"Node Serial: error cannot start the serial port at {serial_port}")
        return False
    return True


def write_serial_raw(x):
    step = int(np.floor(SERIAL_MAX_TRANSMIT_PAYLOAD / SERIAL_SIZE_OF_RAW))
    n_packs = int(np.ceil(len(x) / step))
    for n in range(n_packs):
        if DEBUGGING_SERIAL:
            print(f"sending raw {n} of {n_packs}")
        lo = n * step
        hi = min((n + 1) * step, len(x))
        p = pack_tx_head(pack_tx_end(pack_raw_data(x[lo:hi])))
        ser.write(p)
        if not read_serial_cmd(UART_CMD_RAW_READY):
            return False

    write_serial_cmd(UART_CMD_RAW_END)
    return read_serial_cmd(UART_CMD_RAW_COMPLETED)


def write_serial_uint16(x):
    step = int(np.floor(SERIAL_MAX_TRANSMIT_PAYLOAD / SERIAL_SIZE_OF_UINT16))
    n_packs = int(np.ceil(len(x) / step))
    for n in range(n_packs):
        if DEBUGGING_SERIAL:
            print(f"sending uint16 {n} of {n_packs}")
        lo = n * step
        hi = min((n + 1) * step, len(x))
        p = pack_tx_head(pack_tx_end(pack_uint16_data(x[lo:hi])))
        ser.write(p)
        if not read_serial_cmd(UART_CMD_UINT16_READY):
            return False

    write_serial_cmd(UART_CMD_UINT16_END)
    return read_serial_cmd(UART_CMD_UINT16_COMPLETED)


def write_serial_uint8(x):
    step = int(np.floor(SERIAL_MAX_TRANSMIT_PAYLOAD / SERIAL_SIZE_OF_UINT8))
    n_packs = int(np.ceil(len(x) / step))
    for n in range(n_packs):
        if DEBUGGING_SERIAL:
            print(f"sending uint8 {n} of {n_packs}")
        lo = n * step
        hi = min((n + 1) * step, len(x))
        p = pack_tx_head(pack_tx_end(pack_uint8_data(x[lo:hi])))
        ser.write(p)
        if not read_serial_cmd(UART_CMD_UINT8_READY):
            return False

    write_serial_cmd(UART_CMD_UINT8_END)
    return read_serial_cmd(UART_CMD_UINT8_COMPLETED)


def write_serial_string(s):
    msg = pack_tx_head(pack_tx_end(pack_string(s)))
    ser.write(msg)


def write_serial_cmd(cmd):
    msg = pack_tx_head(pack_tx_end(pack_cmd(cmd)))
    if DEBUGGING_SERIAL:
        print("writing:", cmd)
    ser.write(msg)


remaining_read_buffer = bytearray()


def read_serial_until(start=False, non_blocking=False):
    global remaining_read_buffer

    done = False
    m = remaining_read_buffer
    msg = None
    ln = 0
    timeout_s = SERIAL_RETRIES_S

    init_t = time.time()
    while time.time() - init_t < timeout_s and not done:
        if non_blocking:
            timeout_s = 0
        packet = ser.read(100)
        m.extend(packet)
        if len(m) < 2:
            continue
        ln = struct.unpack("!H", m[:2])[0]
        if ln > SERIAL_MAX_TRANSMIT_SIZE or ln == 0:
            if DEBUGGING_SERIAL:
                print(f"incorrect_transmit size {ln} > {SERIAL_MAX_TRANSMIT_SIZE}")
            if start and len(m) > 1:
                m = m[1:]
                continue
            break  # incorrect transmit size.
        if len(m) >= ln:
            if b"\r\n" == m[ln - 2 : ln]:
                msg = m[2 : ln - 2]
                remaining_read_buffer = m[ln:]
                done = True
            else:
                if DEBUGGING_SERIAL:
                    print("unexpected squence termination", m, m[ln - 2 : ln])
                if start and len(m) > 1:
                    m = m[1:]
                    continue
                break  # Unexpected sequence termination
    if DEBUGGING_SERIAL:
        if not (non_blocking and ln == 0):
            print("message: ", m, ln, len(m))
            if len(m) > 5:
                print(" message: ", parse_header(m[2:]))
    if not done and not non_blocking:
        clean_reamining_buffer()
    return done, msg


def clean_reamining_buffer():
    global remaining_read_buffer
    remaining_read_buffer = bytearray()


def read_serial_eval():
    running = True
    while running:
        done, msg = read_serial_until()
        if done:
            running = False

    cmd, len, payload = parse_header(bytes(msg))
    if cmd != UART_CMD_EVAL_INF or len != (SERIAL_SIZE_OF_RAW + 1):
        if logger is not None:
            logger.warn(f"Serial Error, cannot read eval data {cmd} - {len}")
        else:
            warn(f"Serial Error, cannot read eval data {cmd} - {len}", UserWarning)
        return None
    score, prediction = parse_eval(payload)
    if DEBUGGING_SERIAL:
        print("score, pred", score, prediction)

    return score, prediction


def read_serial_string(start=False):

    done, msg = read_serial_until(start)
    if not done:
        if logger is not None:
            logger.warn(f"Serial Error, cannot read string data {done}")
        else:
            warn(f"Serial Error, cannot read string data {done}", UserWarning)
        return None

    cmd, l, payload = parse_header(bytes(msg))
    if cmd != UART_CMD_STRING:
        if logger is not None:
            logger.warn(f"Serial Error, cannot read string data {cmd}")
        else:
            warn(f"Serial Error, cannot read string data {cmd}", UserWarning)
        return None

    s = parse_string(payload)
    if len(s) != l:
        if logger is not None:
            logger.warn(f"Serial Error, wrong size of string data {len(s)} - {l}")
        else:
            warn(f"Serial Error, wrong size of string data {len(s)} - {l}", UserWarning)
        return None
    if DEBUGGING_SERIAL:
        print("read:", s)
    return s


def read_serial_cmd(cmd):
    done, msg = read_serial_until()
    if not done:
        if logger is not None:
            logger.warn(f"Serial Error, cannot read serial CMD")
        else:
            warn(f"Serial Error, cannot read serial CMD {cmd}", UserWarning)
        return False
    cmd_ser, ln, payload = parse_header(bytes(msg))
    if cmd != cmd_ser or ln != 0 or 0 != len(payload):
        if logger is not None:
            logger.warn(f"Serial Error, wrong message {cmd}-{cmd_ser}, {ln}, {payload}")
        else:
            warn(f"Serial Error, wrong message {cmd}-{cmd_ser}, {ln}, {payload}", UserWarning)
        return False
    if DEBUGGING_SERIAL:
        print("read_cmd:", cmd)
    return True


#######################################
# Main
#######################################
def clean_serial():
    clean_reamining_buffer()
    rep = SERIAL_RETRIES_S
    while ser.in_waiting > 0 or rep > 0:
        n = ser.in_waiting
        ser.read(n)
        rep -= 1


def flush_serial():
    ser.flushInput()
    ser.flushOutput()
    clean_serial()


def init(serial_port=DEFAULT_SERIAL_PORT, logger_name=None):
    """
    Initialize the serial communication to the node

    :param serial_port: path to the serial device connected to the node
    :param logger_name: main application logger name or none to skip logging for this module
    """
    global logger

    if logger_name is not None:
        logger = logging.getLogger(logger_name)
        logger.info("Node Serial: Starting")

    if not init_serial(serial_port):
        return False
    flush_serial()

    return True


def inject_data(x):
    """
    Send raw data to the node.
    The data is interpreted as being consecutive samples, each sample represented by 3 values for the 3 axes.

    [ X0, Y0, Z0, X1, Y1, Z1, X2, Y2, Z2, ... ]

    Therfore, the data should be multiple of 3, otherwise the lhe last incomplete sample will not be
    processed by the node.

    :param arg_parser: array of raw values (uint32) to send to the node
    """
    flush_serial()
    start_flag_recv = False
    while not start_flag_recv:
        start_flag_recv = read_serial_cmd(UART_CMD_RAW_READY)
    return write_serial_raw(x)
