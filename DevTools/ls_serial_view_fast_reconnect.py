#!/usr/bin/env python3

"""
Script to monitor messages from a node over a persistent serial connection.

This script continuously attempts to reconnect to the node with a short 0.01 second
delay. It prints the connection status (connected/disconnected) only when the state
changes. It reads and formats incoming messages in a human-readable format.

Reconnect attempts are not printed by default because it crowds the terminal.

Command-line arguments:
- First argument: device (e.g., /dev/ttyUSB0 for serial).
- `-l`: Enable one-line message format.
- `-s [server_ip]`: Use socket connection with the specified server IP.
- '-v': Enable verbose printing that changes logging level to info.
"""

import datetime
import logging
import re
import sys
import time

sys.path.append("./lib/")

import ls_msg2string as ls_msg2string
import serial  # from pyserial, avoid installing just 'serial' package (errors)
import serialbsc as serialbsc

# Configure logging


# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def get_utc_timestamp():
    """Returns the current UTC timestamp as seconds since epoch."""
    return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds())


def open_serial_connection(device, use_socket=False, server_ip=None):
    """
    Opens a serial or socket connection and returns the connection object.
    If unsuccessful, returns None.
    """
    try:
        if not use_socket:
            ser = serialbsc.open_serial(device, baudrate=115200)
        else:
            port_num = str(int(re.search(r"(\d+)$", device).group(0)) + 54500)
            ser = serial.serial_for_url(f"socket://{server_ip}:{port_num}", 115200)

        ser.reset_input_buffer()  # Flush input buffer to avoid stale data
        return ser
    except Exception:
        return None


def format_message(msg_data, one_line_flag):
    """
    Formats the incoming message data into a readable string.
    If one_line_flag is True, the output is in a compact format.
    """
    timestamp = datetime.datetime.now()
    formatted_data = " ".join(f"{byte:02x}" for byte in msg_data)

    if one_line_flag:
        return f"{get_utc_timestamp()};{timestamp}; {formatted_data};{ls_msg2string.msg2string(msg_data)}"
    else:
        return f"\n[{timestamp}] {formatted_data}\n{ls_msg2string.msg2string(msg_data)}"


def read_message(ser, one_line_flag):
    """
    Reads a message from the serial connection and processes it.
    Returns False if there is a connection issue, otherwise True.
    """
    try:
        msg_dict = serialbsc.rcv_message_from_mote(ser)
        msg_data = msg_dict["Data"]
        print(format_message(msg_data, one_line_flag))
        sys.stdout.flush()
        return True
    except (serial.SerialException, OSError):
        return False
    except Exception as e:
        logging.error(f"Unexpected error while reading message: {e}")
        return False


def parse_arguments():
    """Parses and returns command-line arguments."""
    device = sys.argv[1]
    one_line_flag = "-l" in sys.argv
    use_socket = "-s" in sys.argv
    server_ip = sys.argv[sys.argv.index("-s") + 1] if use_socket else None
    verbose = "-v" in sys.argv

    return device, one_line_flag, use_socket, server_ip, verbose


def main():
    device, one_line_flag, use_socket, server_ip, verbose = parse_arguments()

    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    is_connected = False
    reconnect_delay = 0.01
    while True:
        ser = open_serial_connection(device, use_socket, server_ip)

        if ser:
            if not is_connected:
                print(f"{GREEN}Connected {YELLOW}{device}{RESET}")
                is_connected = True

            if not read_message(ser, one_line_flag):
                try:
                    ser.close()
                except Exception as e:
                    logging.error(f"Error closing connection: {e}")
                ser = None

        else:
            if is_connected:
                print(f"{RED}Disconnected {YELLOW}{device}{RESET}")
                is_connected = False

        time.sleep(reconnect_delay)


if __name__ == "__main__":
    sys.exit(main())
