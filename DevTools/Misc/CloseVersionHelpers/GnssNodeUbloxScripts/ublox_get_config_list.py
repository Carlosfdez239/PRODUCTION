import sys

sys.path.append("../../../lib/")
import logging
import time

import serialbsc
import ubloxutils

# Constants
CONFIG_FILE_NAME = "ublox_config_list.txt"  # Define the output file name

# List of packets to be sent to get all the configs from ublox
valget_packets = [
    bytes.fromhex("B5 62 06 8B 08 00 00 00 00 00 00 00 FF 0F A7 9E"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 40 00 00 00 FF 0F E7 1E"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 80 00 00 00 FF 0F 27 9E"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 C0 00 00 00 FF 0F 67 1E"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 00 01 00 00 FF 0F A8 A3"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 40 01 00 00 FF 0F E8 23"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 80 01 00 00 FF 0F 28 A3"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 C0 01 00 00 FF 0F 68 23"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 00 02 00 00 FF 0F A9 A8"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 40 02 00 00 FF 0F E9 28"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 80 02 00 00 FF 0F 29 A8"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 C0 02 00 00 FF 0F 69 28"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 00 03 00 00 FF 0F AA AD"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 40 03 00 00 FF 0F EA 2D"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 80 03 00 00 FF 0F 2A AD"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 C0 03 00 00 FF 0F 6A 2D"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 00 04 00 00 FF 0F AB B2"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 40 04 00 00 FF 0F EB 32"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 80 04 00 00 FF 0F 2B B2"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 C0 04 00 00 FF 0F 6B 32"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 00 05 00 00 FF 0F AC B7"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 40 05 00 00 FF 0F EC 37"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 80 05 00 00 FF 0F 2C B7"),
    bytes.fromhex("B5 62 06 8B 08 00 00 00 C0 05 00 00 FF 0F 6C 37"),
]

# Configure logging to both console and file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format for log messages
    handlers=[
        logging.StreamHandler(),  # Output to the console
        # logging.FileHandler("ublox_log.txt")  # Output to a file named "ublox_log.txt"
    ],
)


def wait_for_ack_or_nak(ser, timeout=3):
    start_time = time.time()  # Record the starting time of the function call
    accumulated_data = b""  # Initialize an empty byte string to accumulate data
    ack_message = None  # Initialize ack_message to prevent UnboundLocalError

    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            # Read the available data
            new_data = ser.read(ser.in_waiting)
            accumulated_data += new_data  # Append the new data to the accumulated data

            # Look for the UBX header (0xB5 0x62 0x06 0x8B)
            header_index = accumulated_data.find(b"\xb5\x62\x06\x8B")

            # Check if the header was found
            if header_index != -1:
                # Extract the message length (16-bit, little-endian)
                if (
                    len(accumulated_data) >= header_index + 6
                ):  # Check if we have enough bytes to read size
                    size_msg = (
                        int.from_bytes(
                            accumulated_data[header_index + 4 : header_index + 6],
                            byteorder="little",
                        )
                        + 8
                    )
                    # Check if accumulated_data has enough bytes for extraction
                    if len(accumulated_data) >= header_index + size_msg:
                        # Extract the data if there's enough length
                        ack_message = accumulated_data[header_index : header_index + size_msg]

            # Only proceed if ack_message is assigned
            if ack_message and len(ack_message) >= size_msg:
                # Validate Class ID (should be 0x06 0x8B for UBX-CFG-VALGET)
                class_id = ack_message[2:4]  # Extract Class ID (2nd and 3rd bytes)
                if class_id == b"\x06\x8B":  # UBX-CFG-VALGET
                    # Validate CRC (last two bytes of the message)
                    if ubloxutils.ubx_check_crc(ack_message):
                        # Remove header (first two bytes) and CRC (last two bytes)
                        trimmed_message = ack_message[2:-2]

                        # Convert the trimmed message to hex and save to file
                        hex_data = " ".join(f"{byte:02X}" for byte in trimmed_message)

                        data_line = f"CFG-VALGET - {hex_data}"

                        # Save the hex data to a file
                        with open(CONFIG_FILE_NAME, "a") as f:
                            f.write(data_line + "\n")
                        logging.info(f"Received packet saved to file '{CONFIG_FILE_NAME}'.")
                        return "ACK"
                    else:
                        logging.error("Invalid CRC.")
                        return None
                else:
                    logging.error(f"Unexpected Class ID: {class_id.hex()}. Expected 0x06 0x8B.")
                    return None

    logging.error("No response received within timeout.")
    return None


# Function to process base or rover configuration with retries
def configure_device(ser, max_retries=10):
    ubloxutils.enter_ser_bridge_mode(ser)

    # Close the current serial connection and re-open with the new baud rate
    serialbsc.close_serial(ser)  # Close the existing connection
    # Now the node is in bridge mode, so change the baud rate to 38400
    ser = serialbsc.open_serial(
        serial_port, baudrate=38400
    )  # Re-open the serial port with new baud rate
    # Loop over the packets and retry only on NAK responses
    for packet in valget_packets:

        for attempt in range(max_retries):

            # Wait for 500 milliseconds between packet sends
            time.sleep(0.5)

            # Send the packet
            # logging.info(f"Attempt {attempt + 1} of {max_retries} to send reset packet: {packet.hex()}")
            ubloxutils.send_uart_data(ser, packet)  # Send the packet

            # Wait for the ACK/NAK response
            response = wait_for_ack_or_nak(ser)
            if response == "ACK":
                # logging.info(f"Ublox config packet Rx successful: {packet.hex()}")
                break  # Move to the next packet if ACK is received
            elif response == "NAK":
                logging.error(f"Failed to receive the correct response for packet: {packet.hex()}")
                # Only retry this specific packet on NAK
                if attempt == max_retries - 1:  # If we've exhausted retries for this packet
                    logging.error("Max retries reached for packet")
                continue  # Retry this packet
            else:
                logging.warning(
                    f"No response or invalid response received for packet: {packet.hex()}. Retrying..."
                )

        else:
            # If we exit the inner loop without encountering an ACK (i.e., all retries failed)
            logging.error(
                f"Failed to receive ACK after {max_retries} attempts for packet: {packet.hex()}"
            )
            break

    serialbsc.close_serial(ser)
    ser = serialbsc.open_serial(
        serial_port, baudrate=38400
    )  # Re-open the serial port with new baud rate
    # Wait for 500 milliseconds
    time.sleep(0.5)
    ubloxutils.exit_ser_bridge_mode(ser)


if __name__ == "__main__":
    # Check if a command-line argument is provided for the serial port
    serial_port = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB0"

    try:
        # Open the serial port using open_serial function
        ser = serialbsc.open_serial(serial_port)

        # Configure the device based on the input with retries
        configure_device(ser)

    finally:
        # Close the serial connection after configuration
        if "ser" in locals() and ser.is_open:
            serialbsc.close_serial(ser)
