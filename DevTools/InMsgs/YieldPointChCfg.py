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

        # method to set the config

        def set_config(event):

            try:
                output = "\\x91\\x07\\x00"
                # print output
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

        vertical_pos = 20

        pnl = wx.Panel(self, -1)

        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(20 + 100, 60 + vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        w_set_config_btn = wx.Button(
            pnl, label="Request Config", pos=(135 + 100, 60 + vertical_pos)
        )
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_config)

        wx.StaticText(
            pnl, label="This tool configures the node to read Yieldpoint sensors", pos=(50, 30)
        )
        wx.StaticText(pnl, label="Same config is used for all Yieldpoint sensors", pos=(50, 50))

        self.SetSize((470, 203))
        self.SetTitle("YieldPointChCfg")
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
        print("Usage " + os.path.basename(__file__) + " [serial_tty] [-s IP]")
        sys.exit(1)
    ex = wx.App()
    Example(None)
    ex.MainLoop()


if __name__ == "__main__":
    main()
