#!/usr/bin/env python3
import os
import struct
import subprocess
import sys
import threading
import time
from collections import OrderedDict
from pathlib import Path

import bitstring
import wx
import wx.lib.newevent
from ls_utils import ls_send_message_uart

FCC_MAC_VERSIONS = [2, 3, 6]

MIN_SF = 7
MAX_SF_FCC = 9
MAX_SF_NO_FCC = 11

MAX_SF_ALLOWED = 12

NUM_ITERATIONS = 5
MAX_DB = 30

START_SERIAL_MSG_STRING = " 40 "

REQUEST_RADIO_GENERAL_CFG_CMD = "\\x00\\x84"
LORA_LINK_CHECK_CMD = "\\x11"

MIN_TX_POWER = 2
MAX_TX_POWER = 20

COVERAGE_RESULTS_DICT = OrderedDict(  # TODO: To be tested and adjusted
    [
        ["NO SIGNAL", [0]],
        ["BAD", [0, 0.25]],
        ["POOR", [0.26, 0.50]],
        ["FAIR", [0.51, 0.75]],
        ["GOOD", [0.76, 1]],
    ]
)


class LinkCoverageTestThread(threading.Thread):
    def __init__(
        self,
        fw_update_status_wx,
        fw_update_results_wx,
        add_status_info,
        add_results_info,
        tty_usb,
        change_tx_power,
        tx_power,
        allow_high_sf,
    ):
        threading.Thread.__init__(self)
        self.fw_update_status_wx = fw_update_status_wx
        self.fw_update_results_wx = fw_update_results_wx
        self.add_status_info = add_status_info
        self.add_results_info = add_results_info
        self.tty_usb = tty_usb
        self.tx_power = tx_power
        self.change_tx_power = change_tx_power
        self.allow_high_sf = allow_high_sf

    def run(self):
        self.run_coverage_test()

    def write_coverage_info(self, info_string):
        self.add_status_info(info_string)

    def write_coverage_results(self, info_string):
        self.add_results_info(info_string)

    def treat_tx_power(self):
        try:
            value = int(self.tx_power)
        except:
            self.add_status_info("ERROR: Tx Power is not a number\n")
            return None

        if value >= MIN_TX_POWER and value <= MAX_TX_POWER:
            return value
        else:
            self.add_status_info(
                "ERROR: Tx power outside the range [{}, {}]\n".format(MIN_TX_POWER, MAX_TX_POWER)
            )
            return None

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

    def get_response_from_command(self, command_to_send):
        path = Path(os.path.dirname(os.path.abspath(__file__)))
        path = path.parent
        my_file = os.path.join(str(path), "ls_serial_view.py")
        arguments = [str(my_file), str(self.tty_usb)]

        p = subprocess.Popen(
            arguments,
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        timer = threading.Timer(15, p.terminate)
        time.sleep(0.1)
        ls_send_message_uart(command_to_send, self.tty_usb, self)
        timer.start()
        response = ""
        for stdout_line in iter(p.stdout.readline, ""):
            if START_SERIAL_MSG_STRING in stdout_line:
                response = stdout_line
                break
        p.stdout.close()
        p.terminate()
        timer.cancel()
        return response[response.find(START_SERIAL_MSG_STRING) + 1 :].split()[5:]

    def request_radio_general_config(self):
        self.add_status_info("Requesting radio general configuration...\n")

        response = self.get_response_from_command(REQUEST_RADIO_GENERAL_CFG_CMD)

        if len(response) == 0:
            self.write_coverage_info(
                "ERROR: The node is not responding or you have the serial view opened.\n"
            )
            return None

        if response[0] != "84":
            self.write_coverage_info("ERROR: Wrong response message.\n")
            return None

        if self.extract_bits_from_array(chr(int(response[2], 16)), 1, 1) == 0:
            self.write_coverage_info("ERROR: Radio not enabled.\n")
            return None

        return response

    def get_max_sf(self, radio_general_cfg):
        offset_bits = 4  # skip msg version
        mac_version = self.extract_bits_from_array(
            chr(int(radio_general_cfg[1], 16)), offset_bits, 4
        )
        max_sf_to_test = MAX_SF_FCC if mac_version in FCC_MAC_VERSIONS else MAX_SF_NO_FCC
        self.add_status_info("MAC Version is: {}\n".format(mac_version))

        return max_sf_to_test

    def generate_radio_general_cfg(self, radio_general_cfg, spreading_factor):
        misc_fields_sf_tx_pow = bitstring.BitArray()
        misc_fields_sf_tx_pow.append(
            bitstring.pack(
                "uint:3, uint:1, uint:4",
                self.extract_bits_from_array(chr(int(radio_general_cfg[2], 16)), 0, 3),
                0,
                spreading_factor,
            )
        )
        if self.change_tx_power != 0:
            misc_fields_sf_tx_pow.append(bitstring.pack("uint:8", self.tx_power))

        cfg = "".join(["%0.2X" % ord(chr(int(s, 16))) for s in radio_general_cfg[:2]])
        cfg += "".join(["%0.2X" % ord(e) for e in misc_fields_sf_tx_pow.tobytes()])
        cfg += "".join(
            [
                "%0.2X" % ord(chr(int(s, 16)))
                for s in radio_general_cfg[4 if self.change_tx_power else 3 :]
            ]
        )
        cfg = "\\x" + "\\x".join(a + b for a, b in zip(cfg[::2], cfg[1::2]))

        return cfg

    def send_radio_general_cfg(self, configuration):

        response = self.get_response_from_command(configuration)

        if len(response) == 0:
            self.write_coverage_info(
                "ERROR: The node is not responding or you have the serial view opened.\n"
            )
            return False

        if response[0] != "00":
            self.write_coverage_info("ERROR: Wrong response message.\n")
            return False

        for s in response[1:]:
            if s != "00":
                self.write_coverage_info("ERROR: Configuration not accepted by the node.\n")
                return False

        return True

    def calculate_coverage_test_label(self, link_health_value):
        for label, range in list(COVERAGE_RESULTS_DICT.items()):
            if len(range) == 1:
                if link_health_value == range[0]:
                    return label
            elif link_health_value >= range[0] and link_health_value <= range[1]:
                return label
        return "N/A"

    def is_link_health_enough(self, link_health_value):
        return list(COVERAGE_RESULTS_DICT.keys())[-1] == self.calculate_coverage_test_label(
            link_health_value
        )

    def run_coverage_test(self):
        try:
            results_dict = {}
            self.fw_update_status_wx.SetValue("")
            self.fw_update_results_wx.SetValue("")

            if not self.change_tx_power:
                self.add_status_info("Tx Power not set, using the one in the lora general cfg\n")
            else:
                self.tx_power = self.treat_tx_power()

            radio_general_cfg = self.request_radio_general_config()
            if radio_general_cfg is None:
                return

            max_sf_to_test = (
                MAX_SF_ALLOWED if self.allow_high_sf else self.get_max_sf(radio_general_cfg)
            )

            self.add_status_info("Maximum SF to test:{}\n".format(max_sf_to_test))

            spreading_factor = MIN_SF

            while spreading_factor <= max_sf_to_test:

                results_dict[spreading_factor] = {}
                results_dict[spreading_factor]["db_margin"] = []
                results_dict[spreading_factor]["replies"] = 0

                new_configuration = self.generate_radio_general_cfg(
                    radio_general_cfg, spreading_factor
                )
                if not self.send_radio_general_cfg(new_configuration):
                    break
                time.sleep(8)
                """
                    Setting a general cfg with a legacy mac resets de frame counter.The frame counter is considered
                    rolloved by the loraserver and checks with a greater 16-bit upper part of the 32 bits used for the
                    frame counter (65536), but the actual frame counter is 0, so the check fails and the packet is
                    dropped.
                    In order to the loraserver to accept the packet, a delay has to be done after setting the lora
                    general cfg.
                    The loraserver requires 10 seconds to check with more sequence numbers (it could be after a reset),
                    then checks with an upper part of the frame counter set to 0 and the first packet after a
                    lora general cfg is accepted.
                """

                self.write_coverage_info("Configuration for SF {} set\n".format(spreading_factor))

                for iteration in range(0, NUM_ITERATIONS):
                    response = self.get_response_from_command(LORA_LINK_CHECK_CMD)

                    if len(response) != 0:
                        results_dict[spreading_factor]["db_margin"].append(int(response[1], 16))
                        results_dict[spreading_factor]["replies"] += 1

                        self.add_status_info(
                            "Iteration {}, link margin :{} dB\n".format(
                                iteration + 1, int(response[1], 16)
                            )
                        )

                    else:
                        self.add_status_info("Iteration {}, no reply\n".format(iteration + 1))

                try:
                    average_db_margin = (
                        float(sum(results_dict[spreading_factor]["db_margin"]))
                        / results_dict[spreading_factor]["replies"]
                    )
                except ZeroDivisionError:
                    average_db_margin = 0
                results_dict[spreading_factor]["link_health"] = (
                    float(results_dict[spreading_factor]["replies"]) / NUM_ITERATIONS
                ) * 0.75 + min(float(average_db_margin) / MAX_DB, 1) * 0.25

                if spreading_factor == max_sf_to_test:
                    self.add_results_info(
                        "RESULT FOR SF {} IS {:.3f} ({:.1f} %) - {}\n".format(
                            spreading_factor,
                            results_dict[spreading_factor]["link_health"],
                            (results_dict[spreading_factor]["link_health"] * 100),
                            self.calculate_coverage_test_label(
                                results_dict[spreading_factor]["link_health"]
                            ),
                        )
                    )

                else:
                    self.add_results_info(
                        "RESULT FOR SF {} IS {:.3f} ({:.1f} %)\n".format(
                            spreading_factor,
                            results_dict[spreading_factor]["link_health"],
                            (results_dict[spreading_factor]["link_health"] * 100),
                        )
                    )

                if (
                    self.is_link_health_enough(results_dict[spreading_factor]["link_health"])
                    and not self.allow_high_sf
                ):
                    self.add_results_info(
                        "COVERAGE TEST IS {}\n".format(list(COVERAGE_RESULTS_DICT.keys())[-1])
                    )
                    break

                spreading_factor += 1

            self.add_results_info("END LINKCHECK COVERAGE\n")

            self.add_status_info("Restoring original radio configuration...\n")

            if self.send_radio_general_cfg("\\x" + "\\x".join(a + b for a, b in radio_general_cfg)):
                self.write_coverage_info("Original configuration set\n")

        except Exception as e:
            print(e)
            self.write_coverage_info("ERROR: exception rised\n")


class LinkCheckCoverageTest(wx.Frame):

    coverage_test_thread = None

    def __init__(self, *args, **kw):
        super(LinkCheckCoverageTest, self).__init__(*args, **kw)

        self.init_ui()

    def init_ui(self):
        global global_tty

        y_initial_pos = 20
        x_initial_pos = 20
        y_pos = y_initial_pos
        x_pos = x_initial_pos
        y_pos_increment = 35
        x_pos_increment = 70

        coverage_status_x_size = 300
        coverage_status_y_size = 500

        coverage_result_x_size = 300
        coverage_result_y_size = 300

        tty_usb_panel_x_size = 90
        tty_usb_panel_y_size = 30

        tty_usb_label_x_size = 120

        coverage_label = 150

        link_check_cov_button_x_size = 250
        link_check_cov_button_y_size = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="Coverage Status:", pos=(x_pos, y_pos))
        y_pos += y_pos_increment

        self.w_coverage_status = wx.TextCtrl(
            pnl,
            -1,
            size=(coverage_status_x_size, coverage_status_y_size),
            pos=(x_pos, y_pos),
            style=wx.TE_MULTILINE | wx.TE_READONLY,
        )
        self.w_coverage_status.SetBackgroundColour(wx.Colour(100, 100, 100))
        self.w_coverage_status.SetValue("")

        x_pos += coverage_status_x_size + x_pos_increment
        y_size_col_1 = y_pos + y_pos_increment + coverage_status_y_size + y_initial_pos
        y_pos = 20

        wx.StaticText(pnl, label="Coverage Result:", pos=(x_pos, y_pos))
        y_pos += y_pos_increment

        self.w_coverage_result = wx.TextCtrl(
            pnl,
            -1,
            size=(coverage_result_x_size, coverage_result_y_size),
            pos=(x_pos, y_pos),
            style=wx.TE_MULTILINE | wx.TE_READONLY,
        )
        self.w_coverage_result.SetBackgroundColour(wx.Colour(100, 100, 100))
        self.w_coverage_result.SetValue("")

        y_pos += coverage_result_y_size + y_pos_increment

        wx.StaticText(pnl, label="ttyUSB Number", pos=(x_pos, y_pos))
        self.w_tty_usb = wx.TextCtrl(
            pnl,
            -1,
            size=(tty_usb_panel_x_size, tty_usb_panel_y_size),
            pos=(x_pos + tty_usb_label_x_size, y_pos - 5),
        )
        self.w_tty_usb.SetMaxLength(10)
        self.w_tty_usb.WriteText("0")

        y_pos += y_pos_increment

        wx.StaticText(pnl, label="Change Tx Power", pos=(x_pos, y_pos))
        self.w_change_tx_power = wx.CheckBox(pnl, pos=(x_pos + coverage_label, y_pos))
        self.Bind(wx.EVT_CHECKBOX, self.toggle_tx_power_field, self.w_change_tx_power)

        self.w_tx_power = wx.TextCtrl(
            pnl,
            -1,
            size=(tty_usb_panel_x_size, tty_usb_panel_y_size),
            pos=(x_pos + tty_usb_label_x_size + 30, y_pos - 5),
        )
        self.w_tx_power.SetMaxLength(2)
        self.w_tx_power.WriteText("")
        self.w_tx_power.Hide()

        y_pos += y_pos_increment

        wx.StaticText(pnl, label="Don't stop coverage\ntest until SF12", pos=(x_pos, y_pos))
        self.w_high_sf_check = wx.CheckBox(pnl, pos=(x_pos + coverage_label, y_pos))

        y_pos += y_pos_increment + 10

        self.w_start_coverage = wx.Button(
            pnl,
            label="Start Link Check Coverage Test",
            size=(link_check_cov_button_x_size, link_check_cov_button_y_size),
            pos=(x_pos, y_pos),
        )
        self.Bind(wx.EVT_BUTTON, self.coverage_test)

        y_size_col_2 = y_pos + y_pos_increment
        x_pos += coverage_result_x_size + x_initial_pos

        self.SetSize((x_pos, max(y_size_col_1, y_size_col_2)))
        self.SetTitle("LinkCheckCoverageTest")
        self.Centre()
        self.Show(True)

        self.Event1, self.NEW_EVENT = wx.lib.newevent.NewEvent()
        self.CommandEvent, self.NEW_COMMAND_EVENT = wx.lib.newevent.NewCommandEvent()
        self.Bind(self.NEW_EVENT, self.coverage_status_handler)

        self.Event2, self.NEW_EVENT = wx.lib.newevent.NewEvent()
        self.CommandEvent, self.NEW_COMMAND_EVENT = wx.lib.newevent.NewCommandEvent()
        self.Bind(self.NEW_EVENT, self.coverage_results_handler)

    def coverage_status_handler(self, event):
        self.w_coverage_status.WriteText(event.attr1)

    def coverage_results_handler(self, event):
        self.w_coverage_result.WriteText(event.attr1)

    def add_coverages_status_text(self, string_text):
        evt = self.Event1(attr1=string_text)
        wx.PostEvent(self, evt)

    def add_coverage_results_text(self, string_text):
        evt = self.Event2(attr1=string_text)
        wx.PostEvent(self, evt)

    def toggle_tx_power_field(self, event):
        if self.w_change_tx_power.GetValue():
            self.w_tx_power.Show()
        else:
            self.w_tx_power.Hide()

    def coverage_test(self, event):
        if not self.coverage_test_thread or not self.coverage_test_thread.is_alive():
            self.w_start_coverage.Disable()
            self.w_change_tx_power.Disable()
            self.w_tx_power.Disable()
            tty_usb = "/dev/ttyUSB" + self.w_tty_usb.GetValue()
            self.coverage_test_thread = LinkCoverageTestThread(
                self.w_coverage_status,
                self.w_coverage_result,
                self.add_coverages_status_text,
                self.add_coverage_results_text,
                tty_usb,
                self.w_change_tx_power.GetValue(),
                self.w_tx_power.GetValue(),
                self.w_high_sf_check.GetValue(),
            )
            self.coverage_test_thread.daemon = True
            self.coverage_test_thread.start()
            self.w_start_coverage.Enable()
            self.w_change_tx_power.Enable()
            self.w_tx_power.Enable()


def main():
    global use_socket
    global server_ip
    global global_tty
    if len(sys.argv) == 2 and "/dev/" in sys.argv[1]:
        global_tty = sys.argv[1]
    elif len(sys.argv) == 4:
        global_tty = sys.argv[1]
        use_socket = True
        server_ip = sys.argv[3]
    elif len(sys.argv) == 1:
        global_tty = "/dev/ttyUSB0"  # Use default tty
    else:
        print("Usage" + os.path.basename(__file__) + " [serial_tty] [-s IP]")
        sys.exit(1)

    ex = wx.App()
    LinkCheckCoverageTest(None)
    ex.MainLoop()


if __name__ == "__main__":
    main()
