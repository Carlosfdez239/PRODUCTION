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

            if config == "Default":
                w_string_protocol.SetValue("1")
                w_rst_delay.SetValue("Off")
                w_num_channels.SetValue("0")
                w_channels_ids.SetValue("")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "1-5":
                w_string_protocol.SetValue("1")
                w_rst_delay.SetValue("Off")
                w_num_channels.SetValue("5")
                w_channels_ids.SetValue("1 2 3 4 5")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "1-50":
                w_string_protocol.SetValue("1")
                w_rst_delay.SetValue("Off")
                w_num_channels.SetValue("50")
                w_channels_ids.SetValue(
                    "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 "
                    "31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50"
                )

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Quick Sampling":
                w_string_protocol.SetValue("1")
                w_rst_delay.SetValue("Off")
                w_num_channels.SetValue("1")
                w_channels_ids.SetValue("1")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        # method to set the config
        def set_config(event):

            try:
                string_protocol = int(w_string_protocol.GetValue())
                num_channels = int(w_num_channels.GetValue())
                rst_delay_active = 0 if w_rst_delay.GetValue() == "Off" else 1
            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            try:
                ids_channels = w_channels_ids.GetValue().split()
                if len(ids_channels) != num_channels:
                    msgb = wx.MessageDialog(
                        self,
                        "Number of ids is different from number of channels reported",
                        "ERROR",
                        wx.OK | wx.ICON_HAND,
                    )
                    msgb.ShowModal()
                    return
            except:
                msgb = wx.MessageDialog(self, "Could not parse ids", "ERROR", wx.OK | wx.ICON_HAND)
                msgb.ShowModal()
                return

            try:
                msg_str = Popen(
                    [
                        "java",
                        "-jar",
                        "jars/DigGsiChCfg.jar",
                        str(string_protocol),
                        str(rst_delay_active),
                        str(num_channels),
                    ]
                    + ids_channels,
                    stdout=PIPE,
                )
                (output, err) = msg_str.communicate()
                msg_str.wait()
                print(output)
            except:
                msgb = wx.MessageDialog(
                    self, "Error executing jars/DigGsiChCfg.jar", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(output, tty_usb, self)

        # method to request the config
        def request_config(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x00\\x91", tty_usb, self)

        def set_custom_config(event):
            w_load_config.SetStringSelection("Custom")

        width = 500
        outer_margin = 20
        inner_margin = 6

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        obj_width = 90
        obj_height = 30
        wx.StaticText(
            pnl, label="ttyUSB", pos=(outer_margin + obj_width + inner_margin, vertical_pos + 6)
        )
        w_tty_usb = wx.TextCtrl(
            pnl, -1, size=(obj_width, obj_height), pos=(outer_margin, vertical_pos)
        )
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        string_protocol_list = ["0", "1"]
        wx.StaticText(pnl, label="String Protocol", pos=(115, vertical_pos + 6))
        w_string_protocol = wx.ComboBox(
            pnl, 500, value="0", size=(90, 30), pos=(20, vertical_pos), choices=string_protocol_list
        )
        w_string_protocol.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        rst_delay_list = ["On", "Off"]
        wx.StaticText(pnl, label="RST Delay", pos=(115, vertical_pos + 6))
        w_rst_delay = wx.ComboBox(
            pnl, 500, value="Off", size=(90, 30), pos=(20, vertical_pos), choices=rst_delay_list
        )
        w_rst_delay.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        num_channels_list = [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
            "19",
            "20",
            "21",
            "22",
            "23",
            "24",
            "25",
            "26",
            "27",
            "28",
            "29",
            "30",
            "31",
            "32",
            "33",
            "34",
            "35",
            "36",
            "37",
            "38",
            "39",
            "40",
            "41",
            "42",
            "43",
            "44",
            "45",
            "46",
            "47",
            "48",
            "49",
            "50",
        ]
        wx.StaticText(pnl, label="Num of Channels", pos=(115, vertical_pos + 6))
        w_num_channels = wx.ComboBox(
            pnl, 500, value="1", size=(90, 30), pos=(20, vertical_pos), choices=num_channels_list
        )
        w_num_channels.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Channels Ids", pos=(20, vertical_pos + 6))
        vertical_pos = vertical_pos + vertical_pos_increment
        w_channels_ids = wx.TextCtrl(
            pnl,
            -1,
            size=(width - (outer_margin * 2), 30 + 2 * vertical_pos_increment),
            pos=(outer_margin, vertical_pos),
            style=wx.TE_MULTILINE,
        )
        w_channels_ids.WriteText("1")
        w_channels_ids.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + 3 * vertical_pos_increment

        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(260, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        w_set_config_btn = wx.Button(pnl, label="Request Config", pos=(350, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_config)

        configs_list = ["Custom", "Default", "1-5", "1-50", "Quick Sampling"]
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

        vertical_pos = vertical_pos + vertical_pos_increment
        self.SetSize((width, vertical_pos + vertical_pos_increment + outer_margin))
        self.SetTitle("DigGsiChCfg")
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
