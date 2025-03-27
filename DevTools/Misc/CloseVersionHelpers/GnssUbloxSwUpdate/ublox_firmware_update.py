#!/usr/bin/env python3
import os
import sys

sys.path.append("../../../lib/")
import logging
import time

import fwupdatelib
import serialbsc
import ubloxutils

# Constants
DEFAULT_PORT = "/dev/ttyUSB0"
DEFAULT_FW_FILE = ""
DEFAULT_BAUDRATE = 38400


def configure_logging(serial_number):
    # Default log file
    default_log_file = "default_ublox_fwupdate.txt"

    # Delete the default log file if it exists
    if serial_number and os.path.exists(default_log_file):
        try:
            os.remove(default_log_file)
            print(f"Deleted default log file: {default_log_file}")
        except Exception as e:
            print(f"Failed to delete default log file: {e}")

    # Get the root logger
    logger = logging.getLogger()
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers.clear()

    # Create the dynamic file name if serial_number is provided
    if serial_number:
        log_file_name = f"{serial_number}_ublox_fwupdate.txt"
    else:
        log_file_name = default_log_file

    # Add handlers for both console and file
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(log_file_name, mode="a")

    # Define a common log format
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Set handlers and logging level
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)


def wait_for_response(ser, timeout=3):
    """
    Waits for a response from the device and extracts the serial number from the received data.

    Args:
        ser (serial.Serial): Serial connection object.
        timeout (int, optional): Timeout in seconds to wait for a response. Default is 3 seconds.

    Returns:
        int or None: Extracted serial number if successful, otherwise None.
    """
    start_time = time.time()  # Record the starting time of the function call
    accumulated_data = b""  # Initialize an empty byte string to accumulate data

    # Target message size in bytes
    expected_size = 31  # Length of the message in bytes

    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            # Read the available data
            new_data = ser.read(ser.in_waiting)
            accumulated_data += new_data  # Append the new data to the accumulated data

            # Check if we've read at least the expected message size
            if len(accumulated_data) >= expected_size:
                logging.info("Expected message size received. Parsing data.")
                break

    # Check if data was received
    if len(accumulated_data) < expected_size:
        logging.error(f"Timeout or incomplete data received. Size: {len(accumulated_data)} bytes.")
        return None

    try:
        # Calculate the positions for the serial number
        # Example message: 10 02 40 59 00 59 04 4f 00 00 08 d5 40 00 01 42 1e e1 bb a0 02 01 00 00 59 03 04 00 00 10 03
        sn_pos_start = (
            22  # Position for the byte containing the nibble (22th byte in 0-based index)
        )

        # Extract the first nibble from byte 23
        serial_number_part1 = (
            accumulated_data[sn_pos_start] & 0x0F
        )  # Mask to get only the lower nibble (last 4 bits)
        # Extract the next 2 bytes from positions 23 and 24
        serial_number_part2 = int.from_bytes(
            accumulated_data[23:25], byteorder="big"
        )  # Byte 23 and 24

        # Combine the parts to form the full serial number
        serial_number = (
            serial_number_part1 << 16
        ) | serial_number_part2  # Shift nibble to the higher bits and combine

        # Log the extracted serial number
        logging.info(f"Extracted Serial Number (SN): {serial_number}")
        return serial_number

    except Exception as e:
        logging.error(f"Failed to parse serial number: {e}")
        return None


def enter_serial_bridge(ser, baudrate):
    """
    Enters serial bridge mode for the u-blox device communication.

    Args:
        ser (serial.Serial): Serial connection object.
        baudrate (int): Baud rate to set for the serial bridge.

    Returns:
        bool: True if successful, raises an exception otherwise.
    """
    try:
        ubloxutils.enter_ser_bridge_mode(ser, baudrate)
        logging.info(f"Entered serial bridge mode at {baudrate} baud.")
        serialbsc.close_serial(ser)
        return True
    except Exception as e:
        logging.error(f"Failed to enter serial bridge mode: {e}")
        raise


def exit_serial_bridge(ser):
    """
    Exits serial bridge mode.

    Args:
        ser (serial.Serial): Serial connection object.

    Returns:
        None
    """
    try:
        ubloxutils.exit_ser_bridge_mode(ser)
        logging.info("Exited serial bridge mode.")
        serialbsc.close_serial(ser)
    except Exception as e:
        logging.error(f"Failed to exit serial bridge mode: {e}")
        raise


def send_uart1_baud_change(ser, baudrate):
    """
    Changes the UART1 baud rate of the u-blox device.

    Args:
        ser (serial.Serial): Serial connection object.
        baudrate (int): New baud rate to set (9600 or 38400).

    Returns:
        None
    """
    try:
        if baudrate == 9600:
            packet_base = bytes.fromhex(
                "B5 62 06 8A 0C 00 00 05 00 00 01 00 52 40 80 25 00 00 D9 F8"
            )  # for 9600 baud rate
        elif baudrate == 38400:
            packet_base = bytes.fromhex(
                "b5 62 06 8a 0c 00 00 05 00 00 01 00 52 40 00 96 00 00 ca 4b"
            )  # for 38400 baud rate
        else:
            raise ValueError(f"Unsupported baud rate: {baudrate}")

        ubloxutils.send_uart_data(ser, packet_base)
        time.sleep(1)
        logging.info(f"Changed UART1 baud rate to {baudrate}")
    except Exception as e:
        logging.error(f"Failed to change UART1 baud rate: {e}")
        raise


