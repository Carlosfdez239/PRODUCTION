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
        def set_time(time_to_set):
            try:
                tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
                send_msg_uart = Popen(
                    ["../lib/ls_set_time.sh", str(time_to_set), tty_usb], stdout=PIPE
                )
                (output2, err) = send_msg_uart.communicate()
                send_msg_uart.wait()
                w_time.SetValue(str(time_to_set))
                self.last_set_time = int(time.time())
            except:
                e = sys.exc_info()[0]
                msgb = wx.MessageDialog(
                    self,
                    "Error executing ../lib/ls_set_time.sh: " + str(e),
                    "ERROR",
                    wx.OK | wx.ICON_HAND,
                )
                msgb.ShowModal()
                return

        # method to set the config
        def set_given_time(event):

            try:
                time_to_set = int(w_time.GetValue())
            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            set_time(time_to_set)

        def set_1000_time(event):
            set_time(1000)

        # method to request the config

        def set_current_time(event):
            current_time = int(time.time())
            set_time(current_time)

        def update_last_set_time(event):
            timer.Start(1000)  # milliseconds
            current_time = int(time.time())
            w_last_set_elapsed.SetValue(str(current_time - self.last_set_time))

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Time to set", pos=(115, vertical_pos + 6))
        w_time = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_time.SetMaxLength(10)
        w_time.WriteText("1000")
        vertical_pos = vertical_pos + vertical_pos_increment

        w_set_1000_btn = wx.Button(pnl, label="Set time to 1000", pos=(20, vertical_pos))
        w_set_1000_btn.Bind(wx.EVT_BUTTON, set_1000_time)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Seconds elapsed since last change", pos=(235, 20 + 6))
        w_last_set_elapsed = wx.TextCtrl(
            pnl,
            -1,
            size=(90, 30),
            pos=(300, 20 + vertical_pos_increment),
            style=wx.TE_READONLY | wx.TE_RIGHT,
        )
        w_last_set_elapsed.SetMaxLength(11)
        w_last_set_elapsed.WriteText("1000")

        self.last_set_time = 0

        timer_id = 100  # pick a number
        timer = wx.Timer(pnl, timer_id)  # message will be sent to the panel
        timer.Start(1000)  # milliseconds
        try:
            wx.EVT_TIMER(pnl, timer_id, update_last_set_time)  # call the on_timer function
        except:  # to add compatibility with new version of libraries
            pnl.Bind(wx.EVT_TIMER, update_last_set_time)  # call the on_timer function

        w_set_time_btn = wx.Button(pnl, label="Set Time", pos=(255, vertical_pos))
        w_set_time_btn.Bind(wx.EVT_BUTTON, set_given_time)

        w_set_current_time = wx.Button(pnl, label="Set current time", pos=(345, vertical_pos))
        w_set_current_time.Bind(wx.EVT_BUTTON, set_current_time)
        vertical_pos = vertical_pos + vertical_pos_increment

        self.SetSize((480, (vertical_pos + vertical_pos_increment)))
        self.SetTitle("LSSetTime")
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
