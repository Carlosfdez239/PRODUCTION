import sys

sys.path.append("../../../lib/")
import logging
import time

import serialbsc
import ubloxutils

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
            # logging.info(f"Accumulated response: {accumulated_data.hex()}")

            # Look for the UBX header (0xB5 0x62)
            header_index = accumulated_data.find(b"\xb5\x62")
            if header_index != -1:
                # logging.info("UBX Header found: 0xB5 0x62")

                # Extract the next 2 bytes for Class ID and Message ID (ACK or NAK)
                if len(accumulated_data) >= header_index + 4:  # Ensure there are enough bytes
                    class_id_and_msg_id = accumulated_data[header_index + 2 : header_index + 4]

                    # Check for UBX-ACK-ACK (0x05 0x01) or UBX-ACK-NAK (0x05 0x00)
                    if class_id_and_msg_id == b"\x05\x01":  # UBX-ACK-ACK

                        # Extract the full ACK message and check the Class ID and CRC
                        ack_message = accumulated_data[
                            header_index : header_index + 10
                        ]  # Length of UBX-ACK-ACK is 10 bytes
                        if len(ack_message) >= 10:
                            msg_id = ack_message[4]  # Extract msgID from the payload (5th byte)

                            # Validate msgID (should be 0x02 for UBX-CFG-CFG)
                            if msg_id == 0x02:
                                # logging.info(f"msgID matched. Checking Class ID and CRC...")

                                # Validate Class ID (should be 0x06 0x09 for UBX-CFG-CFG)
                                class_id = ack_message[6:8]  # Extract Class ID (6th and 7th bytes)
                                if class_id == b"\x06\x09":  # UBX-CFG-CFG

                                    # Validate CRC (last two bytes of the message)
                                    if ubloxutils.ubx_check_crc(ack_message):
                                        logging.info("CRC validated successfully.")
                                        return "ACK"
                                    else:
                                        logging.error("Invalid CRC.")
                                        return None
                                else:
                                    logging.error(
                                        f"Unexpected Class ID: {class_id.hex()}. Expected 0x06 0x09."
                                    )
                                    return None
                            else:
                                logging.error(f"Unexpected msgID: {msg_id}. Expected 0x02.")
                                return None

                    # Check for UBX-ACK-NAK (0x05 0x00)
                    elif class_id_and_msg_id == b"\x05\x00":  # UBX-ACK-NAK
                        logging.error("NAK received: Command not processed.")
                        return "NAK"

    logging.error("No ACK/NAK response received within timeout.")
    return None


# Function to process base or rover configuration with retries
def configure_device(ser, max_retries=5):

    ubloxutils.enter_ser_bridge_mode(ser)

    # Retry logic: Try up to max_retries times
    for attempt in range(max_retries):
        # Close the current serial connection and re-open with the new baud rate
        serialbsc.close_serial(ser)
        ser = serialbsc.open_serial(
            serial_port, baudrate=38400
        )  # Re-open the serial port with new baud rate
        logging.info("Changing baud rate to 38400")

        # Wait for 500 milliseconds
        time.sleep(0.5)

        # configuration packet to reset the u-blox
        packet_base = bytes.fromhex(
            "B5 62 06 09 0D 00 FF FF 00 00 00 00 00 00 FF FF 00 00 03 1B 9A"
        )
        # logging.info(f"Attempt {attempt + 1} of {max_retries} to send reset packet.")
        ubloxutils.send_uart_data(ser, packet_base)

        # Wait for the ACK/NAK response
        response = wait_for_ack_or_nak(ser)
        if response == "ACK":
            logging.info("Ublox Device reset successful.")
            break
        elif response == "NAK":
            logging.error("Failed to reset device due to NAK.")
            break
        else:
            logging.warning(f"No response or invalid response received. Retrying...")

    else:
        # If we exit the loop without breaking, log a final error
        logging.error("Failed to receive valid ACK after retries.")
        # Close the current serial connection and re-open with the new baud rate

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
