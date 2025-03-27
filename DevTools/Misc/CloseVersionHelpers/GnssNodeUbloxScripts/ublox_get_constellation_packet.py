import sys

sys.path.append("../../../lib/")
import logging
import time

import serialbsc
import ubloxutils

# Constants
CONFIG_FILE_NAME = "ublox_constellation_packet.txt"  # Define the output file name

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

    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            # Read the available data
            new_data = ser.read(ser.in_waiting)
            accumulated_data += new_data  # Append the new data to the accumulated data

            # Look for the UBX header (0xB5 0x62)
            header_index = accumulated_data.find(b"\xb5\x62")
            if header_index != -1:
                # Check for UBX-CFG-VALGET (0x06 0x8B)
                ack_message = accumulated_data[
                    header_index : header_index + 42
                ]  # Length of UBX-CFG-VALGET is 42 bytes
                if len(ack_message) >= 42:
                    msg_id = ack_message[4]  # Extract msgID from the payload (5th byte)

                    # Validate msgID (should be 0x22 for UBX-CFG-VALGET)
                    if msg_id == 0x22:
                        # Validate Class ID (should be 0x06 0x8B for UBX-CFG-VALGET)
                        class_id = ack_message[2:4]  # Extract Class ID (2nd and 3rd bytes)
                        if class_id == b"\x06\x8B":  # UBX-CFG-VALGET
                            # Validate CRC (last two bytes of the message)
                            if ubloxutils.ubx_check_crc(ack_message):
                                # Convert the message to hex and write to file with spaces between bytes
                                hex_data = " ".join(f"{byte:02X}" for byte in ack_message)

                                # Save the hex data to a file
                                with open(CONFIG_FILE_NAME, "w") as f:
                                    f.write(hex_data)
                                logging.info(f"Received packet saved to file '{CONFIG_FILE_NAME}'.")
                                return "ACK"
                            else:
                                logging.error("Invalid CRC.")
                                return None
                        else:
                            logging.error(
                                f"Unexpected Class ID: {class_id.hex()}. Expected 0x06 0x8B."
                            )
                            return None
                    else:
                        logging.error(f"Unexpected msgID: {msg_id}. Expected 0x22.")
                        return None

    logging.error("No response received within timeout.")
    return None


# Function to process base or rover configuration with retries
def configure_device(ser, max_retries=5):
    ubloxutils.enter_ser_bridge_mode(ser)
    # Close the current serial connection and re-open with the new baud rate
    serialbsc.close_serial(ser)
    # Now the node is in bridge mode, so change the baud rate to 38400
    ser = serialbsc.open_serial(serial_port, baudrate=38400)
    # logging.info("Changing baud rate to 38400")

    # Wait for 500 milliseconds
    time.sleep(0.5)
    # Retry logic: Try up to max_retries times
    for attempt in range(max_retries):

        # configuration packet to get the constellation values.
        packet_base = bytes.fromhex(
            "B5 62 06 8B 1C 00 00 00 00 00 1F 00 31 10 20 00 "
            "31 10 21 00 31 10 22 00 31 10 24 00 31 10 25 00 "
            "31 10 FE 89"
        )
        # logging.info(f"Attempt {attempt + 1} of {max_retries} to send reset packet.")
        ubloxutils.send_uart_data(ser, packet_base)

        # Wait for the ACK/NAK response
        response = wait_for_ack_or_nak(ser)
        if response == "ACK":
            logging.info("Constellation Packet Rx successful.")
            break
        elif response == "NAK":
            logging.error("Failed to receive the to CRC.")
            break
        else:
            logging.warning(f"No response or invalid response received. Retrying...")

    else:
        # If we exit the loop without breaking, log a final error
        logging.error("Failed to receive valid packet after retries.")

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
