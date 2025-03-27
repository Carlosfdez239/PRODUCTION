#!/usr/bin/env python3
import os
import sys
import time
from subprocess import PIPE, Popen

import wx


class Example(wx.Frame):
    def __init__(self, *args, **kw):
        super(Example, self).__init__(*args, **kw)

        self.init_ui()

    def init_ui(self):
        global global_tty

        # method to set the time
        def set_correction(correction, token):
            try:
                if correction < 0:
                    sign = 1
                    correction = -correction
                else:
                    sign = 0

                tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
                send_msg_uart = Popen(
                    [
                        "../lib/ls_time_correction.sh",
                        str(sign),
                        str(correction),
                        str(token),
                        tty_usb,
                    ],
                    stdout=PIPE,
                )
                (output2, err) = send_msg_uart.communicate()
                send_msg_uart.wait()
            except:
                e = sys.exc_info()[0]
                msgb = wx.MessageDialog(
                    self,
                    "Error executing ../lib/ls_time_correction.sh: " + str(e),
                    "ERROR",
                    wx.OK | wx.ICON_HAND,
                )
                msgb.ShowModal()
                return

        # method to set the config
        def set_time_correction(event):

            try:
                time_correction_to_set = int(w_time_correction.GetValue())
                token_to_set = int(w_token.GetValue())
            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            set_correction(time_correction_to_set, token_to_set)

        # method to request the config

        def set_token(event):
            current_time = int(time.time())
            w_token.SetValue(str(current_time))

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Time correction to set", pos=(115, vertical_pos + 6))
        w_time_correction = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_time_correction.SetMaxLength(11)
        w_time_correction.WriteText("60")
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Token", pos=(115, vertical_pos + 6))
        w_token = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_token.SetMaxLength(10)
        w_token.WriteText("1")

        w_set_token_btn = wx.Button(pnl, label="Set token to current time", pos=(170, vertical_pos))
        w_set_token_btn.Bind(wx.EVT_BUTTON, set_token)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_set_time_btn = wx.Button(pnl, label="Set Time Correction", pos=(255, vertical_pos))
        w_set_time_btn.Bind(wx.EVT_BUTTON, set_time_correction)

        vertical_pos = vertical_pos + vertical_pos_increment
        self.SetSize((420, vertical_pos + vertical_pos_increment))
        self.SetTitle("LSTimeCorrection")
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
