import logging
import time


# Function to send data via UART
def send_uart_data(ser, data):
    try:
        # Send the data
        ser.write(data)
        logging.info(f"Data sent: {data.hex()}")
    except Exception as e:
        logging.error(f"Error sending data: {e}")
        raise


def enter_ser_bridge_mode(ser):
    # Send the packet to enter bridge mode
    config_base = (
        b"\x10\x02\x12\x01\x00\x00\x96\x00\x08\x01\x00\x64\x2B\x2B\x2B\x03\x00\x78\x00\x78\x10\x03"
    )
    send_uart_data(ser, config_base)
    # Wait for 2000 milliseconds
    time.sleep(3)


def exit_ser_bridge_mode(ser):
    # Send the exit code (2b2b2b) to exit bridge mode
    exit_code = b"\x2B\x2B\x2B"
    send_uart_data(ser, exit_code)
    logging.info("Sent exit code to exit bridge mode.")


# Function to validate CRC (checksum) for the payload starting from the ACK ID (skipping header and trailer)
def ubx_check_crc(data):
    ck_a = 0
    ck_b = 0

    # Start from the ACK ID (skipping header bytes and ending before CRC bytes)
    for byte in data[2:-2]:  # Skip the first 2 bytes (header) and last 2 bytes (CRC)
        ck_a = (ck_a + byte) & 0xFF
        ck_b = (ck_b + ck_a) & 0xFF

    # The last two bytes in the data should be CK_A and CK_B
    expected_ck_a = data[-2]
    expected_ck_b = data[-1]

    # Compare the calculated CRC with the expected values (CK_A and CK_B)
    return expected_ck_a == ck_a and expected_ck_b == ck_b
