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
        self.initializing = False
        self.init_ui()

    def init_ui(self):
        global global_tty

        def load_config(event):
            config = w_load_config.GetValue()
            if config == "Default":
                self.initializing = True
                w_diag_freq.SetValue("200")
                w_msg_version.SetValue("0")
                w_node_type.SetValue("0")
                w_cmd_code.SetValue("0")
                self.initializing = False

        def request_config(event):
            try:
                diag_freq = int(w_diag_freq.GetValue())
                if diag_freq < 150 or diag_freq > 400:
                    wx.MessageBox(
                        "Diagnostic frequency range must be between 150 and 400, Message will be sent upon clicking OK",
                        "ERROR",
                        wx.OK | wx.ICON_HAND,
                    )
            except ValueError:
                wx.MessageBox(
                    "Diagnostic frequency must be an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                return

            try:
                msg_version = int(w_msg_version.GetValue())
                node_type = int(w_node_type.GetValue())
                cmd_code = int(w_cmd_code.GetValue())
            except ValueError:
                wx.MessageBox(
                    "msgVersion, nodeType, and cmdCode must be integers",
                    "ERROR",
                    wx.OK | wx.ICON_HAND,
                )
                return

            # Construct the message
            msg_type = 22
            inner_version = 0

            # Combine msg_version (4 bits), node_type (8 bits), and inner_version (4 bits)
            combined_version = ((msg_version & 0xF) << 4) | ((node_type & 0xF0) >> 4)
            combined_inner_version = ((node_type & 0x0F) << 4) | (inner_version & 0xF)

            # Pack the message in the required format
            message = struct.pack(
                "!BBBBH", msg_type, combined_version, combined_inner_version, cmd_code, diag_freq
            )

            # Convert to the desired string format with extra backslashes
            formatted_message = "".join(f"\\x{b:02x}" for b in message)

            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(formatted_message, tty_usb, self)

        def set_custom_config(event):
            if not self.initializing:
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

        wx.StaticText(pnl, label="msgVersion", pos=(115, vertical_pos + 6))
        w_msg_version = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_msg_version.SetMaxLength(10)
        w_msg_version.WriteText("0")
        w_msg_version.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="nodeType", pos=(115, vertical_pos + 6))
        w_node_type = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_node_type.SetMaxLength(10)
        w_node_type.WriteText("0")
        w_node_type.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="cmdCode", pos=(115, vertical_pos + 6))
        w_cmd_code = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_cmd_code.SetMaxLength(10)
        w_cmd_code.WriteText("0")
        w_cmd_code.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Diagnostic Frequency Hz", pos=(115, vertical_pos + 6))
        w_diag_freq = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_diag_freq.SetMaxLength(10)
        w_diag_freq.WriteText("200")
        w_diag_freq.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        configs_list = ["Default", "Custom"]
        wx.StaticText(pnl, label="Load preset configs", pos=(270, vertical_pos - 180))
        w_load_config = wx.ComboBox(
            pnl,
            500,
            value="Default",
            size=(200, 30),
            pos=(270, vertical_pos - 160),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_load_config.Bind(wx.EVT_COMBOBOX, load_config)
        w_load_config.SetStringSelection("Default")

        # Ensure the initial setup does not trigger the set_custom_config function
        self.initializing = True
        load_config(0)
        self.initializing = False

        w_get_diag_data_btn = wx.Button(pnl, label="Get Diag Data", pos=(350, vertical_pos + 35))
        w_get_diag_data_btn.Bind(wx.EVT_BUTTON, request_config)

        self.SetSize((470, vertical_pos + 3 * vertical_pos_increment))
        self.SetTitle("GetDiagData")
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
