#!/usr/bin/env python3
import os
import struct
import sys

import wx
from ls_utils import ls_send_message_uart

sys.path.append("../lib/")

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
                w_response_size.SetValue("43")
                w_total_petition_packet.SetValue("1")
                w_response_offset_ms.SetValue("10")
                w_msg_version.SetValue("0")
                w_cmd_code.SetValue("1")
                self.initializing = False

        def request_config(event):
            # Retrieve values from the UI elements
            try:
                response_size = int(w_response_size.GetValue())
                total_petition_packet = int(w_total_petition_packet.GetValue())
                response_offset_ms = int(w_response_offset_ms.GetValue())
                msg_version = int(w_msg_version.GetValue())
                cmd_code = int(w_cmd_code.GetValue())
            except ValueError:
                wx.MessageBox(
                    "All fields must contain integer values.", "ERROR", wx.OK | wx.ICON_ERROR
                )
                return

            # Fixed values for node type and RFU
            node_type = 1  # Fixed node type value
            rfu = 0  # Fixed RFU value

            # Construct the message fields according to specified sizes
            msg_type = 22
            inner_version = 0

            # Combine message components
            combined_version = ((msg_version & 0xF) << 4) | ((node_type & 0xF0) >> 4)
            combined_inner_version = ((node_type & 0x0F) << 4) | (inner_version & 0xF)

            # Pack the message in the required format
            last_byte1 = (total_petition_packet & 0x7) << 5 | ((response_offset_ms >> 3) & 0x1F)
            last_byte2 = ((response_offset_ms & 0x07) << 5) | (rfu & 0x1F)

            message = struct.pack(
                "!BBBBBBB",
                msg_type,
                combined_version,
                combined_inner_version,
                cmd_code,
                response_size,
                last_byte1,
                last_byte2,
            )

            # Convert to the desired string format with extra backslashes
            formatted_message = "".join(f"\\x{b:02x}" for b in message)

            # Send the message using the provided tty_usb
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(formatted_message, tty_usb, self)
            # wx.MessageBox("Message sent successfully!", "Info", wx.OK | wx.ICON_INFORMATION)

        def set_custom_config(event):
            if not self.initializing:
                w_load_config.SetStringSelection("Custom")

        # Define all UI elements here before calling load_config
        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="msgVersion", pos=(115, vertical_pos + 6))
        w_msg_version = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_msg_version.SetMaxLength(10)
        w_msg_version.WriteText("0")
        w_msg_version.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="cmdCode", pos=(115, vertical_pos + 6))
        w_cmd_code = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_cmd_code.SetMaxLength(10)
        w_cmd_code.WriteText("1")
        w_cmd_code.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="Response Size", pos=(115, vertical_pos + 6))
        w_response_size = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_response_size.SetMaxLength(10)
        w_response_size.WriteText("43")
        w_response_size.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="Total Petition Packet", pos=(115, vertical_pos + 6))
        w_total_petition_packet = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_total_petition_packet.SetMaxLength(10)
        w_total_petition_packet.WriteText("1")
        w_total_petition_packet.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="Response Offset Ms", pos=(115, vertical_pos + 6))
        w_response_offset_ms = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_response_offset_ms.SetMaxLength(10)
        w_response_offset_ms.WriteText("10")
        w_response_offset_ms.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        configs_list = ["Default", "Custom"]
        wx.StaticText(pnl, label="Load preset configs", pos=(270, vertical_pos - 175))
        w_load_config = wx.ComboBox(
            pnl,
            500,
            value="Default",
            size=(200, 30),
            pos=(270, vertical_pos - 155),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_load_config.Bind(wx.EVT_COMBOBOX, load_config)
        w_load_config.SetStringSelection("Default")

        # Call load_config after all UI elements have been created
        self.initializing = True
        load_config(0)
        self.initializing = False

        w_get_diag_data_btn = wx.Button(
            pnl, label="Get Coverage Data", pos=(270, vertical_pos + 35)
        )
        w_get_diag_data_btn.Bind(wx.EVT_BUTTON, request_config)

        self.SetSize((530, (vertical_pos + 70) + 3 * vertical_pos_increment))
        self.SetTitle("GNSS GetCoveragePos Data")
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
