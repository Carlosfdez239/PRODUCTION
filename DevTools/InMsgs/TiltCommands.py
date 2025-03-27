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

        def get_raw_data(event):
            print("Average " + w_avg.GetValue())
            send_command("\\x0B" + "\\x{:02x}".format(int(w_avg.GetValue())))

        def set_params(events):
            timestamp = time.time()
            values = (
                timestamp,
                float(w_t1_offset.GetValue()),
                float(w_t1_coef_a.GetValue()),
                float(w_t1_coef_b.GetValue()),
                float(w_t1_coef_c.GetValue()),
                float(w_t1_coef_d.GetValue()),
                float(w_t2_offset.GetValue()),
                float(w_t2_coef_a.GetValue()),
                float(w_t2_coef_b.GetValue()),
                float(w_t2_coef_c.GetValue()),
                float(w_t2_coef_d.GetValue()),
            )
            packer = struct.Struct("!Iffffffffff")
            packed_data = packer.pack(*values)
            cmd = binascii.hexlify(packed_data)
            cmd = "\\x" + "\\x".join(high + low for high, low in zip(cmd[::2], cmd[1::2]))
            send_command("\\x92" + cmd)

        def request_calib(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x00\\x92", tty_usb, self)

        def set_custom_calib(event):
            w_load_calib.SetStringSelection("Custom")

        def load_calib(event):
            calib = w_load_calib.GetValue()

            if calib == "Default":
                w_t1_offset.SetValue("0.0")
                w_t1_coef_a.SetValue("0.0")
                w_t1_coef_b.SetValue("0.0")
                w_t1_coef_c.SetValue("1.0")
                w_t1_coef_d.SetValue("0.0")
                w_t2_offset.SetValue("0.0")
                w_t2_coef_a.SetValue("0.0")
                w_t2_coef_b.SetValue("0.0")
                w_t2_coef_c.SetValue("1.0")
                w_t2_coef_d.SetValue("0.0")
                # update on textctrls change the drop down to custom, change it back
                w_load_calib.SetStringSelection(calib)
            elif calib == "TestNode1":
                w_t1_offset.SetValue("0.08217796241")  # X params for node 1
                w_t1_coef_a.SetValue("-0.000003820734879")
                w_t1_coef_b.SetValue("0.00001447148592")
                w_t1_coef_c.SetValue("1.006522645")
                w_t1_coef_d.SetValue("-0.0002929840657")
                w_t2_offset.SetValue("0.242280671")
                w_t2_coef_a.SetValue(
                    "-0.000005073131622"
                )  # those are actually X params for node 2:
                w_t2_coef_b.SetValue("0.00002613711223")
                w_t2_coef_c.SetValue("1.007359624")
                w_t2_coef_d.SetValue("-0.0004532035797")
                # update on textctrls change the drop down to custom, change it back
                w_load_calib.SetStringSelection(calib)
            if calib == "Silly":
                w_t1_offset.SetValue("1.10")
                w_t1_coef_a.SetValue("2.9")
                w_t1_coef_b.SetValue("3.8")
                w_t1_coef_c.SetValue("4.7")
                w_t1_coef_d.SetValue("5.6")
                w_t2_offset.SetValue("6.5")
                w_t2_coef_a.SetValue("7.4")
                w_t2_coef_b.SetValue("8.3")
                w_t2_coef_c.SetValue("9.2")
                w_t2_coef_d.SetValue("10.1")
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
        wx.StaticText(pnl, label="CoefA", pos=(100 + 100 * 1, vertical_pos))
        wx.StaticText(pnl, label="CoefB", pos=(100 + 100 * 2, vertical_pos))
        wx.StaticText(pnl, label="CoefC", pos=(100 + 100 * 3, vertical_pos))
        wx.StaticText(pnl, label="CoefD", pos=(100 + 100 * 4, vertical_pos))
        vertical_pos = vertical_pos + vertical_pos_increment // 2

        wx.StaticText(pnl, label="Tilt1:", pos=(20, vertical_pos))
        w_t1_offset = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(100, vertical_pos))
        w_t1_offset.SetMaxLength(20)
        w_t1_offset.WriteText("0.00000")
        w_t1_offset.Bind(wx.EVT_TEXT, set_custom_calib)

        w_t1_coef_a = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(100 + 100 * 1, vertical_pos))
        w_t1_coef_a.SetMaxLength(20)
        w_t1_coef_a.WriteText("0.00000")
        w_t1_coef_a.Bind(wx.EVT_TEXT, set_custom_calib)

        w_t1_coef_b = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(100 + 100 * 2, vertical_pos))
        w_t1_coef_b.SetMaxLength(20)
        w_t1_coef_b.WriteText("0.00000")
        w_t1_coef_b.Bind(wx.EVT_TEXT, set_custom_calib)

        w_t1_coef_c = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(100 + 100 * 3, vertical_pos))
        w_t1_coef_c.SetMaxLength(20)
        w_t1_coef_c.WriteText("1.00000")
        w_t1_coef_c.Bind(wx.EVT_TEXT, set_custom_calib)

        w_t1_coef_d = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(100 + 100 * 4, vertical_pos))
        w_t1_coef_d.SetMaxLength(20)
        w_t1_coef_d.WriteText("0.00000")
        w_t1_coef_d.Bind(wx.EVT_TEXT, set_custom_calib)

        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Tilt2:", pos=(20, vertical_pos))
        w_t2_offset = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(100, vertical_pos))
        w_t2_offset.SetMaxLength(20)
        w_t2_offset.WriteText("0.00000")
        w_t2_offset.Bind(wx.EVT_TEXT, set_custom_calib)

        w_t2_coef_a = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(100 + 100 * 1, vertical_pos))
        w_t2_coef_a.SetMaxLength(20)
        w_t2_coef_a.WriteText("0.00000")
        w_t2_coef_a.Bind(wx.EVT_TEXT, set_custom_calib)

        w_t2_coef_b = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(100 + 100 * 2, vertical_pos))
        w_t2_coef_b.SetMaxLength(20)
        w_t2_coef_b.WriteText("0.00000")
        w_t2_coef_b.Bind(wx.EVT_TEXT, set_custom_calib)

        w_t2_coef_c = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(100 + 100 * 3, vertical_pos))
        w_t2_coef_c.SetMaxLength(20)
        w_t2_coef_c.WriteText("1.00000")
        w_t2_coef_c.Bind(wx.EVT_TEXT, set_custom_calib)

        w_t2_coef_d = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(100 + 100 * 4, vertical_pos))
        w_t2_coef_d.SetMaxLength(20)
        w_t2_coef_d.WriteText("0.00000")
        w_t2_coef_d.Bind(wx.EVT_TEXT, set_custom_calib)

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
        self.SetTitle("LSTiltCommands")
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