if __name__ == "__main__":
    """
    Main script to update u-blox firmware.

    Steps:
    1. Open the serial port with 115200 baudrate (default serial USB connection rate).
    2. Send a health command to get the GNSS node's serial number and configure logging.
    3. Enter serial bridge mode with 38400 baudrate (default u-blox UART1 baudrate).
    4. If the target baudrate is 9600:
        - Open the serial port with 38400 baudrate.
        - Change the UART1 baud rate to 9600.
        - Exit the serial bridge and re-enter with 9600 baudrate.
    5. Perform firmware update using the ubxfwupdate tool.
    6. Re-open the serial port with the updated baudrate and exit the serial bridge.
    """
    serial_port = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PORT
    baudrate = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_BAUDRATE
    firmware_file = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_FW_FILE

    # Validate baud rate
    if baudrate > 38400:
        logging.warning("Baud rate greater than 38400 is not supported. Exiting.")
        sys.exit(1)

    # Validate firmware file
    if not os.path.isfile(firmware_file):
        logging.error(f"Firmware file not found: {firmware_file}")
        sys.exit(1)

    try:
        # Open the serial port with 115200 baudrate. This is the default baudrate of serial USB connection.
        ser = serialbsc.open_serial(serial_port, baudrate=115200)

        # health command to get the serial number of the gnss node.
        helath_cmd = b"\x10\x02\x01\x10\x03"
        ubloxutils.send_uart_data(ser, helath_cmd)
        # Extract serial number
        serial_number = wait_for_response(ser)
        if serial_number is None:
            logging.error("Serial number extraction failed. Exiting.")
            exit(1)

        # Configure logging with the extracted serial number
        configure_logging(serial_number)

        # Step 1: Enter serial bridge with 38400 baudrate because the default u-blox UART1 baudrate is 38400.
        ser = enter_serial_bridge(ser, baudrate=38400)

        if baudrate == 9600:
            # Open the serial port once enter into the serial bridge with 38400 baudrate
            ser = serialbsc.open_serial(serial_port, baudrate=38400)
            logging.info("Changing baud rate to 38400")
            time.sleep(5)

            # Step 2: Change UART1 baud rate of u-blox to 9600
            send_uart1_baud_change(ser, baudrate)
            time.sleep(5)
            # exit the serial bridge of 38400 baudrate
            exit_serial_bridge(ser)
            time.sleep(5)
            # Once exit the serial bridge then node will be defaulting to 115200 baudrate,
            # hence open the serial port with 115200
            ser = serialbsc.open_serial(serial_port, baudrate=115200)
            time.sleep(2)

            # Step 3: Re-enter serial bridge with 9600 baudrate, because u-blox UART1 baudrate was set to 9600.
            ser = enter_serial_bridge(ser, baudrate=9600)
            time.sleep(5)

            # Step 4: Perform firmware update with ubxfwupdate tool.
            # The tool will be communicating with u-blox on 9600:9600:9600 baudrate.
            # First baudrate 9600 is used:sending the training sequence and reading the fw version.
            # Second baudrate 9600 is used to communicate with u-blox in safeboot.if safeboot is enable.
            # Third baudrate 9600 is used for flashing the firmware.
            fwupdatelib.perform_firmware_update(serial_port, firmware_file, baudrate)

            # Once the fwupdate is completed, then open the serial port with 9600 baudrate
            # (this was the baudrate used to enter into serial bridge)
            ser = serialbsc.open_serial(serial_port, baudrate=9600)

        elif baudrate == 38400:
            # Open the serial port once enter into the serial bridge with 38400 baudrate
            ser = serialbsc.open_serial(serial_port, baudrate=38400)
            time.sleep(5)
            # Step 2: and Step 3: are not required since the u-blox UART1 is working with 38400 baudrate by default.

            # Step 4: Perform firmware update with ubxfwupdate tool.
            # The tool will be communicating with u-blox on 38400:9600:38400 baudrate.
            # First baudrate 38400 is used: sending the training sequence and reading the fw version.
            # Second baudrate 9600 is used to communicate with u-blox in safeboot.
            # Here the safeboot is disable:with serial bridge fwupdate flashing is not possible with other baudrate.
            # Third baudrate 38400 is used for flashing the firmware.
            fwupdatelib.perform_firmware_update(serial_port, firmware_file, baudrate)

            # Once the fwupdate is completed, then open the serial port with 38400 baudrate
            # (this was the baudrate used to enter into serial bridge)
            ser = serialbsc.open_serial(serial_port, baudrate=38400)

        time.sleep(2)

        # Step 5: Exit serial bridge mode.
        exit_serial_bridge(ser)

    finally:
        # Close the serial connection after configuration
        if "ser" in locals() and ser.is_open:
            serialbsc.close_serial(ser)
