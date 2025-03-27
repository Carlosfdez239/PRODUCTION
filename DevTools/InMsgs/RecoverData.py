#!/usr/bin/env python3
import os
import sys
from subprocess import PIPE, Popen

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

            if config == "All data all time":
                w_data_type.SetValue("All")
                w_start_time.SetValue("0")
                w_end_time.SetValue("4294967295")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Default Test":
                w_start_time.SetValue("240")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        # method to set the config

        def request_data(event):
            def w_type_to_int(w_type):
                if w_type == "All":
                    return 0
                if w_type == "Health":
                    return 64
                if w_type == "Health-v2":
                    return 70
                if w_type == "Health-v3":
                    return 79
                if w_type == "VW":
                    return 65
                if w_type == "GSI-deprecated":
                    return 66
                if w_type == "DIG":
                    return 68
                if w_type == "Voltage":
                    return 67
                if w_type == "Tilt":
                    return 69
                if w_type == "Laser":
                    return 73
                if w_type == "Pnode":
                    return 71
                if w_type == "SIPI":
                    return 72
                if w_type == "GMM":
                    return 75
                if w_type == "Tilt360":
                    return 76
                if w_type == "Laser360":
                    return 78
                if w_type == "Tilt360A":
                    return 80
                if w_type == "DYN Data":
                    return 82
                if w_type == "DYN Short Event Data":
                    return 83
                if w_type == "GNSS Statistics":
                    return 84
                if w_type == "GNSS Rover Data":
                    return 85
                if w_type == "RAW Storage Data":
                    return 86
                if w_type == "GNSS Raw Data":
                    return 87

            try:
                data_type = w_type_to_int(w_data_type.GetValue())
                start_time = int(w_start_time.GetValue())
                end_time = int(w_end_time.GetValue())

            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            try:
                msg_str = Popen(
                    [
                        "java",
                        "-jar",
                        "jars/RecoverData.jar",
                        str(data_type),
                        str(start_time),
                        str(end_time),
                    ],
                    stdout=PIPE,
                )
                (output, err) = msg_str.communicate()
                msg_str.wait()
            except:
                msgb = wx.MessageDialog(
                    self, "Error executing jars/RecoverData.jar", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(output, tty_usb, self)

        # method to request the config
        def request_interval(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x04", tty_usb, self)

        def set_custom_config(event):
            w_load_config.SetStringSelection("Custom")

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        vertical_pos_increment = 35
        element_width = 110
        horizontal_pos = element_width + 30

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(horizontal_pos, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(element_width, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        data_type_list = [
            "All",
            "Health",
            "Health-v2",
            "Health-v3",
            "VW",
            "DIG",
            "GMM",
            "Voltage",
            "Tilt",
            "Tilt360",
            "Tilt360A",
            "Laser",
            "Laser360",
            "Pnode",
            "SIPI",
            "GSI-deprecated",
            "DYN Data",
            "DYN Short Event Data",
            "GNSS Statistics",
            "GNSS Rover Data",
            "RAW Storage Data",
            "GNSS Raw Data",
        ]
        wx.StaticText(pnl, label="Data type", pos=(horizontal_pos, vertical_pos + 6))
        w_data_type = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(element_width, 30),
            pos=(20, vertical_pos),
            choices=data_type_list,
            style=wx.CB_READONLY,
        )
        w_data_type.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Start time", pos=(horizontal_pos, vertical_pos + 6))
        w_start_time = wx.TextCtrl(pnl, -1, size=(element_width, 30), pos=(20, vertical_pos))
        w_start_time.SetMaxLength(10)
        w_start_time.WriteText("1800")
        w_start_time.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="End time", pos=(horizontal_pos, vertical_pos + 6))
        w_end_time = wx.TextCtrl(pnl, -1, size=(element_width, 30), pos=(20, vertical_pos))
        w_end_time.SetMaxLength(10)
        w_end_time.WriteText("1800")
        w_end_time.Bind(wx.EVT_TEXT, set_custom_config)

        vertical_pos = vertical_pos + 2 * vertical_pos_increment
        w_set_config_btn = wx.Button(pnl, label="Request data", pos=(200, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_data)

        w_set_config_btn = wx.Button(pnl, label="Request Interval", pos=(350, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_interval)
        vertical_pos = vertical_pos + vertical_pos_increment

        horizontal_pos += 150
        configs_list = ["Custom", "All data all time"]
        wx.StaticText(pnl, label="Load preset configs", pos=(horizontal_pos, 16))
        w_load_config = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(horizontal_pos, 10 + vertical_pos_increment),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_load_config.Bind(wx.EVT_COMBOBOX, load_config)
        w_load_config.SetStringSelection("All data all time")
        load_config(0)

        self.SetSize((horizontal_pos + 250, vertical_pos + 2 * vertical_pos_increment))
        self.SetTitle("RecoverData")
        self.Centre()
        self.Show(True)


def main():
    # Global variables to call ls_send_message_uart
    global use_socket
    global server_ip
    # Global variables to call ls_send_message_uart

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
