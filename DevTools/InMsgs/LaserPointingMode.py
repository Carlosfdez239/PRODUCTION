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

        def load_config(event):

            config = w_load_config.GetValue()

            if config == "Default":
                w_pointing_time.SetValue("30")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)
            if config == "5 minutes":
                w_pointing_time.SetValue("300")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        # method to set the config
        def set_config(event):
            try:
                pointing_time = int(w_pointing_time.GetValue())

            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            version = 0
            msg2send = "\\x50"
            msg2send += "\\x%02X" % version
            msg2send += "\\x%02X" % (pointing_time >> 8) + "\\x%02X" % (pointing_time & 0x00FF)
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(msg2send, tty_usb, self)

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

        wx.StaticText(pnl, label="Laser Pointing Time", pos=(115, vertical_pos + 6))
        w_pointing_time = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_pointing_time.SetMaxLength(10)
        w_pointing_time.WriteText("1800")
        w_pointing_time.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment
        vertical_pos = vertical_pos + vertical_pos_increment

        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(260, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        configs_list = ["Default", "5 minutes"]
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
        w_load_config.SetStringSelection("Default")
        load_config(0)

        self.SetSize((470, vertical_pos + vertical_pos_increment))
        self.SetTitle("LaserPointingMode")
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
