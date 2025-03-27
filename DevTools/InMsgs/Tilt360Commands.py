#!/usr/bin/env python3
import binascii
import os
import struct
import sys
import time

import wx
from ls_utils import ls_send_message_uart


class Example(wx.Frame):
    def __init__(self, *args, **kw):
        super(Example, self).__init__(*args, **kw)

        self.init_ui()

    def init_ui(self):
        global global_tty

        # method to set the time
        def send_command(command):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(command, tty_usb, self)

        def get_health(event):
            send_command("\\x01")

        def get_data(event):
            send_command("\\x02")

        # def get_raw_data(event):
        #    tty_usb = '/dev/ttyUSB' + w_tty_usb.GetValue()
        #    ls_send_message_uart("\\x0b\\x00",tty_usb, self)
        def get_raw_data(event):
            print("Average " + w_avg.GetValue())
            send_command("\\x0B" + "\\x{:02x}".format(int(w_avg.GetValue())))

        def set_params(events):
            timestamp = time.time()
            values = (
                int(timestamp),
                float(w_t1_gain.GetValue()),
                float(w_t1_offset.GetValue()),
                float(w_t2_gain.GetValue()),
                float(w_t2_offset.GetValue()),
                float(w_t3_gain.GetValue()),
                float(w_t3_offset.GetValue()),
            )
            packer = struct.Struct("!Iffffff")
            packed_data = packer.pack(*values)
            cmd = binascii.hexlify(packed_data).decode("utf-8")
            cmd = "\\x" + "\\x".join(high + low for high, low in zip(cmd[::2], cmd[1::2]))
            send_command("\\x98" + cmd)

        def request_calib(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x00\\x98", tty_usb, self)

        def set_custom_calib(event):
            w_load_calib.SetStringSelection("Custom")

        def load_calib(event):
            calib = w_load_calib.GetValue()

            if calib == "Default":
                w_t1_offset.SetValue("0.0")
                w_t1_gain.SetValue("1.0")
                w_t2_offset.SetValue("0.0")
                w_t2_gain.SetValue("1.0")
                w_t3_offset.SetValue("0.0")
                w_t3_gain.SetValue("1.0")
                # update on textctrls change the drop down to custom, change it back
                w_load_calib.SetStringSelection(calib)
            elif calib == "TestNode1":
                w_t1_offset.SetValue("2.0")
                w_t1_gain.SetValue("1.0")
                w_t2_offset.SetValue("3.0")
                w_t2_gain.SetValue("1.0")
                w_t3_offset.SetValue("4.0")
                w_t3_gain.SetValue("1.0")
                # update on textctrls change the drop down to custom, change it back
                w_load_calib.SetStringSelection(calib)
            if calib == "Silly":
                w_t1_offset.SetValue("1.7")
                w_t1_gain.SetValue("2.8")
                w_t2_offset.SetValue("3.9")
                w_t2_gain.SetValue("4.10")
                w_t3_offset.SetValue("5.11")
                w_t3_gain.SetValue("6.12")
                # update on textctrls change the drop down to custom, change it back
                w_load_calib.SetStringSelection(calib)

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        w_get_health_btn = wx.Button(pnl, label="Get health", pos=(20, vertical_pos))
        w_get_health_btn.Bind(wx.EVT_BUTTON, get_health)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Average Samples", pos=(115, vertical_pos + 6))
        w_avg = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_avg.SetMaxLength(3)
        w_avg.WriteText("1")
        vertical_pos = vertical_pos + vertical_pos_increment

        w_get_raw_data_btn = wx.Button(pnl, label="Get RAW data", pos=(20, vertical_pos))
        w_get_raw_data_btn.Bind(wx.EVT_BUTTON, get_raw_data)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_get_data_btn = wx.Button(pnl, label="Get data", pos=(20, vertical_pos))
        w_get_data_btn.Bind(wx.EVT_BUTTON, get_data)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Offset", pos=(100, vertical_pos))
        wx.StaticText(pnl, label="Gain", pos=(100 + 100 * 1, vertical_pos))

        vertical_pos = vertical_pos + vertical_pos_increment // 2

        wx.StaticText(pnl, label="Axis1:", pos=(20, vertical_pos))
        w_t1_offset = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(100, vertical_pos))
        w_t1_offset.SetMaxLength(20)
        w_t1_offset.WriteText("0.00000")
        w_t1_offset.Bind(wx.EVT_TEXT, set_custom_calib)

        w_t1_gain = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(100 + 100 * 1, vertical_pos))
        w_t1_gain.SetMaxLength(20)
        w_t1_gain.WriteText("0.00000")
        w_t1_gain.Bind(wx.EVT_TEXT, set_custom_calib)

        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Axis2:", pos=(20, vertical_pos))
        w_t2_offset = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(100, vertical_pos))
        w_t2_offset.SetMaxLength(20)
        w_t2_offset.WriteText("0.00000")
        w_t2_offset.Bind(wx.EVT_TEXT, set_custom_calib)

        w_t2_gain = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(100 + 100 * 1, vertical_pos))
        w_t2_gain.SetMaxLength(20)
        w_t2_gain.WriteText("0.00000")
        w_t2_gain.Bind(wx.EVT_TEXT, set_custom_calib)

        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Axis3:", pos=(20, vertical_pos))
        w_t3_offset = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(100, vertical_pos))
        w_t3_offset.SetMaxLength(20)
        w_t3_offset.WriteText("0.00000")
        w_t3_offset.Bind(wx.EVT_TEXT, set_custom_calib)

        w_t3_gain = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(100 + 100 * 1, vertical_pos))
        w_t3_gain.SetMaxLength(20)
        w_t3_gain.WriteText("0.00000")
        w_t3_gain.Bind(wx.EVT_TEXT, set_custom_calib)

        vertical_pos = vertical_pos + vertical_pos_increment

        w_get_data_btn = wx.Button(pnl, label="Request Calib", pos=(20, vertical_pos))
        w_get_data_btn.Bind(wx.EVT_BUTTON, request_calib)

        w_get_data_btn = wx.Button(pnl, label="Set Params", pos=(150, vertical_pos))
        w_get_data_btn.Bind(wx.EVT_BUTTON, set_params)

        calibs_list = ["Custom", "Default", "TestNode1", "Silly"]
        wx.StaticText(pnl, label="Preset calibs:", pos=(300, vertical_pos))
        w_load_calib = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(150, 30),
            pos=(400, vertical_pos),
            choices=calibs_list,
            style=wx.CB_READONLY,
        )
        w_load_calib.Bind(wx.EVT_COMBOBOX, load_calib)
        w_load_calib.SetStringSelection("Default")
        load_calib(1)

        vertical_pos = vertical_pos + vertical_pos_increment * 2

        self.SetSize((650, vertical_pos))
        self.SetTitle("LSTilt360Commands")
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
