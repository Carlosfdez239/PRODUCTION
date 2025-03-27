# **Overview**

This repository contains Python scripts for configuring and managing u-blox devices. Each script performs a specific task, such as resetting configurations, retrieving configuration keys, or fetching constellation configuration data. Below is a description of each script and its functionality.

---

## **1. _ublox_get_config_list.py_**

This script retrieves a list of all configuration keys from the u-blox device and saves them to a file.

### **Steps Performed:**
- Opens a serial connection with the Loadsening device at a baud rate of `115200`.
- Enters serial bridge mode (baud rate: `38400`) by sending a specific serial bridge command.
- Change the BR of serial connection to 38400.
- Sends a command to the u-blox device to retrieve all configuration keys.
- Saves the configuration keys to a file named **`ublox_config_list.txt`** in the same folder as the script.
- Exits serial bridge mode by sending an exit command.

---

## **2. _ublox_reset.py_**

This script resets the u-blox device to its factory default configuration.

### **Steps Performed:**
- Opens a serial connection with the Loadsensing device at a baud rate of `115200`.
- Enters serial bridge mode (baud rate: `38400`) by sending a specific serial bridge command.
- Change the BR of serial connection to 38400.
- Sends a command to the u-blox device to reset and revert to default configurations.
- Exits serial bridge mode by sending an exit command.

---

## **3. _ublox_get_constellation_packet.py_**

This script retrieves the constellation configuration data from the u-blox device and saves it to a file.

### **Steps Performed:**
- Opens a serial connection with the Loadsensing device at a baud rate of `115200`.
- Enters serial bridge mode (baud rate: `38400`) by sending a specific serial bridge command.
- Change the BR of serial connection to 38400.
- Sends a command to the u-blox device to get the constellation configuration data.
- Saves the constellation configuration data to a file named **`ublox_constellation_packet.txt`** in the same folder as the script.
- Exits serial bridge mode by sending an exit command.

---

## **Usage Instructions**

1. Ensure you have **Python 3** installed on your system.
2. Set the proper serial port if required; otherwise, the default serial port is **`/dev/ttyUSB0`**.
3. Before running the script, Ensure that Loadsensing device is powered ON and running.
4. Ensure no other process or program is accessing the same serial port, causing conflicts.
5. Run the desired script using Python:
   ```bash
   python ublox_get_config_list.py
   python ublox_reset.py
   python ublox_get_constellation_packet.py
   ```