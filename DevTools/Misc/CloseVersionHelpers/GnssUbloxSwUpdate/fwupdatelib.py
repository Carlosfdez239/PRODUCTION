import logging
import select
import subprocess


def perform_firmware_update(serial_port, firmware_file, baudrate):
    """
    Perform firmware update using the ubxfwupdate tool.

    Args:
        serial_port (str): The serial port of the device (e.g., /dev/ttyUSB0).
        firmware_file (str): The path to the firmware file.
        baudrate (int): The baud rate for the update (e.g., 9600 or 38400).
    """
    # Dynamically set the -s value based on the baud rate.In case of 9600 baudrate the safeboot is enable.
    s_flag = "1" if baudrate == 9600 else "0"
    cmd = [
        "./ubxfwupdate",
        "-p",
        serial_port,
        "-b",
        f"{baudrate}:9600:{baudrate}",  # Dynamically construct the baud rate string
        "--no-fis",
        "1",
        "-s",
        s_flag,  # Set -s dynamically
        "-t",
        "1",
        "-v",
        "1",
        firmware_file,
    ]
    logging.info(f"Running firmware update: {' '.join(cmd)}")
    # Run the subprocess
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    while True:
        reads = [process.stdout.fileno(), process.stderr.fileno()]
        ret = select.select(reads, [], [])
        for fd in ret[0]:
            if fd == process.stdout.fileno():
                line = process.stdout.readline().strip()
            elif fd == process.stderr.fileno():
                line = process.stderr.readline().strip()

            if line:
                logging.info(line)  # Log all lines as INFO for now

        if process.poll() is not None:
            break

    # Check return code
    if process.returncode != 0:
        return False
    logging.info("Firmware update completed successfully.")
