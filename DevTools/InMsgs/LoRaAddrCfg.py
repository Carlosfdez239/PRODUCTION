#!/usr/bin/env python3
import os
import sys
import time
from subprocess import PIPE, Popen

import wx
from ls_utils import ls_send_message_uart


class Example(wx.Frame):
    def __init__(self, *args, **kw):
        super(Example, self).__init__(*args, **kw)

        self.init_ui()

    def init_ui(self):
        global global_tty

        # method to set the config
        def set_addr(addr_to_set):
            try:
                tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
                send_msg_uart = Popen(
                    ["../lib/ls_set_lora_addr.sh", str(addr_to_set), tty_usb], stdout=PIPE
                )
                (output2, err) = send_msg_uart.communicate()
                send_msg_uart.wait()
                w_addr.SetValue(str(addr_to_set))
                self.last_set_time = int(time.time())
            except:
                e = sys.exc_info()[0]
                msgb = wx.MessageDialog(
                    self,
                    "Error executing ../lib/ls_set_lora_addr.sh: " + str(e),
                    "ERROR",
                    wx.OK | wx.ICON_HAND,
                )
                msgb.ShowModal()
                return

        # method to set the config
        def set_given_addr(event):

            try:
                addr_to_set = int(w_addr.GetValue())
            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            set_addr(addr_to_set)

        # method to request the config
        def request_config(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x00\\x83", tty_usb, self)

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Address", pos=(115, vertical_pos + 6))
        w_addr = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_addr.SetMaxLength(10)
        w_addr.WriteText("1000")
        vertical_pos = vertical_pos + vertical_pos_increment

        w_set_cfg_btn = wx.Button(pnl, label="Set Addr Config", pos=(175, vertical_pos))
        w_set_cfg_btn.Bind(wx.EVT_BUTTON, set_given_addr)

        w_set_config_btn = wx.Button(pnl, label="Request Config", pos=(300, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_config)

        vertical_pos = vertical_pos + vertical_pos_increment
        self.SetSize((430, vertical_pos + vertical_pos_increment))
        self.SetTitle("LSLoRaAddrCfg")
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
