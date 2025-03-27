#!/usr/bin/env python3
import os
import sys

import wx
from ls_utils import ls_send_message_uart
from remote_configs import convert_to_remote_config

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
                w_message_version.SetValue("0")
                w_reserved.SetValue("0")
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        def build_config_binary():
            output = None
            try:

                message_version = int(w_message_version.GetValue())
                if message_version > 3:
                    msgb = wx.MessageDialog(
                        self, "Version valid range is [0-3]", "ERROR", wx.OK | wx.ICON_HAND
                    )
                    msgb.ShowModal()
                    return
                config_byte = (message_version << 6) & 0xC0

                reserved_value = int(w_reserved.GetValue())
                if reserved_value > 7:
                    msgb = wx.MessageDialog(
                        self, "Reserved valid range is [0-7]", "ERROR", wx.OK | wx.ICON_HAND
                    )
                    msgb.ShowModal()
                    return
                config_byte = config_byte | (reserved_value << 3) & 0x38

                if w_ch1_enabled.GetValue():
                    config_byte = config_byte | 0x01
                if w_ch2_enabled.GetValue():
                    config_byte = config_byte | 0x02
                if w_ch3_enabled.GetValue():
                    config_byte = config_byte | 0x04

                output = "\\x9A"
                output += "\\x%02X" % config_byte
            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()

            return output

        # method to set the config

        def set_config(event):

            output = build_config_binary()

            if output:
                tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
                ls_send_message_uart(output, tty_usb, self)

        def set_remote_config(event):
            output = build_config_binary()

            if output:

                remote_output = convert_to_remote_config(output, w_token.GetValue())
                tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
                ls_send_message_uart(remote_output, tty_usb, self)

        # method to request the config
        def request_config(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x00\\x9A", tty_usb, self)

        def set_custom_config(event):
            w_load_config.SetStringSelection("Custom")

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Config version", pos=(20, vertical_pos + 6))
        w_message_version = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(130, vertical_pos))
        w_message_version.SetMaxLength(1)
        w_message_version.WriteText("240")
        w_message_version.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="Reserved bits", pos=(20, vertical_pos + 6))
        w_reserved = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(130, vertical_pos))
        w_reserved.SetMaxLength(1)
        w_reserved.WriteText("240")
        w_reserved.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        w_ch1_enabled = wx.CheckBox(pnl, label="Ch1", pos=(40, vertical_pos))
        w_ch1_enabled.SetValue(True)
        w_ch1_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_ch2_enabled = wx.CheckBox(pnl, label="Ch2", pos=(120, vertical_pos))
        w_ch2_enabled.SetValue(True)
        w_ch2_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_ch3_enabled = wx.CheckBox(pnl, label="Ch3", pos=(200, vertical_pos))
        w_ch3_enabled.SetValue(True)
        w_ch3_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        vertical_pos += vertical_pos_increment

        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(280, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        w_set_config_btn = wx.Button(pnl, label="Request Config", pos=(280 + 100, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_config)
        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="Remote Token", pos=(20, vertical_pos + 6))
        w_token = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(130, vertical_pos))
        w_token.SetMaxLength(3)
        w_token.WriteText("1")
        w_set_remote_config_btn = wx.Button(pnl, label="Set Remote Config", pos=(280, vertical_pos))
        w_set_remote_config_btn.Bind(wx.EVT_BUTTON, set_remote_config)

        configs_list = ["Custom", "Default"]
        wx.StaticText(pnl, label="Load preset configs", pos=(300, 20))
        w_load_config = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(300, 20 + vertical_pos_increment / 2),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_load_config.Bind(wx.EVT_COMBOBOX, load_config)
        w_load_config.SetStringSelection("Default")
        load_config(0)

        vertical_pos = vertical_pos + vertical_pos_increment
        self.SetSize((520, vertical_pos))
        self.SetTitle("Tilt360ChCfg")
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
