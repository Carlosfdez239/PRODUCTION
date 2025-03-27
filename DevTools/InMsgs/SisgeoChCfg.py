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
                w_warmup_delay.SetValue("0")
                w_addr_delay.SetValue("0")
                w_num_channels.SetValue("0")
                w_channels_ids.SetValue("")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "1-5":
                w_warmup_delay.SetValue("0")
                w_addr_delay.SetValue("0")
                w_num_channels.SetValue("5")
                w_channels_ids.SetValue("1 2 3 4 5")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "1-30":
                w_warmup_delay.SetValue("5")
                w_addr_delay.SetValue("5")
                w_num_channels.SetValue("30")
                w_channels_ids.SetValue(
                    "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30"
                )

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Quick Sampling":
                w_warmup_delay.SetValue("0")
                w_addr_delay.SetValue("0")
                w_num_channels.SetValue("1")
                w_channels_ids.SetValue("1")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        # method to set the config
        def set_config(event):

            try:
                warmup_delay = int(w_warmup_delay.GetValue())
                addr_delay = int(w_addr_delay.GetValue())
                num_channels = int(w_num_channels.GetValue())
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
                version = get_sisgeo_version()
                output = "\\x91" + "\\x%0.2X" % version + "\\x00"
                output += (
                    "\\x%0.2X" % num_channels + "\\x%0.2X" % addr_delay + "\\x%0.2X" % warmup_delay
                )
                for sid in ids_channels:
                    output += "\\x%0.2X" % int(sid)
                print(output)
            except:
                msgb = wx.MessageDialog(
                    self, "Error creating message", "ERROR", wx.OK | wx.ICON_HAND
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

        def get_sisgeo_version():
            version_code = 0
            version = w_sigeo_version_config.GetValue()

            if version == "Legacy":
                version_code = 1
            elif version == "V3":
                version_code = 3
            else:
                raise Exception("Invalid sisgeo version")
            return version_code

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Warmup Delay", pos=(115, vertical_pos + 6))
        w_warmup_delay = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_warmup_delay.SetMaxLength(4)
        w_warmup_delay.WriteText("0")
        w_warmup_delay.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Address Delay", pos=(115, vertical_pos + 6))
        w_addr_delay = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_addr_delay.SetMaxLength(4)
        w_addr_delay.WriteText("0")
        w_addr_delay.Bind(wx.EVT_TEXT, set_custom_config)
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
        ]
        wx.StaticText(pnl, label="Num of Channels", pos=(115, vertical_pos + 6))
        w_num_channels = wx.ComboBox(
            pnl, 500, value="1", size=(90, 30), pos=(20, vertical_pos), choices=num_channels_list
        )
        # w_num_channels = wx.TextCtrl(pnl, -1, size = (90, 30), pos = (20,vertical_pos))
        # w_num_channels.SetMaxLength(10)
        # w_num_channels.WriteText('0')
        w_num_channels.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Channels Ids", pos=(20, vertical_pos + 6))
        vertical_pos = vertical_pos + vertical_pos_increment
        w_channels_ids = wx.TextCtrl(
            pnl,
            -1,
            size=(400, 30 + 2 * vertical_pos_increment),
            pos=(20, vertical_pos),
            style=wx.TE_MULTILINE,
        )
        w_channels_ids.WriteText("1")
        w_channels_ids.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + 3 * vertical_pos_increment

        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(260, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        w_set_config_btn = wx.Button(pnl, label="Request Config", pos=(350, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_config)

        configs_list = ["Custom", "Default", "1-5", "1-30", "Quick Sampling"]
        wx.StaticText(pnl, label="Load preset configs", pos=(250, 30))
        w_load_config = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(250, 30 + vertical_pos_increment - 10),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_load_config.Bind(wx.EVT_COMBOBOX, load_config)
        w_load_config.SetStringSelection("Default")
        load_config(0)

        sisgeo_version_list = ["Legacy", "V3"]
        wx.StaticText(pnl, label="Sisgeo version", pos=(250, 30 + 2 * vertical_pos_increment))
        w_sigeo_version_config = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(250, 30 + 3 * vertical_pos_increment - 10),
            choices=sisgeo_version_list,
            style=wx.CB_READONLY,
        )
        w_sigeo_version_config.SetStringSelection("Legacy")

        self.SetSize((470, vertical_pos + vertical_pos_increment))
        self.SetTitle("SisgeoChCfg")
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
