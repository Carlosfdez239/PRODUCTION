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

            if config == "v0.0 - v0.0":
                w_version.SetValue("0")
                w_password.SetValue("2894317262")
                w_brd1_major.SetValue("0")
                w_brd1_minor.SetValue("0")
                w_brd2_major.SetValue("0")
                w_brd2_minor.SetValue("0")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Tilt v2.0 - v4.0":
                w_version.SetValue("0")
                w_password.SetValue("2894317262")
                w_brd1_major.SetValue("2")
                w_brd1_minor.SetValue("0")
                w_brd2_major.SetValue("4")
                w_brd2_minor.SetValue("0")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "VW v2.77":
                w_version.SetValue("0")
                w_password.SetValue("2894317262")
                w_brd1_major.SetValue("2")
                w_brd1_minor.SetValue("77")
                w_brd2_major.SetValue("0")
                w_brd2_minor.SetValue("0")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        def packed_string_to_hexa(
            s,
        ):  # translates message from binary to the format expected by ls_send_message_uart
            encoded_s = s.hex()
            return "\\x" + "\\x".join(a + b for a, b in zip(encoded_s[::2], encoded_s[1::2]))

        # method to set the config
        def set_config(event):
            try:
                version = int(w_version.GetValue())
                password = int(w_password.GetValue())
                brd1_major = int(w_brd1_major.GetValue())
                brd1_minor = int(w_brd1_minor.GetValue())
                brd2_major = int(w_brd2_major.GetValue())
                brd2_minor = int(w_brd2_minor.GetValue())

            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            output = struct.pack(
                "!BBIBBBB", 13, version, password, brd1_major, brd1_minor, brd2_major, brd2_minor
            )
            hex_output = packed_string_to_hexa(output)
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(hex_output, tty_usb, self)

        def get_extended_node_info(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x0E", tty_usb, self)

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

        wx.StaticText(pnl, label="Version", pos=(115, vertical_pos + 6))
        w_version = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_version.SetMaxLength(3)
        w_version.WriteText("0")
        w_version.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Password", pos=(115, vertical_pos + 6))
        w_password = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_password.SetMaxLength(10)
        w_password.WriteText("2894317262")
        w_password.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Board 1 Major", pos=(115, vertical_pos + 6))
        w_brd1_major = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_brd1_major.SetMaxLength(10)
        w_brd1_major.WriteText("0")
        w_brd1_major.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Board 1 Minor", pos=(115, vertical_pos + 6))
        w_brd1_minor = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_brd1_minor.SetMaxLength(10)
        w_brd1_minor.WriteText("0")
        w_brd1_minor.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Board 2 Major", pos=(115, vertical_pos + 6))
        w_brd2_major = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_brd2_major.SetMaxLength(10)
        w_brd2_major.WriteText("0")
        w_brd2_major.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Board 2 Minor", pos=(115, vertical_pos + 6))
        w_brd2_minor = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_brd2_minor.SetMaxLength(10)
        w_brd2_minor.WriteText("0")
        w_brd2_minor.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_set_config_btn = wx.Button(pnl, label="Set HW version", pos=(200, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        w_set_config_btn = wx.Button(pnl, label="Get Ext. Node Info", pos=(320, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, get_extended_node_info)

        configs_list = ["Custom", "v0.0 - v0.0", "Tilt v2.0 - v4.0", "VW v2.77"]

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
        w_load_config.SetStringSelection("v0.0 - v0.0")
        load_config(0)
        vertical_pos = vertical_pos + vertical_pos_increment

        self.SetSize((470, vertical_pos + vertical_pos_increment))
        self.SetTitle("SetHWVersion")
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
