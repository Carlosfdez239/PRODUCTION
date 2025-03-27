# **u-blox Firmware Update Script**

## **Overview**
This repository provides a Python script for updating the firmware of u-blox devices. The script automates entering and exiting serial bridge mode, adjusting baud rates, and running the firmware update process using the `ubxfwupdate` tool.

---

## **Features**
- Automatically handles serial bridge mode for communication with the u-blox device.
- Dynamically adjusts UART1 baud rate (`9600`, `38400`) as required.
- Executes firmware updates using the `ubxfwupdate` tool with real-time progress logs.
- Read the Gnss node serial number and create the log file: SN_ublox_fwupdate.txt

---

## **Requirements**
1. **Python 3.x** installed on your system.
2. **`ubxfwupdate`** tool must be present in the working directory or system `PATH`.
   **`ubxfwupdate tool source code:`**'https://drive.google.com/file/d/198s1HcOsvoIhIqJ2mH6ebJY7SxJ8zJyO/view?usp=drive_link`
3. The u-blox firmware update binary file should be available.
   **`ublox fw binary:`**'https://drive.google.com/file/d/1-ooibhv4v35Xp9kIhMUTlq5D4BcZRa2e/view?usp=drive_link`

---

## **Usage Instructions**

### **1. Prepare the Environment**
- Ensure the GNSS device is powered ON and connected to your computer via a serial port (e.g., `/dev/ttyUSB0`).
- Verify that no other program or process is using the serial port.
- Place the firmware file you wish to use in a known directory.

---

### **2. Run the Script**
The script takes three optional arguments:

```bash
python ublox_firmware_update.py [serial_port] [baudrate] [firmware_file]
```
#### Arguments:
- serial_port: The serial port connected to the u-blox device (default:`/dev/ttyUSB0`).
- baudrate: Desired baud rate (default: `38400`). Supported values: `9600, 38400`.
- firmware_file: Path to the firmware file to upload (default: empty, required if not specified).

#### Example
```bash
python ublox_firmware_update.py /dev/ttyUSB0 38400 firmware.bin

```
## **NOTE**
- U-blox firmware update takes approximately 5 minutes if the flashing baud rate is 38400.
- U-blox firmware update takes approximately 23 minutes if the flashing baud rate is 9600.
- Always prefer to use the 38400 baud rate for quicker flashing.
- If the u-blox firmware is corrupted, consider using the 9600 baud rate for flashing in safeboot.