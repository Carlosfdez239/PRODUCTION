#!/usr/bin/env python3
import os
import struct
import sys

import wx
from ls_utils import ls_send_message_uart

global_tty = ""


class Example(wx.Frame):
    def __init__(self, *args, **kw):
        super(Example, self).__init__(*args, **kw)

        self.init_ui()

    def init_ui(self):
        global global_tty

        def load_config(event):

            config = w_load_config.GetValue()

            if config == "LS-G6-VW-1-SA":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("50")
                w_serial_number.SetValue("50")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-VW-5-SA":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("51")
                w_serial_number.SetValue("51")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-VW-1-FCC":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("52")
                w_serial_number.SetValue("52")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-VW-5-FCC":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("53")
                w_serial_number.SetValue("53")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-VW-1-EU":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("54")
                w_serial_number.SetValue("54")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-VW-5-EU":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("55")
                w_serial_number.SetValue("55")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-DIG-1-SA":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("60")
                w_serial_number.SetValue("60")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-DIG-2-SA":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("61")
                w_serial_number.SetValue("61")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-DIG-1-FCC":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("62")
                w_serial_number.SetValue("62")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-DIG-2-FCC":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("63")
                w_serial_number.SetValue("63")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-DIG-1-EU":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("64")
                w_serial_number.SetValue("64")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-DIG-2-EU":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("65")
                w_serial_number.SetValue("65")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-VOLT-4-SA":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("70")
                w_serial_number.SetValue("70")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-VOLT-4-EU":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("71")
                w_serial_number.SetValue("71")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-VOLT-4-FCC":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("72")
                w_serial_number.SetValue("72")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-INC15":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("73")
                w_serial_number.SetValue("73")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-INC15_1":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("74")
                w_serial_number.SetValue("74")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-PICO":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("75")
                w_serial_number.SetValue("75")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)
            elif config == "LS-G6-LASER":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("76")
                w_serial_number.SetValue("76")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)
            elif config == "LS-G6-TIL90-X":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("77")
                w_serial_number.SetValue("77")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)
            elif config == "LS-G6-TIL90-I":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("78")
                w_serial_number.SetValue("78")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)
            elif config == "LS-G6-LAS-TIL90":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("79")
                w_serial_number.SetValue("79")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-TIL90-XE":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("80")
                w_serial_number.SetValue("80")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-TIL90-IE":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("81")
                w_serial_number.SetValue("81")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LS-G6-VW-RCR":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("82")
                w_serial_number.SetValue("82")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LSG7ACL-BILH-VIB":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("86")
                w_serial_number.SetValue("86")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LSG7ACL-BILH-TIL":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("87")
                w_serial_number.SetValue("87")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LSG7ACL-BILR-TIL":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("88")
                w_serial_number.SetValue("88")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LSG7-GNSS":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("89")
                w_serial_number.SetValue("89")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LSG7-6VW-IL":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("90")
                w_serial_number.SetValue("90")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LSG7-6VW-XL":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("91")
                w_serial_number.SetValue("91")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LSG7-2VW-XL":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("92")
                w_serial_number.SetValue("92")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LSG7-BXLH-VIB":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("93")
                w_serial_number.SetValue("93")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LSG7-BXLH-TIL":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("94")
                w_serial_number.SetValue("94")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LSG7-2VW-IL":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("95")
                w_serial_number.SetValue("95")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LSG7-1VW-XL":
                w_password.SetValue("545611284")
                w_pr_code.SetValue("96")
                w_serial_number.SetValue("96")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        def get_input():
            try:
                password = int(w_password.GetValue())
                version = 0
                product_code = int(w_pr_code.GetValue())
                serial_number = int(w_serial_number.GetValue())
            except Exception:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return [None] * 4
            return password, version, product_code, serial_number

        def send_msg(byte_values):
            output = "".join(["\\x{:02X}".format(e) for e in byte_values])
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(output, tty_usb, self)

        # method to set the config
        def set_config_v1(event):
            password, version, product_code, serial_number = get_input()
            if password is None:
                return

            byte_values = [0x6]
            byte_values += list(struct.pack(">I", int(password)))
            byte_values += [product_code]
            byte_values += list(struct.pack(">H", serial_number))
            send_msg(byte_values)

        def set_config_v2(event):
            password, version, product_code, serial_number = get_input()
            if password is None:
                return

            byte_values = [0x13]
            byte_values += list(struct.pack(">I", int(password)))
            byte_values += [version << 6]
            byte_values += [product_code]
            byte_values += list(struct.pack(">I", serial_number))
            send_msg(byte_values)

        def get_node_info(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x43\\x69\\x00\\x00", tty_usb, self)

        def set_custom_config(event):
            w_load_config.SetStringSelection("Custom")

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Password", pos=(115, vertical_pos + 6))
        w_password = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_password.SetMaxLength(10)
        w_password.WriteText("1800")
        w_password.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Product Code", pos=(115, vertical_pos + 6))
        w_pr_code = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_pr_code.SetMaxLength(10)
        w_pr_code.WriteText("1800")
        w_pr_code.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Serial Number", pos=(115, vertical_pos + 6))
        w_serial_number = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_serial_number.SetMaxLength(10)
        w_serial_number.WriteText("1800")
        w_serial_number.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment + 10

        w_set_config_btn = wx.Button(pnl, label="Set Config SN<65k", pos=(20, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config_v1)

        w_set_config_btn = wx.Button(pnl, label="Set Config SN>65k", pos=(190, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config_v2)

        w_set_config_btn = wx.Button(pnl, label="Get Node Info", pos=(360, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, get_node_info)
        vertical_pos += vertical_pos_increment

        configs_list = [
            "Custom",
            "LS-G6-VW-1-SA",
            "LS-G6-VW-5-SA",
            "LS-G6-VW-1-FCC",
            "LS-G6-VW-5-FCC",
            "LS-G6-VW-1-EU",
            "LS-G6-VW-5-EU",
            "LS-G6-DIG-1-SA",
            "LS-G6-DIG-2-SA",
            "LS-G6-DIG-1-FCC",
            "LS-G6-DIG-2-FCC",
            "LS-G6-DIG-1-EU",
            "LS-G6-DIG-2-EU",
            "LS-G6-VOLT-4-SA",
            "LS-G6-VOLT-4-EU",
            "LS-G6-VOLT-4-FCC",
            "LS-G6-INC15",
            "LS-G6-INC15_1",
            "LS-G6-PICO",
            "LS-G6-LASER",
            "LS-G6-TIL90-X",
            "LS-G6-TIL90-I",
            "LS-G6-LAS-TIL90",
            "LS-G6-TIL90-XE",
            "LS-G6-TIL90-IE",
            "LS-G6-VW-RCR",
            "LSG7ACL-BILH-VIB",
            "LSG7ACL-BILH-TIL",
            "LSG7ACL-BILR-TIL",
            "LSG7-GNSS",
            "LSG7-6VW-IL",
            "LSG7-6VW-XL",
            "LSG7-2VW-XL",
            "LSG7-BXLH-VIB",
            "LSG7-BXLH-TIL",
            "LSG7-2VW-IL",
            "LSG7-1VW-XL",
        ]

        wx.StaticText(pnl, label="Load preset configs", pos=(250, 16))
        w_load_config = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(250, 10 + vertical_pos_increment),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_load_config.Bind(wx.EVT_COMBOBOX, load_config)
        w_load_config.SetStringSelection("LS-G6-VW-1-SA")
        load_config(0)

        self.SetSize((500, vertical_pos + vertical_pos_increment + 20))
        self.SetTitle("SetPrcodeSn")
        self.Centre()
        self.Show(True)


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
    Example(None)
    ex.MainLoop()


if __name__ == "__main__":
    main()
