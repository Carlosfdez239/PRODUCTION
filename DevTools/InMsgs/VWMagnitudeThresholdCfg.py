#!/usr/bin/env python3
import binascii
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

            if config != "Custom":
                w_mag_threshold.SetValue(config)

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        def send_command(command):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(command, tty_usb, self)

        # method to set the config
        def set_config(event):
            try:
                mag_threshold = float(w_mag_threshold.GetValue())

            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not a float", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            packer = struct.Struct("!f")
            packed_data = packer.pack(mag_threshold)
            cmd = binascii.hexlify(packed_data)
            cmd = "\\x" + "\\x".join(high + low for high, low in zip(cmd[::2], cmd[1::2]))

            send_command("\\x96" + cmd)

        # method to request the config
        def request_config(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x00\\x96", tty_usb, self)

        def get_mag_data(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x0b\\x00", tty_usb, self)

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

        wx.StaticText(pnl, label="Magnitude Threshold", pos=(115, vertical_pos + 6))
        w_mag_threshold = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_mag_threshold.SetMaxLength(10)
        w_mag_threshold.WriteText("1800")
        w_mag_threshold.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_get_mag_data_btn = wx.Button(pnl, label="Get Magnitude Data", pos=(20, vertical_pos))
        w_get_mag_data_btn.Bind(wx.EVT_BUTTON, get_mag_data)

        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(250, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        w_set_config_btn = wx.Button(pnl, label="Request Config", pos=(340, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_config)

        configs_list = ["Custom", "1000.0", "2000.5", "123.456"]
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
        w_load_config.SetStringSelection("1000.0")
        load_config(0)

        vertical_pos = vertical_pos + vertical_pos_increment
        vertical_pos = vertical_pos + vertical_pos_increment
        self.SetSize((470, vertical_pos))
        self.SetTitle("VWMagnitudeThresholdCfg")
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
