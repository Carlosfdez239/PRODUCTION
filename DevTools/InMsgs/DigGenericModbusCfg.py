#!/usr/bin/env python3
import json
import math
import os
import struct
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import bitstring
import wx
from bitstring import BitArray
from ls_utils import ls_send_message_uart

# version control for instructions. Whenever we implement or modify an instruction, we shall increment the version
INSTRUCTIONS_VERSION = 0
# version control for the config. Whenever we modify the config generic_modbus_configs.json in a way that
# the DLOG and Subscritor are no longer compatible, we shall increment the version
CONFIG_VERSION = 0

GLOBAL_INSTRUCTIONS_BUFFER_SIZE_BYTES = (
    15  # maximum size in bytes for all the global instructions and the corresponding arguments
)
# maximum size in bytes for all the sensor instructions and the corresponding arguments
SENSOR_INSTRUCTIONS_BUFFER_SIZE_BYTES = 400
MESSAGE_MAX_SIZE_BYTES = (
    39  # maximum size in bytes for the data that the node will send via serial or via LoRa
)
MAX_MESSAGES = 10  # maximum number of messages that the node will send via serial or via LoRa
MAX_SENSORS_IN_CONFIG = 50
TTY_PREFIX = "/dev/ttyUSB"

# The dictionary contains all the possible instructions and the structure is:
# The key is the ID of the instruction, and every entry in the dictionary contains:
# A list of two positions where the first is the name of the instruction (informational purposes for the UI)
# and the second position of the list is an another list that
# contains the size in bits of the arguments of the instruction.
INSTRUCTIONS_DICT = {
    0: ["PUSH 16", [2, 16, 0, 0]],
    1: ["PUSH 32", [2, 16, 16, 0]],
    2: ["POP", [0, 0, 0, 0]],
    3: ["READ MODBUS", [2, 1, 1, 16]],
    4: ["WRITE MULTIPLE MODBUS", [1, 16, 0, 0]],
    5: ["JUMP", [8, 0, 0, 0]],
    6: ["BRANCH EQ", [3, 8, 0, 0]],
    7: ["BRANCH NQ", [3, 8, 0, 0]],
    8: ["BRANCH GT", [3, 8, 0, 0]],
    9: ["BRANCH GE", [3, 8, 0, 0]],
    10: ["BRANCH LT", [3, 8, 0, 0]],
    11: ["BRANCH LE", [3, 8, 0, 0]],
    12: ["ADD", [0, 0, 0, 0]],
    13: ["SUB", [0, 0, 0, 0]],
    14: ["MULT", [0, 0, 0, 0]],
    15: ["DIV", [0, 0, 0, 0]],
    16: ["OR", [0, 0, 0, 0]],
    17: ["AND", [0, 0, 0, 0]],
    18: ["XOR", [0, 0, 0, 0]],
    19: ["SHIFT RIGHT", [5, 0, 0, 0]],
    20: ["SHIFT LEFT", [5, 0, 0, 0]],
    21: ["CAST", [2, 0, 0, 0]],
    22: ["SLEEP MILLISECONDS", [0, 0, 0, 0]],
    23: ["PUSH DATA OUT", [6, 0, 0, 0]],
    24: ["CHECK VOLTAGE SUPPLY", [0, 0, 0, 0]],
    25: ["DUPLICATE", [0, 0, 0, 0]],
    26: ["BURY", [4, 0, 0, 0]],
    27: ["DIG", [4, 0, 0, 0]],
    28: ["BRANCH FLOAT NAN", [3, 8, 2, 0]],
    29: ["BRANCH FLOAT INF", [3, 8, 2, 0]],
    30: ["BRANCH FLOAT NOT FINITE", [3, 8, 2, 0]],
    31: ["BRANCH FLOAT NOT NORMAL", [3, 8, 2, 0]],
    32: ["WRITE SINGLE MODBUS", [16, 0, 0, 0]],
}

PARITY_DIC = {0: "0 (None)", 1: "1 (even)", 2: "2 (odd)"}
STOP_BITS_DIC = {0: "0 (0.5 bit)", 1: "1 (1 bit)", 2: "2 (1.5 bit)", 3: "3 (2 bit)"}
DATA_BITS_LIST = ["8", "9"]

# list that will store all the global instructions (every position in the
# list will be another list with an instruction and the arguments)
global_instructions_list = []
# list that will store all the sensor instructions (every position in the
# list will be another list with an instruction and the arguments)
sensor_instructions_list = []
# list that will store all the information from every channel of the
# sensor (every position of the list will be a dictionary with the
# information of a channel)
channels_info_list = []
global_set_instructions_list = [
    INSTRUCTIONS_DICT[0][0],
    INSTRUCTIONS_DICT[1][0],
    INSTRUCTIONS_DICT[22][0],
]  # list the global instructions admitted
config_values_dict = (
    {}
)  # dictionary that will store all the parameters in order to set a configuration correctly
sensors_list = []  # list that will store the ids of the sensors
last_file_opened_string = "configs.json"  # json file that contains the configurations


