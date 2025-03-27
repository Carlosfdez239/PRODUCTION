#!/usr/bin/env python3
import os
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

        # method to enable the certification module
        def enable_module(event):

            output = "15000001"
            output = "\\x" + "\\x".join(a + b for a, b in zip(output[::2], output[1::2]))
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(output, tty_usb, self)

        # method to disable the certification module
        def disable_module(event):

            output = "15000000"
            output = "\\x" + "\\x".join(a + b for a, b in zip(output[::2], output[1::2]))
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(output, tty_usb, self)

        # method to check the status the certification module
        def check_module(event):

            output = "15000002"
            output = "\\x" + "\\x".join(a + b for a, b in zip(output[::2], output[1::2]))
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(output, tty_usb, self)

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(140, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(30, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        w_set_config_btn = wx.Button(pnl, label="Enable Module", pos=(30, vertical_pos))
        vertical_pos = vertical_pos + vertical_pos_increment
        w_set_config_btn.Bind(wx.EVT_BUTTON, enable_module)

        w_set_config_btn = wx.Button(pnl, label="Disable Module", pos=(30, vertical_pos))
        vertical_pos = vertical_pos + vertical_pos_increment
        w_set_config_btn.Bind(wx.EVT_BUTTON, disable_module)

        w_set_config_btn = wx.Button(pnl, label="Module Status", pos=(30, vertical_pos))
        vertical_pos = vertical_pos + vertical_pos_increment
        w_set_config_btn.Bind(wx.EVT_BUTTON, check_module)

        vertical_pos = vertical_pos + vertical_pos_increment
        vertical_pos = vertical_pos + vertical_pos_increment
        self.SetSize((250, vertical_pos))
        self.SetTitle("LoRaEnableCertificationModule")
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
