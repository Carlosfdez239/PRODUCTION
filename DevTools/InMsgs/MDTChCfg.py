#!/usr/bin/env python
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
                w_enabled.SetValue("1")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        # method to set the config

        def set_config(event):

            try:
                enabled = int(w_enabled.GetValue())
            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            try:
                output = "\\x91\\x02\\x00"
                output += "\\x%0.2X" % enabled
                print(output)
            except:
                msgb = wx.MessageDialog(
                    self, "Error creating message", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            ls_send_message_uart(output, global_tty, self)

        # method to request the config
        def request_config(event):
            ls_send_message_uart("\\x00\\x91", global_tty, self)

        def set_custom_config(event):
            w_load_config.SetStringSelection("Custom")

        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        enabled_list = ["0", "1"]
        wx.StaticText(pnl, label="Enabled", pos=(115, vertical_pos + 6))
        w_enabled = wx.ComboBox(
            pnl, 500, value="1", size=(90, 30), pos=(20, vertical_pos), choices=enabled_list
        )
        w_enabled.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(260, 60 + vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        w_set_config_btn = wx.Button(pnl, label="Request Config", pos=(350, 60 + vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_config)

        configs_list = ["Custom", "Default"]
        wx.StaticText(pnl, label="Load preset configs", pos=(250, 30))
        w_load_config = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(250, 30 + vertical_pos_increment),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_load_config.Bind(wx.EVT_COMBOBOX, load_config)
        w_load_config.SetStringSelection("Default")
        load_config(0)

        self.SetSize((470, 203))
        self.SetTitle("MDTChCfg")
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