class DigGenericModbusCfg(wx.Frame):
    def __init__(self, *args, **kw):
        super(DigGenericModbusCfg, self).__init__(*args, **kw)
        self.init_ui()

    # Checks if the input value is a number
    #
    # @param s: The number in string format to check
    #
    # @return: A boolean, true if the input value is a number, false otherwise
    #
    def is_number(self, s):
        try:
            int(s)
            return True
        except:
            try:
                int(s, 16)
                return True
            except:
                return False

    # Converts the input value to a decimal representation
    #
    # @param s: The number in string format to convert
    #
    # @return: The number in decimal representation
    #

    def to_int(self, s):
        try:
            value = int(s)
            return value
        except ValueError:
            value = int(s, 16)
            return value

    # Searches the key in INSTRUCTIONS_DICT that contains the value name
    #
    # @param name: The string to search the correct key
    #
    # @return: the key that contains the name param in integer format
    #
    def get_id_instruction(self, name):
        for key in list(INSTRUCTIONS_DICT.keys()):
            if INSTRUCTIONS_DICT[key][0] == name:
                return key

    # Gets all the instructions names from INSTRUCTIONS_DICT
    #
    # @return: a list with all the instructions names in string format
    #
    def get_instructions_names(self):
        list_names = []
        for instruction in list(INSTRUCTIONS_DICT.values()):
            list_names.append(instruction[0])
        return list_names

    # Creates a mask in bits
    #
    # @param num_bits: The size of the mask
    #
    # @return: the mask
    #
    def create_mask(self, num_bits):
        return (1 << num_bits) - 1

    # Extracts a certain number of bits from a message
    #
    # @param msg: The message from the bits will be extracted
    # @param bit_offset: The index where the function will start to extract bits
    # @param num_bits: The number of bits to extract from the message msg
    #
    # @return: the substracted bits
    #
    def extract_bits_from_array(self, msg, bit_offset, num_bits):
        first_byte = bit_offset / 8
        first_bit_offset = bit_offset % 8
        last_byte = (bit_offset + num_bits - 1) / 8
        last_bit_offset = (bit_offset + num_bits - 1) % 8
        value = 0
        current_mask_size = 8 - first_bit_offset
        current_mask = self.create_mask(current_mask_size)

        current_byte = first_byte
        while current_byte < last_byte:
            byte = struct.unpack("!B", msg[current_byte : current_byte + 1])
            value = (value << current_mask_size) | (current_mask & byte[0])

            current_mask_size = 8
            current_mask = self.create_mask(current_mask_size)
            current_byte = current_byte + 1

        discard_right_numbits = 8 - (last_bit_offset + 1)

        current_mask_size = current_mask_size - discard_right_numbits
        current_mask = self.create_mask(current_mask_size)

        byte = struct.unpack("!B", msg[current_byte : current_byte + 1])
        value = (value << current_mask_size) | (current_mask & (byte[0] >> discard_right_numbits))

        return value

    # Gets the the keys of a certain json file (last_file_opened -> the configs.json or an imported json file)
    #
    # @return: The list with all the keys of the file, in case of the file is empty or missing,
    #          the list contains a "-" key
    #
    def get_keys(self):
        keys_list = []
        if os.path.exists(last_file_opened_string):
            with open(last_file_opened_string, "r") as infile:
                try:
                    datafile_dict = json.load(infile)
                except:
                    datafile_dict = {}
            infile.close()
            if len(list(datafile_dict.keys())) > 0:
                keys_list = list(datafile_dict.keys())
                keys_list.sort(key=int)
            else:
                keys_list.append("-")
        else:
            keys_list.append("-")
        return keys_list

    # Loads the configuration with the selected configuration ID from a json file to the program variables
    # and to the UI, if the file is empty or missing,
    # calls the reset_ui function that resets the UI and all the internal program variables
    #
    # @param event: Nedded to allow the wx library to call this function when the user interacts with the UI
    #
    def load_config(self, event):
        global global_instructions_list
        global sensor_instructions_list
        global channels_info_list
        config_id = str(self.w_load_config.GetValue())
        datafile_dict = {}
        if os.path.exists(last_file_opened_string):
            with open(last_file_opened_string, "r") as infile:
                try:
                    datafile_dict = json.load(infile)
                except:
                    datafile_dict = {}
            if len(list(datafile_dict.keys())) != 0:
                if datafile_dict[config_id]["instructions_version"] != INSTRUCTIONS_VERSION:
                    msgb = wx.MessageDialog(
                        self, "The instructions version is invalid", "ERROR", wx.OK | wx.ICON_HAND
                    )
                    msgb.ShowModal()
                    return
                self.w_instructions_version.SetValue(str(INSTRUCTIONS_VERSION))
                if datafile_dict[config_id]["cfg_version"] != CONFIG_VERSION:
                    msgb = wx.MessageDialog(
                        self, "The config version is invalid", "ERROR", wx.OK | wx.ICON_HAND
                    )
                    msgb.ShowModal()
                    return
                self.w_cfg_version.SetValue(str(CONFIG_VERSION))
                self.w_baudrate.SetValue(str(datafile_dict[config_id]["baudrate"]))
                self.w_databits.SetValue(str(datafile_dict[config_id]["databits"]))
                self.w_parity.SetValue(PARITY_DIC[datafile_dict[config_id]["parity"]])
                self.w_stopbits.SetValue(STOP_BITS_DIC[datafile_dict[config_id]["stopbits"]])
                if datafile_dict[config_id]["swap"] == 0:
                    self.w_swap.SetValue("No")
                else:
                    self.w_swap.SetValue("Yes")
                self.w_timeout.SetValue(str(datafile_dict[config_id]["timeout"]))
                self.w_cfg_manufacturer.SetValue(
                    str(datafile_dict[config_id]["sensor_manufacturer"])
                )
                self.w_cfg_model.SetValue(str(datafile_dict[config_id]["sensor_model"]))
                self.w_cfg_desc.SetValue(str(datafile_dict[config_id]["description"]))
                global_instructions_list = datafile_dict[config_id]["global_instructions"]
                sensor_instructions_list = datafile_dict[config_id]["sensor_instructions"]
                self.w_instructions_global.SetValue(self.string_instructions(0))
                self.w_instructions_sensor.SetValue(self.string_instructions(1))
                channels_info_list = datafile_dict[config_id]["channels"]
                self.w_sensor_bytes.SetValue(
                    str(SENSOR_INSTRUCTIONS_BUFFER_SIZE_BYTES - self.get_size_instr(1))
                )
                self.w_global_bytes.SetValue(
                    str(GLOBAL_INSTRUCTIONS_BUFFER_SIZE_BYTES - self.get_size_instr(0))
                )
                self.w_data_msg_send.SetValue(
                    str(MESSAGE_MAX_SIZE_BYTES - self.get_data_msg_sensor_size_bytes())
                )

                self.update_num_of_sensors(event)
                max_sensors = int(datafile_dict[config_id]["max_allowed_sensors"])
                self.max_allowed_sensors_check_set_from_cfg(max_sensors)
                self.w_add_instr_glb_index.SetValue(str(len(global_instructions_list) + 1))
                self.w_add_instr_sns_index.SetValue(str(len(sensor_instructions_list) + 1))
                self.w_del_instr_glb_index.SetValue(str(len(global_instructions_list)))
                self.w_del_instr_sns_index.SetValue(str(len(sensor_instructions_list)))
            else:
                self.reset_ui()
        else:
            msgb = wx.MessageDialog(
                self, "The configuration file does not exist", "ERROR", wx.OK | wx.ICON_HAND
            )
            msgb.ShowModal()
            self.reset_ui()

    # Checks the input values from de UI, like the baudrate, swap, timeout, the configuration ID are an
    # admitted values, also checks the sizes of the push to data out instructions. Once all this values
    # are checked, all of them are stored into the
    # config_values_dict, the instructions list are stored in this dictionary too.
    # If the values are wrong, the function shows a message and doesn't store any value
    #
    # @return: True if all the values are correct and stored, otherwise returns False
    #
    def store_values(self):
        global sensors_list
        global config_values_dict
        try:
            sensors_list = self.w_sensors_ids.GetValue().split()
            num_sensors = len(sensors_list)
            max_sensors = int(self.w_max_allowed_sensors.GetValue())
            if num_sensors > max_sensors:
                msgb = wx.MessageDialog(
                    self,
                    "The list of ids exceeds the maximum allowed",
                    "ERROR",
                    wx.OK | wx.ICON_HAND,
                )
                msgb.ShowModal()
                return False
            for sid in sensors_list:
                if int(sid) > ((1 << 12) - 1):
                    msgb = wx.MessageDialog(
                        self, "Max sensor id value is 4095", "ERROR", wx.OK | wx.ICON_HAND
                    )
                    msgb.ShowModal()
                    return False
        except:
            msgb = wx.MessageDialog(self, "Could not parse ids", "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()
            return False

        try:
            baudrate = int(self.w_baudrate.GetValue())
            if baudrate < 0:
                msgb = wx.MessageDialog(
                    self, "The baudrate cant be negative", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return False
            config_values_dict["baudrate"] = baudrate
        except:
            msgb = wx.MessageDialog(
                self, "The baudrate is not an integer", "ERROR", wx.OK | wx.ICON_HAND
            )
            msgb.ShowModal()
            return False

        data_bits_str = self.w_databits.GetValue()
        if data_bits_str in DATA_BITS_LIST:
            config_values_dict["databits"] = int(data_bits_str)
        else:
            msgb = wx.MessageDialog(self, "Invalid data bits", "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()
            return False

        try:
            parity_str = self.w_parity.GetValue()
            parity = list(PARITY_DIC.keys())[list(PARITY_DIC.values()).index(parity_str)]
            config_values_dict["parity"] = parity
        except:
            msgb = wx.MessageDialog(self, "Invalid parity", "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()
            return False

        try:
            stop_bits_str = self.w_stopbits.GetValue()
            stop_bits = list(STOP_BITS_DIC.keys())[
                list(STOP_BITS_DIC.values()).index(stop_bits_str)
            ]
            config_values_dict["stopbits"] = stop_bits
        except:
            msgb = wx.MessageDialog(self, "Invalid stop bits", "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()
            return False

        if self.w_swap.GetValue() == "No":
            swap = 0
        else:
            if self.w_swap.GetValue() == "Yes":
                swap = 1
            else:
                msgb = wx.MessageDialog(
                    self, "The Word Swap is not a correct value", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return False
        config_values_dict["swap"] = swap
        try:
            timeout = int(self.w_timeout.GetValue())
            if timeout < 1:
                msgb = wx.MessageDialog(
                    self, "The timeout cant be lower than 1", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return False
            if timeout > 16777215:
                msgb = wx.MessageDialog(
                    self, "The timeout cant be higher than 16777215", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return False
            config_values_dict["timeout"] = timeout
        except:
            msgb = wx.MessageDialog(
                self, "The timeout is not an integer", "ERROR", wx.OK | wx.ICON_HAND
            )
            msgb.ShowModal()
            return False
        try:
            total_data = self.get_data_msg_sensor_size_bytes()

            if total_data > (MESSAGE_MAX_SIZE_BYTES):
                msgb = wx.MessageDialog(
                    self,
                    "The size of the values to send in a message is higher than the maximum value admitted (39 bytes)",
                    "ERROR",
                    wx.OK | wx.ICON_HAND,
                )
                msgb.ShowModal()
                return False
            if total_data * num_sensors > (MESSAGE_MAX_SIZE_BYTES * MAX_MESSAGES):
                msgb = wx.MessageDialog(
                    self,
                    "The number of data to sent for all sensors is higher than the maximum value admitedd (390 bytes)",
                    "ERROR",
                    wx.OK | wx.ICON_HAND,
                )
                msgb.ShowModal()
                return False
            if total_data == 0:
                msgb = wx.MessageDialog(
                    self,
                    'You need to add at least one "Push to data out" instruction in order to get some channel data',
                    "ERROR",
                    wx.OK | wx.ICON_HAND,
                )
                msgb.ShowModal()
                return False
        except:
            msgb = wx.MessageDialog(
                self, "Error calculating the data message size", "ERROR", wx.OK | wx.ICON_HAND
            )
            msgb.ShowModal()
            return False
        try:
            aux = int(self.w_load_config.GetValue())
            if aux < 0:
                msgb = wx.MessageDialog(
                    self, "The Config ID cant be lower than 0", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return False
            config_id = str(aux)
        except:
            msgb = wx.MessageDialog(
                self, "The Config ID is not an integer", "ERROR", wx.OK | wx.ICON_HAND
            )
            msgb.ShowModal()
            return False

        config_values_dict["sensor_manufacturer"] = str(self.w_cfg_manufacturer.GetValue())
        config_values_dict["sensor_model"] = str(self.w_cfg_model.GetValue())
        config_values_dict["description"] = str(self.w_cfg_desc.GetValue())
        config_values_dict["global_instructions"] = global_instructions_list
        config_values_dict["sensor_instructions"] = sensor_instructions_list
        config_values_dict["baudrate"] = baudrate
        config_values_dict["swap"] = swap
        config_values_dict["timeout"] = timeout
        config_values_dict["channels"] = channels_info_list
        config_values_dict["config_id"] = config_id
        config_values_dict["instructions_version"] = INSTRUCTIONS_VERSION
        config_values_dict["cfg_version"] = CONFIG_VERSION
        config_values_dict["max_allowed_sensors"] = max_sensors
        return True

    # Takes the config_values_dict filled in the store_values function and generates the messages that
    # the tool will send to the node and also
    # the messages required to the Dlog, if the function generates the messages correctly,
    # they will be stored in the config_values_dict
    #
    # @return: True if the message is generated and stored correctly, otherwise returns False
    #
    def generate_messages(self):
        global config_values_dict
        global sensors_list
        try:
            # FIRST MESSAGE (GENERIC MODBUS CHANNEL CONFIGURATION)
            type_of_sensor = 5  # 5=GENERIC MODBUS
            cfg_version = 0  # 0=base configuration
            output1 = "91"  # AM_TYPE
            output1 += "%0.2X" % type_of_sensor
            output1 += "%0.2X" % cfg_version
            output1 += "%0.6X" % config_values_dict["baudrate"]
            output1 += "%0.2X" % config_values_dict["databits"]
            output1 += "%0.2X" % config_values_dict["parity"]
            output1 += "%0.2X" % config_values_dict["stopbits"]
            output1 += "%0.2X" % len(sensors_list)
            for sensor in sensors_list:
                output1 += "%0.2X" % int(sensor)
            output1 = "\\x" + "\\x".join(a + b for a, b in zip(output1[::2], output1[1::2]))

            reserved_and_config_id = BitArray()
            reserved_and_config_id.append(
                bitstring.pack("uint:4,uint:12", 0, int(config_values_dict["config_id"]))
            )

            # SECOND MESSAGE (GENERIC MODBUS INSTRUCTIONS CONFIGURATION)
            output2 = "97"  # AM_TYPE
            output2 += "%0.2X" % INSTRUCTIONS_VERSION
            output2 += bytes.hex(reserved_and_config_id.tobytes())
            output2 += "%0.2X" % config_values_dict["swap"]
            output2 += "%0.6X" % config_values_dict["timeout"]
            output2 += "%0.2X" % len(global_instructions_list)

            global_instructions_out = BitArray()
            for instruction in global_instructions_list:
                global_instructions_out.append(bitstring.pack("uint:8", (instruction[0])))
                for x in range(0, len(instruction) - 1):
                    hex_size = "uint:" + str(INSTRUCTIONS_DICT[instruction[0]][1][x])
                    value = instruction[x + 1]
                    global_instructions_out.append(bitstring.pack(hex_size, value))
            while (
                int(math.ceil(global_instructions_out.len / 8.0))
                < GLOBAL_INSTRUCTIONS_BUFFER_SIZE_BYTES
            ):
                global_instructions_out.append(bitstring.pack("uint:8", 0))  # padding
            output2 += bytes.hex(global_instructions_out.tobytes())  # global instructions
            output2 += "%0.2X" % len(sensor_instructions_list)

            sensor_instructions_out = BitArray()
            for instruction in sensor_instructions_list:
                sensor_instructions_out.append(bitstring.pack("uint:8", (instruction[0])))
                for x in range(0, len(instruction) - 1):
                    hex_size = "uint:" + str(INSTRUCTIONS_DICT[instruction[0]][1][x])
                    value = instruction[x + 1]
                    sensor_instructions_out.append(bitstring.pack(hex_size, value))
            while int(sensor_instructions_out.len) < SENSOR_INSTRUCTIONS_BUFFER_SIZE_BYTES * 8:
                sensor_instructions_out.append(bitstring.pack("uint:1", 0))  # padding
            output2 += bytes.hex(sensor_instructions_out.tobytes())  # sensor instructions
            output2 = "\\x" + "\\x".join(a + b for a, b in zip(output2[::2], output2[1::2]))

            config_values_dict["string_global_instructions"] = bytes.hex(
                global_instructions_out.tobytes()
            )
            config_values_dict["string_sensor_instructions"] = bytes.hex(
                sensor_instructions_out.tobytes()
            )
            config_values_dict["message1"] = output1
            config_values_dict["message2"] = output2
            return True
        except:
            msgb = wx.MessageDialog(self, "Error creating message", "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()
            return False

    # Takes the config_values_dict filled in the generate_messages function and sends it to the node with
    # the defined tty in the UI if the tty is not an admitted value, the function shows a dialog and
    # doesn't send the messages, otherwise the configuration is sent to the node
    #
    def send_messages(self):
        try:
            tty = int(self.w_tty_usb.GetValue())
        except:
            msgb = wx.MessageDialog(
                self, "The tty is not an integer", "ERROR", wx.OK | wx.ICON_HAND
            )
            msgb.ShowModal()
            return
        tty_usb = "/dev/ttyUSB" + str(tty)
        ls_send_message_uart(config_values_dict["message1"], tty_usb, self)
        time.sleep(0.5)
        ls_send_message_uart(config_values_dict["message2"], tty_usb, self)

    # This function calls the store_values, generate_messages and send_messages functions, if the first
    # two functions returns a True, the message is sent
    # otherwise the message is not sent to the node
    #
    # @param event: Nedded to allow the wx library to call this function when the user interacts with the UI
    #
    def set_config(self, event):
        if self.store_values() and self.generate_messages():
            self.send_messages()

    # This function calls the functions store_values and generate_messages, and if both of them returns
    # True the function asks to the user if wants to update the Dlog file, in affirmative case the function
    # asks for the csv filename, in affirmative case the function generates
    # a new dictionary based on the config_values_dict dictionary.
    # Then the dictionary is stored in the generic_modbus_configs.json file
    # in an ordered way, finally stores the configuration in the configs.json file and if the config
    # already exists, the function asks to the user
    # if wants to rewrite it, otherwise is automatically saved.
    #
    # @param event: Nedded to allow the wx library to call this function when the user interacts with the UI
    #
    def save_config(self, event):
        if self.store_values() and self.generate_messages():
            global config_values_dict
            global last_file_opened_string
            config_id = str(self.w_load_config.GetValue())
            msgb = wx.MessageDialog(
                self,
                "Do you want to generate the Dlog/Gateway parser file?",
                "Confirm Save",
                wx.YES_NO,
            )
            result = msgb.ShowModal()
            if result == wx.ID_YES:
                dialog = wx.TextEntryDialog(
                    self,
                    ("Please enter the csv filename for this configuration for the Dlog file"),
                    ("csv filename"),
                    "",
                    wx.OK | wx.CANCEL | wx.TE_MULTILINE,
                )
                dialog.SetClientSize(wx.Size(400, 100))
                result = dialog.ShowModal()
                if result == wx.ID_OK:
                    data_config_dict = {}
                    data_config_dict["cfg_id"] = config_id
                    data_config_dict["cfg_version"] = CONFIG_VERSION
                    data_config_dict["max_allowed_sensors"] = config_values_dict[
                        "max_allowed_sensors"
                    ]
                    data_config_dict["manufacturer"] = config_values_dict["sensor_manufacturer"]
                    data_config_dict["sensor_model"] = config_values_dict["sensor_model"]
                    data_config_dict["description"] = config_values_dict["description"]
                    data_config_dict["created_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    data_config_dict["channels"] = channels_info_list
                    data_config_dict["csv_filename"] = dialog.GetValue()
                    config_parameters = {}
                    config_parameters["instructions_version"] = INSTRUCTIONS_VERSION
                    config_parameters["baudrate"] = config_values_dict["baudrate"]
                    config_parameters["databits"] = config_values_dict["databits"]
                    config_parameters["parity"] = config_values_dict["parity"]
                    config_parameters["stopbits"] = config_values_dict["stopbits"]
                    if config_values_dict["swap"] == 1:
                        config_parameters["word_swap"] = True
                    else:
                        config_parameters["word_swap"] = False
                    config_parameters["timeout"] = config_values_dict["timeout"]
                    config_parameters["number_global_instructions"] = len(
                        config_values_dict["global_instructions"]
                    )
                    config_parameters["number_sensor_instructions"] = len(
                        config_values_dict["sensor_instructions"]
                    )
                    config_parameters["global_instructions"] = config_values_dict[
                        "string_global_instructions"
                    ]
                    config_parameters["sensor_instructions"] = config_values_dict[
                        "string_sensor_instructions"
                    ]
                    data_config_dict["cfg_parameters"] = config_parameters

                    abs_path = Path(os.path.dirname(os.path.abspath(__file__)))
                    abs_path = abs_path.parent
                    str_path = os.path.join(
                        str(abs_path), "lib/GenericModbusDataCfgs/generic_modbus_configs.json"
                    )
                    datafile_list = []
                    if os.path.exists(str_path):
                        with open(str_path, "r") as infile:
                            try:
                                datafile_list = json.load(infile)
                            except:
                                datafile_list = []
                        infile.close()
                        added = False
                        for x in range(0, len(datafile_list)):
                            if int(datafile_list[x]["cfg_id"]) == int(config_id):
                                msgb = wx.MessageDialog(
                                    self,
                                    "You will overwrite an existing configuration in the DLog file",
                                    "Confirm Save",
                                    wx.OK | wx.CANCEL,
                                )
                                result = msgb.ShowModal()
                                if result == wx.ID_OK:
                                    datafile_list[x] = data_config_dict
                                added = True
                                break
                            if int(datafile_list[x]["cfg_id"]) > int(config_id):
                                datafile_list.insert(x, data_config_dict)
                                added = True
                                break
                        if not added:
                            datafile_list.append(data_config_dict)
                        with open(str_path, "w") as outfile:
                            json.dump(datafile_list, outfile, indent=4, sort_keys=True)
                        outfile.close()
                    else:
                        msgb = wx.MessageDialog(
                            self, "The Dlog file does not exist, creating", "INFO", wx.OK
                        )
                        msgb.ShowModal()
                        with open(str_path, "w") as outfile:
                            json.dump(data_config_dict, outfile, indent=4, sort_keys=True)
                        outfile.close()

            datafile_dict = {}
            del config_values_dict["config_id"]
            if os.path.exists("configs.json"):
                with open("configs.json", "r") as infile:
                    try:
                        datafile_dict = json.load(infile)
                    except:
                        datafile_dict = {}
                infile.close()
                if config_id not in list(datafile_dict.keys()):
                    config_values_dict["created_date"] = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    datafile_dict[config_id] = config_values_dict
                else:
                    msgb = wx.MessageDialog(
                        self,
                        "You will overwrite an existing configuration in the configurations file",
                        "Confirm Save",
                        wx.OK | wx.CANCEL,
                    )
                    result = msgb.ShowModal()
                    if result == wx.ID_OK:
                        config_values_dict["updated_date"] = datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        datafile_dict[config_id].update(config_values_dict)
                with open("configs.json", "w") as outfile:
                    json.dump(datafile_dict, outfile, indent=4, sort_keys=True)
                outfile.close()
                last_file_opened_string = "configs.json"
                list_ids = list(datafile_dict.keys())
                list_ids.sort(key=int)
                self.w_load_config.Set(list_ids)
            else:
                msgb = wx.MessageDialog(
                    self, "The configuration file does not exist, creating", "INFO", wx.OK
                )
                msgb.ShowModal()
                config_values_dict["created_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                datafile_dict[config_id] = config_values_dict
                with open("configs.json", "w") as outfile:
                    json.dump(datafile_dict, outfile, indent=4, sort_keys=True)
                outfile.close()
                last_file_opened_string = "configs.json"
                list_ids = list(datafile_dict.keys())
                list_ids.sort(key=int)
                self.w_load_config.Set(list_ids)

    # Deletes all the UI fields and deletes the global variables used in the program
    #
    def reset_ui(self):
        global global_instructions_list
        global sensor_instructions_list
        global channels_info_list
        self.w_load_config.SetValue("-")
        self.w_cfg_version.SetValue(str(CONFIG_VERSION))
        self.w_cfg_version.SetValue(str(INSTRUCTIONS_VERSION))
        self.w_baudrate.SetValue("-")
        self.w_databits.SetValue("-")
        self.w_parity.SetValue("-")
        self.w_stopbits.SetValue("-")
        self.w_swap.SetValue("-")
        self.w_timeout.SetValue("-")
        self.w_cfg_manufacturer.SetValue("-")
        self.w_cfg_model.SetValue("-")
        self.w_cfg_desc.SetValue("-")
        self.w_instructions_global.SetValue("")
        self.w_instructions_sensor.SetValue("")
        global_instructions_list = []
        sensor_instructions_list = []
        channels_info_list = []
        self.w_instructions_global.SetValue(self.string_instructions(0))
        self.w_instructions_sensor.SetValue(self.string_instructions(1))
        self.w_sensor_bytes.SetValue(
            str(SENSOR_INSTRUCTIONS_BUFFER_SIZE_BYTES - self.get_size_instr(1))
        )
        self.w_global_bytes.SetValue(
            str(GLOBAL_INSTRUCTIONS_BUFFER_SIZE_BYTES - self.get_size_instr(0))
        )
        self.w_sensors_ids.SetValue("")
        self.w_data_msg_send.SetValue(str(MESSAGE_MAX_SIZE_BYTES))
        self.w_data_all_msg_send.SetValue(str(MESSAGE_MAX_SIZE_BYTES * MAX_MESSAGES))
        self.w_add_instr_glb_index.SetValue(str(len(global_instructions_list) + 1))
        self.w_add_instr_sns_index.SetValue(str(len(sensor_instructions_list) + 1))
        self.w_del_instr_glb_index.SetValue(str(len(global_instructions_list)))
        self.w_del_instr_sns_index.SetValue(str(len(sensor_instructions_list)))

    # Deletes the configuration with the configuration ID selected in the UI on the configs.json file
    #
    # @param event: Nedded to allow the wx library to call this function when the user interacts with the UI
    #
    def delete_config(self, event):
        global last_file_opened_string
        msgb = wx.MessageDialog(
            self, "Do you want to delete the actual config?", "Confirm Delete", wx.YES_NO
        )
        result = msgb.ShowModal()
        if result == wx.ID_YES:
            config_id = self.w_load_config.GetValue()
            datafile_dict = {}
            if os.path.exists(last_file_opened_string):
                with open(last_file_opened_string, "r") as infile:
                    try:
                        datafile_dict = json.load(infile)
                    except:
                        datafile_dict = {}
                infile.close()
                datafile_dict.pop(config_id, None)
                with open(last_file_opened_string, "w") as outfile:
                    json.dump(datafile_dict, outfile, indent=4, sort_keys=True)
                outfile.close()
                list_ids = list(datafile_dict.keys())
                list_ids.sort(key=int)
                self.w_load_config.Set(list_ids)
            if "configs.json" == last_file_opened_string:
                abs_path = Path(os.path.dirname(os.path.abspath(__file__)))
                abs_path = abs_path.parent
                str_path = os.path.join(
                    str(abs_path), "lib/GenericModbusDataCfgs/generic_modbus_configs.json"
                )
                if os.path.exists(str_path):
                    with open(str_path, "r") as infile:
                        try:
                            datafile_list = json.load(infile)
                        except:
                            datafile_list = []
                    infile.close()
                    index = 0
                    for x in range(0, len(datafile_list)):
                        if datafile_list[x]["cfg_id"] == config_id:
                            index = x
                    del datafile_list[index]
                    with open(str_path, "w") as outfile:
                        json.dump(datafile_list, outfile, indent=4, sort_keys=True)
                    outfile.close()
            self.reset_ui()

    # This function calls runs two subprocesses that communicates with the node and obtains the
    # configuration and loads it to the UI and
    # to the global varibales used in the program
    #
    # @param event: Nedded to allow the wx library to call this function when the user interacts with the UI
    #
    def request_config(self, event):
        global global_instructions_list
        global sensor_instructions_list
        global channels_info_list
        try:
            tty = int(self.w_tty_usb.GetValue())
        except:
            msgb = wx.MessageDialog(
                self, "The tty is not an integer", "ERROR", wx.OK | wx.ICON_HAND
            )
            msgb.ShowModal()
            return
        tty_usb = "/dev/ttyUSB" + str(tty)
        path = Path(os.path.dirname(os.path.abspath(__file__)))
        path = path.parent
        my_file = os.path.join(str(path), "ls_serial_view.py")
        arguments = [str(my_file), str(tty_usb)]

        p = subprocess.Popen(
            arguments, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        time.sleep(0.5)
        ls_send_message_uart("\\x00\\x91", tty_usb, self)
        time.sleep(0.5)
        p.terminate()
        string_out_1 = p.communicate()[0]
        values_out_1_list = string_out_1[
            string_out_1.find(" 40 ") + 1 : string_out_1.find("PrCode") - 1
        ].split()
        p = subprocess.Popen(
            arguments, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        time.sleep(0.5)
        ls_send_message_uart("\\x00\\x97", tty_usb, self)
        time.sleep(0.5)
        p.terminate()
        string_out_2 = p.communicate()[0]
        values_out_2_list = string_out_2[
            string_out_2.find(" 40 ") + 1 : string_out_2.find("PrCode") - 1
        ].split()
        if len(values_out_1_list) == 0 or len(values_out_2_list) == 0:
            msgb = wx.MessageDialog(
                self,
                "The node is not responding or you have the serial view opened",
                "ERROR",
                wx.OK | wx.ICON_HAND,
            )
            msgb.ShowModal()
            return
        if values_out_1_list[5] != "91":
            msgb = wx.MessageDialog(self, "Wrong response message", "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()
            return
        # baudrate 8-9-10
        list_value = "".join(values_out_1_list[8:11])
        baudrate = str(int(list_value, 16))
        self.w_baudrate.SetValue(baudrate)
        data_bits = int(values_out_1_list[11], 16)
        self.w_databits.SetValue(str(data_bits))
        parity = int(values_out_1_list[12], 16)
        self.w_parity.SetValue(PARITY_DIC[parity])
        stop_bits = int(values_out_1_list[13], 16)
        self.w_stopbits.SetValue(STOP_BITS_DIC[stop_bits])
        # num of sensors
        num_sensors = int(values_out_1_list[14], 16)
        # ids of sensors
        string_sensors = ""
        for x in range(0, num_sensors):
            sensor = str(int(values_out_1_list[15 + x], 16))
            string_sensors += sensor + " "
        self.w_sensors_ids.SetValue(string_sensors)

        index = 5
        if values_out_2_list[index] != "97":
            msgb = wx.MessageDialog(self, "Wrong response message", "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()
            return
        # instructions version
        index += 1
        if (int(values_out_2_list[index], 16) & 0x0F) != INSTRUCTIONS_VERSION:
            msgb = wx.MessageDialog(self, "Incompatible version", "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()
            return
        else:
            self.w_instructions_version.SetValue(str(INSTRUCTIONS_VERSION))
        # config_id
        index += 1
        list_value = "".join(values_out_2_list[index : index + 2])
        config_id_int = int(list_value, 16) & 0x0FFF
        config_id = str(config_id_int)
        if os.path.exists("configs.json"):
            with open("configs.json", "r") as infile:
                try:
                    datafile_dict = json.load(infile)
                except:
                    datafile_dict = {}
            infile.close()
            if config_id in list(datafile_dict.keys()):
                self.w_cfg_manufacturer.SetValue(
                    str(datafile_dict[config_id]["sensor_manufacturer"])
                )
                self.w_cfg_model.SetValue(str(datafile_dict[config_id]["sensor_model"]))
                self.w_cfg_desc.SetValue(str(datafile_dict[config_id]["description"]))
            else:
                self.w_cfg_manufacturer.SetValue("-")
                self.w_cfg_model.SetValue("-")
                self.w_cfg_desc.SetValue("-")
        else:
            self.w_cfg_manufacturer.SetValue("-")
            self.w_cfg_model.SetValue("-")
            self.w_cfg_desc.SetValue("-")

        self.w_load_config.SetValue(config_id)
        index += 2
        if values_out_2_list[index] == "01":
            self.w_swap.SetValue("Yes")
        elif values_out_2_list[index] == "00":
            self.w_swap.SetValue("No")
        else:
            msgb = wx.MessageDialog(self, "Unknown word swap", "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()
            return
        # TIMEOUT 10-11-12
        index += 1
        size_timeout = 3
        list_value = "".join(values_out_2_list[index : index + size_timeout])
        timeout = str(int(list_value, 16))
        self.w_timeout.SetValue(timeout)

        # global instructions
        index += size_timeout
        num_glb_instr = int(values_out_2_list[index], 16)

        index += 1
        instructions = values_out_2_list[index : index + GLOBAL_INSTRUCTIONS_BUFFER_SIZE_BYTES]
        instructions_str = "".join(chr(int(s, 16)) for s in instructions)
        global_instructions_list = []
        size_instr = 0
        for x in range(num_glb_instr):
            instruction = []
            id_instr = self.extract_bits_from_array(instructions_str, size_instr, 8)
            instruction.append(id_instr)
            size_instr += 8
            for argument in INSTRUCTIONS_DICT[id_instr][1]:
                if argument != 0:
                    instruction.append(
                        self.extract_bits_from_array(instructions_str, size_instr, argument)
                    )
                    size_instr += argument
            global_instructions_list.append(instruction)
        self.w_instructions_global.SetValue(self.string_instructions(0))

        # sensor instructions
        index += GLOBAL_INSTRUCTIONS_BUFFER_SIZE_BYTES
        num_sns_instr = int(values_out_2_list[index], 16)
        index += 1
        size_sensor_instructions = SENSOR_INSTRUCTIONS_BUFFER_SIZE_BYTES
        instructions = values_out_2_list[index : index + size_sensor_instructions]
        instructions_str = "".join(chr(int(s, 16)) for s in instructions)
        sensor_instructions_list = []
        channels_info_list = []
        size_instr = 0
        data_channel = 0
        for x in range(num_sns_instr):
            instruction = []
            id_instr = self.extract_bits_from_array(instructions_str, size_instr, 8)
            if id_instr == 23:
                data_channel = True
            instruction.append(id_instr)
            size_instr += 8
            for argument in INSTRUCTIONS_DICT[id_instr][1]:
                if argument != 0:
                    instruction.append(
                        self.extract_bits_from_array(instructions_str, size_instr, argument)
                    )
                    if data_channel:
                        channel_dict = {}
                        channel_dict["signed_value"] = False
                        channel_dict["check_out_of_range"] = False
                        channel_dict["label"] = "No Label"
                        channel_dict["unit"] = "No Unit"
                        channel_dict["data_size"] = self.extract_bits_from_array(
                            instructions_str, size_instr, argument
                        )
                        channel_dict["data_conversion"] = True
                        channel_dict["conversion_func_python"] = ""
                        channel_dict["conversion_func_android"] = ""
                        channel_dict["chn_num"] = len(channels_info_list) + 1
                        channels_info_list.append(channel_dict)
                        data_channel = False
                size_instr += argument
            sensor_instructions_list.append(instruction)
        self.w_instructions_sensor.SetValue(self.string_instructions(1))
        self.w_sensor_bytes.SetValue(
            str(SENSOR_INSTRUCTIONS_BUFFER_SIZE_BYTES - self.get_size_instr(1))
        )
        self.w_global_bytes.SetValue(
            str(GLOBAL_INSTRUCTIONS_BUFFER_SIZE_BYTES - self.get_size_instr(0))
        )
        self.w_data_msg_send.SetValue(
            str(MESSAGE_MAX_SIZE_BYTES - self.get_data_msg_sensor_size_bytes())
        )
        self.w_data_all_msg_send.SetValue(
            str(
                (MESSAGE_MAX_SIZE_BYTES * MAX_MESSAGES)
                - (self.get_data_msg_sensor_size_bytes() * num_sensors)
            )
        )
        self.w_max_allowed_sensors.SetValue(str(self.get_max_allowed_sensors()))
        self.max_allowed_sensors_check_set(False)
        self.w_add_instr_glb_index.SetValue(str(len(global_instructions_list) + 1))
        self.w_add_instr_sns_index.SetValue(str(len(sensor_instructions_list) + 1))
        self.w_del_instr_glb_index.SetValue(str(len(global_instructions_list)))
        self.w_del_instr_sns_index.SetValue(str(len(sensor_instructions_list)))
        self.w_cfg_version.SetValue(str(CONFIG_VERSION))

    # Calculates the size in bytes of all the instructions in the global or sensor instructions list.
    #
    # @param option: Integer to select which size the function returns, the size of the global instructions
    #                or the sensor instructions
    #
    def get_size_instr(self, option):
        size = 0
        if option == 0:
            for instruction in global_instructions_list:
                for x in range(len(instruction) - 1):
                    size += INSTRUCTIONS_DICT[instruction[0]][1][x]
                size += 8
            size = size / 8.0
            return size
        if option == 1:
            for instruction in sensor_instructions_list:
                for x in range(len(instruction) - 1):
                    size += INSTRUCTIONS_DICT[instruction[0]][1][x]
                size += 8
            size = size / 8.0
            return size

    def get_data_msg_sensor_size_bits(self):
        size = 0
        for channel in channels_info_list:
            size += channel["data_size"]
        size += 1  # error bit (1 per sensor)
        return size

    # Calculates the size in bytes of the total data that will be sent through a message.
    #

    def get_data_msg_sensor_size_bytes(self):
        return self.get_data_msg_sensor_size_bits() / 8.0

    def get_max_allowed_sensors(self):
        sensor_size_bits = self.get_data_msg_sensor_size_bits()
        sensors_per_frame = (MESSAGE_MAX_SIZE_BYTES * 8) / sensor_size_bits
        max_sensors = sensors_per_frame * MAX_MESSAGES
        if max_sensors > MAX_SENSORS_IN_CONFIG:
            max_sensors = MAX_SENSORS_IN_CONFIG
        return max_sensors

    # This function checks that the instruction is a general instruction, checks if the arguments are valid
    # and if the instruction doesn't pass the maximum size
    # also checks if the index value next to the add instruction button is a valid index,
    # adds it to the general instructions list, otherwise the function displays an error message and
    # doesn't add the instruction to the list
    #
    # @param event: Nedded to allow the wx library to call this function when the user interacts with the UI
    #
    def add_glb_instr(self, event):
        arrayvalues = [
            self.w_arg1.GetValue(),
            self.w_arg2.GetValue(),
            self.w_arg3.GetValue(),
            self.w_arg4.GetValue(),
        ]
        id = self.get_id_instruction(self.w_instruction.GetValue())
        arrayarguments = INSTRUCTIONS_DICT[id][1]
        i = 0
        instruction = [id]
        if self.w_instruction.GetValue() in global_set_instructions_list:
            for argument in arrayarguments:
                if argument != 0:
                    if arrayvalues[i] == "":
                        msgb = wx.MessageDialog(
                            self, "Empty arguments", "ERROR", wx.OK | wx.ICON_HAND
                        )
                        msgb.ShowModal()
                        return
                    if not self.is_number(arrayvalues[i]):
                        msgb = wx.MessageDialog(
                            self,
                            "The argument " + str(i + 1) + " is not a number",
                            "ERROR",
                            wx.OK | wx.ICON_HAND,
                        )
                        msgb.ShowModal()
                        return
                    if int(2 ** argument - 1) < int(self.to_int(arrayvalues[i])):
                        msgb = wx.MessageDialog(
                            self,
                            "The maximum value for the argument "
                            + str(i + 1)
                            + " is "
                            + str(2 ** argument - 1),
                            "ERROR",
                            wx.OK | wx.ICON_HAND,
                        )
                        msgb.ShowModal()
                        return
                    else:
                        int_value = self.to_int(arrayvalues[i])
                        instruction.append(int_value)
                i += 1
            instruction_index = self.w_add_instr_glb_index.GetValue()
            if not self.is_number(instruction_index):
                msgb = wx.MessageDialog(
                    self, "The instruction index is not a number", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return
            if self.to_int(instruction_index) > len(global_instructions_list) + 1:
                msgb = wx.MessageDialog(
                    self,
                    "The instruction index is out of the range of the instructions in the list",
                    "ERROR",
                    wx.OK | wx.ICON_HAND,
                )
                msgb.ShowModal()
                return
            global_instructions_list.insert(self.to_int(instruction_index) - 1, instruction)
            size_instr = self.get_size_instr(0)
            if size_instr > GLOBAL_INSTRUCTIONS_BUFFER_SIZE_BYTES:
                msgb = wx.MessageDialog(
                    self,
                    "The instruction you add to the global buffer makes the total size bigger than the "
                    "allowed, the instruction wont be added",
                    "ERROR",
                    wx.OK | wx.ICON_HAND,
                )
                msgb.ShowModal()
                del global_instructions_list[self.to_int(instruction_index) - 1]
                size_instr = self.get_size_instr(0)
            self.w_instructions_global.SetValue(self.string_instructions(0))
            self.w_global_bytes.SetValue(str(GLOBAL_INSTRUCTIONS_BUFFER_SIZE_BYTES - size_instr))
            self.w_del_instr_glb_index.SetValue(str(len(global_instructions_list)))
            self.w_add_instr_glb_index.SetValue(str(len(global_instructions_list) + 1))
        else:
            msgb = wx.MessageDialog(self, "Not a global instruction", "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()
            return

    # This function checks if the arguments are valid and if the instruction doesn't pass the maximum size
    # also checks if the index value next to the add instruction button is a valid index
    # adds it to the sensor instructions list and adds all the information of the data that will be pushed
    # out to a list of dictionaries
    # that will be stored in the jsons files in order to parse the information correctly, otherwise
    # the function displays an error message and doesn't add the instruction to the lists
    #
    # @param event: Nedded to allow the wx library to call this function when the user interacts with the UI
    #
    def add_sensor_instr(self, event):
        arrayvalues = [
            self.w_arg1.GetValue(),
            self.w_arg2.GetValue(),
            self.w_arg3.GetValue(),
            self.w_arg4.GetValue(),
        ]
        id = self.get_id_instruction(self.w_instruction.GetValue())
        arrayarguments = INSTRUCTIONS_DICT[id][1]
        instruction_index = self.w_add_instr_sns_index.GetValue()
        i = 0
        instruction = [id]
        for argument in arrayarguments:
            if argument != 0:
                if arrayvalues[i] == "":
                    msgb = wx.MessageDialog(self, "Empty arguments", "ERROR", wx.OK | wx.ICON_HAND)
                    msgb.ShowModal()
                    return
                if not self.is_number(arrayvalues[i]):
                    msgb = wx.MessageDialog(
                        self,
                        "The argument " + str(i + 1) + " is not a number",
                        "ERROR",
                        wx.OK | wx.ICON_HAND,
                    )
                    msgb.ShowModal()
                    return
                if int(2 ** argument - 1) < int(self.to_int(arrayvalues[i])):
                    msgb = wx.MessageDialog(
                        self,
                        "The maximum value for the argument "
                        + str(i + 1)
                        + " is "
                        + str(2 ** argument - 1),
                        "ERROR",
                        wx.OK | wx.ICON_HAND,
                    )
                    msgb.ShowModal()
                    return
                else:
                    int_value = self.to_int(arrayvalues[i])
                    instruction.append(int_value)
            i += 1
        if not self.is_number(instruction_index):
            msgb = wx.MessageDialog(
                self, "The instruction index is not a number", "ERROR", wx.OK | wx.ICON_HAND
            )
            msgb.ShowModal()
            return
        if self.to_int(instruction_index) > len(sensor_instructions_list) + 1:
            msgb = wx.MessageDialog(
                self,
                "The instruction index is out of the range of the instructions in the list",
                "ERROR",
                wx.OK | wx.ICON_HAND,
            )
            msgb.ShowModal()
            return
        if instruction[0] == 23:  # PUSH TO DATA OUT INSTRUCTION
            if MESSAGE_MAX_SIZE_BYTES < (
                self.get_data_msg_sensor_size_bytes() + (int(instruction[1]) / 8.0)
            ):
                msgb = wx.MessageDialog(
                    self,
                    "The number of data sent for one sensor is higher than ("
                    + str(MESSAGE_MAX_SIZE_BYTES)
                    + " bytes)",
                    "ERROR",
                    wx.OK | wx.ICON_HAND,
                )
                msgb.ShowModal()
                return
            if self.w_label.GetValue() == "":
                msgb = wx.MessageDialog(self, "Empty Channel label", "ERROR", wx.OK | wx.ICON_HAND)
                msgb.ShowModal()
                return
            if self.w_data_units.GetValue() == "":
                msgb = wx.MessageDialog(self, "Empty Data units", "ERROR", wx.OK | wx.ICON_HAND)
                msgb.ShowModal()
                return
            if self.w_signed_value.GetValue() == "No":
                signed_value = False
            else:
                signed_value = True
            if self.w_check_out_of_range.GetValue() == "No":
                check_out_of_range = False
            else:
                check_out_of_range = True
            channel_dict = {}
            channel_dict["signed_value"] = signed_value
            channel_dict["check_out_of_range"] = check_out_of_range
            channel_dict["label"] = self.w_label.GetValue()
            channel_dict["unit"] = self.w_data_units.GetValue()
            channel_dict["data_size"] = int(instruction[1])
            channel_dict["data_conversion"] = True
            channel_dict["conversion_func_python"] = ""
            channel_dict["conversion_func_android"] = ""
            index = 0
            for x in range(0, int(instruction_index) - 1):
                if sensor_instructions_list[x][0] == 23:
                    index += 1
            channel_dict["chn_num"] = index + 1
            channels_info_list.insert(index, channel_dict)
            index = 1
            for channel in channels_info_list:
                channel["chn_num"] = index
                index += 1
            self.w_data_msg_send.SetValue(
                str(MESSAGE_MAX_SIZE_BYTES - (self.get_data_msg_sensor_size_bytes()))
            )
            if self.w_max_allowed_sensors_check.IsChecked() is False:
                self.w_max_allowed_sensors.SetValue(str(self.get_max_allowed_sensors()))

        sensor_instructions_list.insert(self.to_int(instruction_index) - 1, instruction)
        size_instr = self.get_size_instr(1)
        if size_instr > SENSOR_INSTRUCTIONS_BUFFER_SIZE_BYTES:
            msgb = wx.MessageDialog(
                self,
                "The instruction you add to the sensor buffer makes the total size bigger than the allowed, "
                "the instruction wont be added",
                "ERROR",
                wx.OK | wx.ICON_HAND,
            )
            msgb.ShowModal()
            del sensor_instructions_list[self.to_int(instruction_index) - 1]
        self.w_instructions_sensor.SetValue(self.string_instructions(1))
        self.w_sensor_bytes.SetValue(str(SENSOR_INSTRUCTIONS_BUFFER_SIZE_BYTES - size_instr))
        self.w_del_instr_sns_index.SetValue(str(len(sensor_instructions_list)))
        self.w_add_instr_sns_index.SetValue(str(len(sensor_instructions_list) + 1))

    # Checks if the index value next to the add instruction button is a valid index and deletes the
    # instruction of the list of the global instructions or from the sensor instructions with the specified
    # index, if the instruction is a push to data out,
    # the function deletes all the information of the channels info list associated to that instruction.
    #
    # @param event: Nedded to allow the wx library to call this function when the user interacts with the UI
    # @param option: Integer to select from which list delete the last instruction
    #
    def del_instr(self, event, option):
        if option == 0:
            global global_instructions_list
            if len(global_instructions_list) > 0:
                id_instruction = self.w_del_instr_glb_index.GetValue()
                if not self.is_number(id_instruction):
                    msgb = wx.MessageDialog(
                        self, "The instruction index is not a number", "ERROR", wx.OK | wx.ICON_HAND
                    )
                    msgb.ShowModal()
                    return
                if self.to_int(id_instruction) > len(global_instructions_list):
                    msgb = wx.MessageDialog(
                        self,
                        "The instruction index is out of the range of the instructions in the list",
                        "ERROR",
                        wx.OK | wx.ICON_HAND,
                    )
                    msgb.ShowModal()
                    return
                del global_instructions_list[self.to_int(id_instruction) - 1]
                self.w_instructions_global.SetValue(self.string_instructions(0))
                self.w_global_bytes.SetValue(
                    str(GLOBAL_INSTRUCTIONS_BUFFER_SIZE_BYTES - self.get_size_instr(0))
                )
                self.w_del_instr_glb_index.SetValue(str(len(global_instructions_list)))
                self.w_add_instr_glb_index.SetValue(str(len(global_instructions_list) + 1))
                return
        if option == 1:
            global sensors_list
            if len(sensor_instructions_list) > 0:
                id_instruction = self.w_del_instr_sns_index.GetValue()
                if not self.is_number(id_instruction):
                    msgb = wx.MessageDialog(
                        self, "The instruction index is not a number", "ERROR", wx.OK | wx.ICON_HAND
                    )
                    msgb.ShowModal()
                    return
                if self.to_int(id_instruction) > len(sensor_instructions_list):
                    msgb = wx.MessageDialog(
                        self,
                        "The instruction index is out of the range of the instructions in the list",
                        "ERROR",
                        wx.OK | wx.ICON_HAND,
                    )
                    msgb.ShowModal()
                    return
                if sensor_instructions_list[self.to_int(id_instruction) - 1][0] == 23:
                    id_push = 0
                    for x in range(len(sensor_instructions_list)):
                        if sensor_instructions_list[x][0] == 23:
                            if x == (self.to_int(id_instruction) - 1):
                                break
                            id_push += 1
                    if len(channels_info_list) > 0:
                        del channels_info_list[id_push]
                    for x in range(len(channels_info_list)):
                        channels_info_list[x]["chn_num"] = x + 1
                    self.w_data_msg_send.SetValue(
                        str(MESSAGE_MAX_SIZE_BYTES - self.get_data_msg_sensor_size_bytes())
                    )
                    total_sensors = len(sensors_list)
                    self.w_data_all_msg_send.SetValue(
                        str(
                            MESSAGE_MAX_SIZE_BYTES * MAX_MESSAGES
                            - self.get_data_msg_sensor_size_bytes() * total_sensors
                        )
                    )
                    if self.w_max_allowed_sensors_check.IsChecked() is False:
                        self.w_max_allowed_sensors.SetValue(str(self.get_max_allowed_sensors()))
                del sensor_instructions_list[self.to_int(id_instruction) - 1]
                self.w_instructions_sensor.SetValue(self.string_instructions(1))
                self.w_sensor_bytes.SetValue(
                    str(SENSOR_INSTRUCTIONS_BUFFER_SIZE_BYTES - self.get_size_instr(1))
                )
                self.w_del_instr_sns_index.SetValue(str(len(sensor_instructions_list)))
                self.w_add_instr_sns_index.SetValue(str(len(sensor_instructions_list) + 1))

    # Makes a string with all the instructions (general or sensor) with the name of the instruction
    # (not the code) and all the arguments in hex format
    #
    # @param option: Integer to select from which list generate the string
    # @return: A string that contents all of the instructions
    #
    def string_instructions(self, option):
        number_instruction = 1
        if option == 0:
            string_instr = ""
            for instruction in global_instructions_list:
                string_instr += str(number_instruction) + ": "
                string_instr += INSTRUCTIONS_DICT[instruction[0]][0] + " "
                for x in range(1, len(instruction)):
                    hex_value = "0x%0.2X" % int(instruction[x])
                    string_instr += str(hex_value) + " "
                string_instr += "\n"
                number_instruction += 1
            return string_instr
        if option == 1:
            string_instr = ""
            for instruction in sensor_instructions_list:
                string_instr += str(number_instruction) + ": "
                string_instr += INSTRUCTIONS_DICT[instruction[0]][0] + " "
                for x in range(1, len(instruction)):
                    hex_value = "0x%0.2X" % int(instruction[x])
                    string_instr += str(hex_value) + " "
                string_instr += "\n"
                number_instruction += 1
            return string_instr

    # Depending on the instruction selected, enables or disables the required arguments, label and data units fields.
    #
    # @param event: Nedded to allow the wx library to call this function when the user interacts with the UI
    #
    def edit_args(self, event):
        id = self.get_id_instruction(self.w_instruction.GetValue())
        arguments_sizes_list = INSTRUCTIONS_DICT[id][1]
        arguments_fields_list = [self.w_arg1, self.w_arg2, self.w_arg3, self.w_arg4]
        i = 0
        for arg in arguments_sizes_list:
            arguments_fields_list[i].SetValue("")
            if arg == 0:
                arguments_fields_list[i].Disable()
            else:
                arguments_fields_list[i].Enable()
            i += 1
        self.w_label.SetValue("")
        self.w_data_units.SetValue("")
        if self.w_instruction.GetValue() == INSTRUCTIONS_DICT[23][0]:
            self.w_label.Enable()
            self.w_data_units.Enable()
            self.w_signed_value.Enable()
            self.w_check_out_of_range.Enable()
        else:
            self.w_label.Disable()
            self.w_data_units.Disable()
            self.w_signed_value.Disable()
            self.w_check_out_of_range.Disable()

    # Opens a window to select a json file in order to load the configuration to the program variables,
    # makes this file the default file in order
    # to navigate through all configurations of this file in the GUI, otherwise the configs.json is the
    # default file and the UI is reset.
    #
    # @param event: Nedded to allow the wx library to call this function when the user interacts with the UI
    #
    def on_open(self, event):
        global global_instructions_list
        global sensor_instructions_list
        global last_file_opened_string
        global channels_info_list
        wildcard = "JSON files (*.json)|*.json"
        dialog = wx.FileDialog(
            self, "Import Config Files", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )
        if dialog.ShowModal() == wx.ID_CANCEL:
            return
        path = dialog.GetPath()
        last_file_opened_string = path
        if os.path.exists(path):
            with open(path) as infile:
                try:
                    datafile_dict = json.load(infile)
                except:
                    datafile_dict = {}
            if len(list(datafile_dict.keys())) > 0:
                config_id = str(list(datafile_dict.keys())[0])
                self.w_load_config.Set(sorted(datafile_dict.keys()))
                self.w_load_config.SetValue(config_id)
                if datafile_dict[config_id]["instructions_version"] != INSTRUCTIONS_VERSION:
                    msgb = wx.MessageDialog(
                        self,
                        "The instruction version in default cfg is ivalid",
                        "ERROR",
                        wx.OK | wx.ICON_HAND,
                    )
                    msgb.ShowModal()
                    return
                self.w_instructions_version.SetValue(str(INSTRUCTIONS_VERSION))
                if datafile_dict[config_id]["cfg_version"] != CONFIG_VERSION:
                    msgb = wx.MessageDialog(
                        self,
                        "The config version in default cfg is ivalid",
                        "ERROR",
                        wx.OK | wx.ICON_HAND,
                    )
                    msgb.ShowModal()
                    return
                self.w_cfg_version.SetValue(str(CONFIG_VERSION))
                self.w_baudrate.SetValue(str(datafile_dict[config_id]["baudrate"]))
                self.w_databits.SetValue(str(datafile_dict[config_id]["databits"]))
                self.w_parity.SetValue(PARITY_DIC[datafile_dict[config_id]["parity"]])
                self.w_stopbits.SetValue(STOP_BITS_DIC[datafile_dict[config_id]["stopbits"]])
                if datafile_dict[config_id]["swap"] == 0:
                    self.w_swap.SetValue("No")
                else:
                    self.w_swap.SetValue("Yes")
                self.w_timeout.SetValue(str(datafile_dict[config_id]["timeout"]))
                self.w_cfg_manufacturer.SetValue(
                    str(datafile_dict[config_id]["sensor_manufacturer"])
                )
                self.w_cfg_model.SetValue(str(datafile_dict[config_id]["sensor_model"]))
                self.w_cfg_desc.SetValue(str(datafile_dict[config_id]["description"]))
                global_instructions_list = datafile_dict[config_id]["global_instructions"]
                sensor_instructions_list = datafile_dict[config_id]["sensor_instructions"]
                self.w_instructions_global.SetValue(self.string_instructions(0))
                self.w_instructions_sensor.SetValue(self.string_instructions(1))
                self.w_sensor_bytes.SetValue(
                    str(SENSOR_INSTRUCTIONS_BUFFER_SIZE_BYTES - self.get_size_instr(1))
                )
                self.w_global_bytes.SetValue(
                    str(GLOBAL_INSTRUCTIONS_BUFFER_SIZE_BYTES - self.get_size_instr(0))
                )
                channels_info_list = datafile_dict[config_id]["channels"]
                total_sensors = len(sensors_list)
                self.w_data_msg_send.SetValue(
                    str(MESSAGE_MAX_SIZE_BYTES - self.get_data_msg_sensor_size_bytes())
                )
                self.w_data_all_msg_send.SetValue(
                    str(
                        MESSAGE_MAX_SIZE_BYTES * MAX_MESSAGES
                        - self.get_data_msg_sensor_size_bytes() * total_sensors
                    )
                )
                max_sensors = int(datafile_dict[config_id]["max_allowed_sensors"])
                self.max_allowed_sensors_check_set_from_cfg(max_sensors)
                self.store_values()
            else:
                self.reset_ui()
                last_file_opened_string = "configs.json"
        else:
            self.reset_ui()
            last_file_opened_string = "configs.json"
            msgb = wx.MessageDialog(self, "File not found", "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()

    # Resets all the UI to an empty values
    #
    # @param event: Nedded to allow the wx library to call this function when the user interacts with the UI
    #
    def new_config(self, event):
        self.reset_ui()

    # Calculates the size of the data that will be sent for a single message and for all messages,
    # if the size exceeds the maximum value admitted
    #
    # @param event: Nedded to allow the wx library to call this function when the user interacts with the UI
    #
    def update_num_of_sensors(self, event):
        try:
            num_sensors = len(self.w_sensors_ids.GetValue().split())
        except:
            msgb = wx.MessageDialog(
                self, "Error parsing the sensors ids", "ERROR", wx.OK | wx.ICON_HAND
            )
            msgb.ShowModal()
            return False

        if (MESSAGE_MAX_SIZE_BYTES * MAX_MESSAGES) < (
            self.get_data_msg_sensor_size_bytes() * num_sensors
        ):
            msgb = wx.MessageDialog(
                self,
                "The number of sensors reach the maximum allowed for the current configuration, "
                "the last ID will be deleted.",
                "ERROR",
                wx.OK | wx.ICON_HAND,
            )
            msgb.ShowModal()
            list_sensors = self.w_sensors_ids.GetValue().split()[:-1]
            self.w_sensors_ids.SetValue(" ".join(list_sensors))
            return

        self.w_data_all_msg_send.SetValue(
            str(
                MESSAGE_MAX_SIZE_BYTES * MAX_MESSAGES
                - (self.get_data_msg_sensor_size_bytes() * num_sensors)
            )
        )

    # Sets the max allowed sensors and its editable checkbox based on the config value
    # if the config value is lower than the max allowed calculated it means that we are manually
    # limiting the max allowed sensors
    #
    # @param max_allowed_sensors_cfg: max allowed sensors read from the config json
    #
    def max_allowed_sensors_check_set_from_cfg(self, max_allowed_sensors_cfg):
        if max_allowed_sensors_cfg < self.get_max_allowed_sensors():
            # if we had a smaller number of max sensors it means that it was manually edited
            self.max_allowed_sensors_check_set(True)
        else:
            max_allowed_sensors_cfg = self.get_max_allowed_sensors()
            self.max_allowed_sensors_check_set(False)
        self.w_max_allowed_sensors.SetValue(str(max_allowed_sensors_cfg))

    # Event call function for w_max_allowed_sensors_check
    #
    def max_allowed_sensors_check_event(self, event):
        if self.w_max_allowed_sensors_check.IsChecked():
            self.w_max_allowed_sensors.SetEditable(True)
            self.w_max_allowed_sensors.Enable()
        else:
            self.w_max_allowed_sensors.SetValue(str(self.get_max_allowed_sensors()))
            self.w_max_allowed_sensors.SetEditable(False)
            self.w_max_allowed_sensors.Disable()

    # Sets the w_max_allowed_sensors_check to a given value
    # It also calls the event, since it is not called automatically
    #
    # @param value: value to be set: True; False
    #
    def max_allowed_sensors_check_set(self, value):
        self.w_max_allowed_sensors_check.SetValue(value)
        self.max_allowed_sensors_check_event(None)

    # This function defines all the fields that are in the UI (Buttons, Dropdowns, Text fields) in order
    # to display all the elements correctly
    #
    def init_ui(self):
        global global_tty

        ########### START CONFIGURATION FIELDS#############
        pnl = wx.Panel(self, -1)
        wx.StaticText(pnl, label="Config ID:", pos=(20, 30))
        self.w_load_config = wx.ComboBox(
            pnl,
            500,
            value=str(self.get_keys()[0]),
            size=(90, 30),
            pos=(20, 55),
            choices=self.get_keys(),
        )
        self.w_load_config.Bind(wx.EVT_COMBOBOX, self.load_config)

        wx.StaticText(pnl, label="Config Version:", pos=(20, 105))
        self.w_cfg_version = wx.TextCtrl(
            pnl, -1, size=(100, 30), pos=(20, 130), style=wx.CB_READONLY
        )

        wx.StaticText(pnl, label="Instruction Version:", pos=(150, 105))
        self.w_instructions_version = wx.TextCtrl(
            pnl, -1, size=(100, 30), pos=(150, 130), style=wx.CB_READONLY
        )

        wx.StaticText(pnl, label="max sensors:", pos=(20, 180))
        self.w_max_allowed_sensors = wx.TextCtrl(
            pnl, -1, size=(70, 30), pos=(20, 205), style=wx.CB_READONLY
        )

        self.w_max_allowed_sensors_check = wx.CheckBox(pnl, -1, pos=(95, 205))
        self.w_max_allowed_sensors_check.Bind(wx.EVT_CHECKBOX, self.max_allowed_sensors_check_event)
        self.max_allowed_sensors_check_set(False)

        wx.StaticText(pnl, label="IDs (addresses):", pos=(20, 255))
        self.w_sensors_ids = wx.TextCtrl(
            pnl, -1, size=(300, 300), pos=(20, 280), style=wx.TE_MULTILINE
        )
        self.Bind(wx.EVT_TEXT, self.update_num_of_sensors, self.w_sensors_ids)

        baud_rate_list = [
            "110",
            "300",
            "600",
            "1200",
            "2400",
            "4800",
            "9600",
            "14400",
            "19200",
            "38400",
            "57600",
            "115200",
            "128000",
            "256000",
        ]
        wx.StaticText(pnl, label="Baud Rate:", pos=(1200, 30))
        self.w_baudrate = wx.ComboBox(
            pnl,
            500,
            value=baud_rate_list[0],
            size=(150, 30),
            pos=(1200, 55),
            choices=baud_rate_list,
        )

        wx.StaticText(pnl, label="Data bits:", pos=(1200, 105))
        self.w_databits = wx.ComboBox(
            pnl,
            500,
            value=DATA_BITS_LIST[0],
            size=(150, 30),
            pos=(1200, 130),
            choices=DATA_BITS_LIST,
            style=wx.CB_READONLY,
        )

        parity_list = list(PARITY_DIC.values())
        wx.StaticText(pnl, label="Parity:", pos=(1400, 30))
        self.w_parity = wx.ComboBox(
            pnl,
            500,
            value=parity_list[0],
            size=(150, 30),
            pos=(1400, 55),
            choices=parity_list,
            style=wx.CB_READONLY,
        )

        stop_bits_list = list(STOP_BITS_DIC.values())
        wx.StaticText(pnl, label="Stop bits:", pos=(1400, 105))
        self.w_stopbits = wx.ComboBox(
            pnl,
            500,
            value=stop_bits_list[1],
            size=(150, 30),
            pos=(1400, 130),
            choices=stop_bits_list,
            style=wx.CB_READONLY,
        )

        word_swap_list = ["Yes", "No"]
        wx.StaticText(pnl, label="Perform Word Swap:", pos=(150, 30))
        self.w_swap = wx.ComboBox(
            pnl,
            500,
            value=word_swap_list[1],
            size=(150, 30),
            pos=(150, 55),
            choices=word_swap_list,
            style=wx.CB_READONLY,
        )

        wx.StaticText(pnl, label="Timeout (ms):", pos=(340, 105))
        self.w_timeout = wx.TextCtrl(pnl, -1, size=(100, 30), pos=(340, 130))

        wx.StaticText(pnl, label="tty USB number:", pos=(340, 30))
        self.w_tty_usb = wx.TextCtrl(pnl, -1, size=(100, 30), pos=(340, 55))
        self.w_tty_usb.SetValue(global_tty)

        wx.StaticText(pnl, label="Instruction:", pos=(530, 160))
        self.w_instruction = wx.ComboBox(
            pnl,
            -1,
            value=self.get_instructions_names()[0],
            size=(150, 30),
            pos=(530, 190),
            choices=self.get_instructions_names(),
            style=wx.CB_READONLY,
        )
        self.Bind(wx.EVT_COMBOBOX, self.edit_args, self.w_instruction)

        wx.StaticText(pnl, label="Arg1:", pos=(700, 160))
        self.w_arg1 = wx.TextCtrl(pnl, -1, size=(100, 30), pos=(700, 190))

        wx.StaticText(pnl, label="Arg2:", pos=(850, 160))
        self.w_arg2 = wx.TextCtrl(pnl, -1, size=(100, 30), pos=(850, 190))

        wx.StaticText(pnl, label="Arg3:", pos=(1000, 160))
        self.w_arg3 = wx.TextCtrl(pnl, -1, size=(100, 30), pos=(1000, 190))

        wx.StaticText(pnl, label="Arg4:", pos=(1150, 160))
        self.w_arg4 = wx.TextCtrl(pnl, -1, size=(100, 30), pos=(1150, 190))

        wx.StaticText(pnl, label="Channel label:", pos=(1460, 230))
        self.w_label = wx.TextCtrl(pnl, -1, size=(100, 30), pos=(1610, 225))

        wx.StaticText(pnl, label="Data units:", pos=(1460, 275))
        self.w_data_units = wx.TextCtrl(pnl, -1, size=(100, 30), pos=(1610, 275))

        signed_value_list = ["Yes", "No"]
        wx.StaticText(pnl, label="Signed value:", pos=(1460, 320))
        self.w_signed_value = wx.ComboBox(
            pnl,
            500,
            value=signed_value_list[1],
            size=(100, 30),
            pos=(1610, 320),
            choices=signed_value_list,
            style=wx.CB_READONLY,
        )

        check_out_of_range_list = ["Yes", "No"]
        wx.StaticText(pnl, label="check out of range:", pos=(1460, 365))
        self.w_check_out_of_range = wx.ComboBox(
            pnl,
            500,
            value=check_out_of_range_list[1],
            size=(100, 30),
            pos=(1610, 365),
            choices=check_out_of_range_list,
            style=wx.CB_READONLY,
        )

        self.w_add_instr_glb_btn = wx.Button(pnl, size=(120, 30), label="Add instr", pos=(350, 255))
        self.Bind(wx.EVT_BUTTON, self.add_glb_instr, self.w_add_instr_glb_btn)

        self.w_add_instr_glb_index = wx.TextCtrl(pnl, -1, size=(35, 30), pos=(475, 255))

        self.w_add_instr_sns_btn = wx.Button(pnl, size=(120, 30), label="Add instr", pos=(910, 255))
        self.Bind(wx.EVT_BUTTON, self.add_sensor_instr, self.w_add_instr_sns_btn)

        self.w_add_instr_sns_index = wx.TextCtrl(pnl, -1, size=(35, 30), pos=(1035, 255))

        self.w_del_instr_glb_btn = wx.Button(pnl, size=(120, 30), label="Del instr", pos=(350, 500))
        self.Bind(wx.EVT_BUTTON, lambda event: self.del_instr(event, 0), self.w_del_instr_glb_btn)

        self.w_del_instr_glb_index = wx.TextCtrl(pnl, -1, size=(35, 30), pos=(475, 500))

        self.w_del_instr_sns_btn = wx.Button(pnl, size=(120, 30), label="Del instr", pos=(910, 500))
        self.Bind(wx.EVT_BUTTON, lambda event: self.del_instr(event, 1), self.w_del_instr_sns_btn)

        self.w_del_instr_sns_index = wx.TextCtrl(pnl, -1, size=(35, 30), pos=(1035, 500))

        ########### END CONFIGURATION FIELDS#############

        ########### START INFORMATION FIELDS#############
        wx.StaticText(pnl, label="Sensor Manufacturer:", pos=(530, 30))
        self.w_cfg_manufacturer = wx.TextCtrl(pnl, -1, size=(440, 25), pos=(710, 30))
        self.w_cfg_manufacturer.WriteText("")

        wx.StaticText(pnl, label="Sensor Model:", pos=(530, 70))
        self.w_cfg_model = wx.TextCtrl(pnl, -1, size=(440, 25), pos=(710, 70))
        self.w_cfg_model.WriteText("")

        wx.StaticText(pnl, label="Description:", pos=(530, 110))
        self.w_cfg_desc = wx.TextCtrl(pnl, -1, size=(440, 25), pos=(710, 110))
        self.w_cfg_desc.WriteText("")

        wx.StaticText(pnl, label="Global Instructions:", pos=(355, 230))
        self.w_instructions_global = wx.TextCtrl(
            pnl, -1, size=(360, 300), pos=(530, 230), style=wx.TE_MULTILINE | wx.TE_READONLY
        )
        self.w_instructions_global.SetBackgroundColour(wx.Colour(230, 230, 230))
        self.w_instructions_global.WriteText("")

        wx.StaticText(pnl, label="Sensor Instructions:", pos=(910, 230))
        self.w_instructions_sensor = wx.TextCtrl(
            pnl, -1, size=(360, 300), pos=(1085, 230), style=wx.TE_MULTILINE | wx.TE_READONLY
        )
        self.w_instructions_sensor.SetBackgroundColour(wx.Colour(230, 230, 230))
        self.w_instructions_sensor.WriteText("")

        wx.StaticText(pnl, label="Remaining Bytes:", pos=(355, 290))
        self.w_global_bytes = wx.TextCtrl(
            pnl, -1, size=(55, 30), pos=(445, 315), style=wx.TE_READONLY
        )
        self.w_global_bytes.SetBackgroundColour(wx.Colour(230, 230, 230))
        self.w_global_bytes.WriteText(str(GLOBAL_INSTRUCTIONS_BUFFER_SIZE_BYTES))

        wx.StaticText(pnl, label="Remaining Bytes:", pos=(905, 290))
        self.w_sensor_bytes = wx.TextCtrl(
            pnl, -1, size=(60, 30), pos=(1010, 315), style=wx.TE_READONLY
        )
        self.w_sensor_bytes.SetBackgroundColour(wx.Colour(230, 230, 230))
        self.w_sensor_bytes.WriteText(str(SENSOR_INSTRUCTIONS_BUFFER_SIZE_BYTES))

        wx.StaticText(pnl, label="Remaining bytes for data per message:", pos=(1370, 620))
        self.w_data_msg_send = wx.TextCtrl(
            pnl, -1, size=(55, 30), pos=(1370, 645), style=wx.TE_READONLY
        )
        self.w_data_msg_send.SetBackgroundColour(wx.Colour(230, 230, 230))
        self.w_data_msg_send.WriteText(str(MESSAGE_MAX_SIZE_BYTES))

        wx.StaticText(
            pnl,
            label="Remaining bytes for data per all " + str(MAX_MESSAGES) + " messages:",
            pos=(1370, 675),
        )
        self.w_data_all_msg_send = wx.TextCtrl(
            pnl, -1, size=(60, 30), pos=(1370, 700), style=wx.TE_READONLY
        )
        self.w_data_all_msg_send.SetBackgroundColour(wx.Colour(230, 230, 230))
        self.w_data_all_msg_send.WriteText(str(MAX_MESSAGES * MESSAGE_MAX_SIZE_BYTES))

        ########### END INFORMATION FIELDS#############

        ########### START ACTION BUTTONS ###########
        self.w_import_cfg = wx.Button(pnl, label="Import Config", size=(150, 45), pos=(230, 590))
        self.Bind(wx.EVT_BUTTON, self.on_open, self.w_import_cfg)

        self.w_set_config_btn = wx.Button(pnl, size=(150, 45), label="Set Config", pos=(400, 590))
        self.Bind(wx.EVT_BUTTON, self.set_config, self.w_set_config_btn)

        self.w_set_config_btn = wx.Button(
            pnl, size=(150, 45), label="Request Config", pos=(570, 590)
        )
        self.Bind(wx.EVT_BUTTON, self.request_config, self.w_set_config_btn)

        self.w_set_config_btn = wx.Button(pnl, size=(150, 45), label="Save Config", pos=(740, 590))
        self.Bind(wx.EVT_BUTTON, self.save_config, self.w_set_config_btn)

        self.w_del_config_btn = wx.Button(
            pnl, size=(150, 45), label="Delete Config", pos=(910, 590)
        )
        self.Bind(wx.EVT_BUTTON, self.delete_config, self.w_del_config_btn)

        self.w_new_config_btn = wx.Button(pnl, size=(150, 45), label="New Config", pos=(1080, 590))
        self.Bind(wx.EVT_BUTTON, self.new_config, self.w_new_config_btn)

        ########### END ACTION BUTTONS ###########

        self.SetSize((1800, 800))
        self.SetTitle("DigGenericModbusCfg")
        self.Centre()
        self.Show(True)
        self.load_config(None)
        self.edit_args(None)
        self.w_add_instr_glb_index.SetValue(str(len(global_instructions_list) + 1))
        self.w_add_instr_sns_index.SetValue(str(len(sensor_instructions_list) + 1))
        self.w_del_instr_glb_index.SetValue(str(len(global_instructions_list)))
        self.w_del_instr_sns_index.SetValue(str(len(sensor_instructions_list)))


def main():
    global global_tty

    if len(sys.argv) == 2 and TTY_PREFIX in sys.argv[1]:
        tty = sys.argv[1]
        global_tty = tty[tty.index(TTY_PREFIX) + len(TTY_PREFIX) :]
    else:
        global_tty = "0"

    ex = wx.App()
    DigGenericModbusCfg(None)
    ex.MainLoop()


if __name__ == "__main__":
    main()
