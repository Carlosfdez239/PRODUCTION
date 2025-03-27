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
                w_ch0_enabled.SetValue(False)
                w_ch1_enabled.SetValue(False)
                w_ch2_enabled.SetValue(False)

                w_input_type_ch_0.SetValue("Gauge")

                w_warmup_time_ch_0.SetValue("0")
                w_warmup_time_ch_1.SetValue("0")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Default Test":
                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)

                w_input_type_ch_0.SetValue("Gauge")

                w_warmup_time_ch_0.SetValue("0")
                w_warmup_time_ch_1.SetValue("0")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        # method to set the config

        def set_config(event):
            def w_in_type_to_int(w_type):
                if w_type == "Gauge":
                    return 0
                if w_type == "Potentiometer":
                    return 1
                if w_type == "Volt Single Ended":
                    return 2
                if w_type == "Volt Differential":
                    return 3
                else:
                    return 255

            try:
                enabled_channels_map = 0
                if w_ch0_enabled.GetValue():
                    enabled_channels_map = enabled_channels_map | 0x01
                if w_ch1_enabled.GetValue():
                    enabled_channels_map = enabled_channels_map | 0x02
                if w_ch2_enabled.GetValue():
                    enabled_channels_map = enabled_channels_map | 0x04

                input_type_0 = w_in_type_to_int(w_input_type_ch_0.GetValue())

                warmup_time_0 = int(w_warmup_time_ch_0.GetValue())
                warmup_time_1 = int(w_warmup_time_ch_1.GetValue())

            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            output = "\\x93"
            output += "\\x%02X" % enabled_channels_map
            output += "\\x%02X" % input_type_0
            output += "\\x%02X" % (warmup_time_0 >> 8) + "\\x%02X" % (warmup_time_0 & 0x00FF)
            output += "\\x%02X" % (warmup_time_1 >> 8) + "\\x%02X" % (warmup_time_1 & 0x00FF)
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(output, tty_usb, self)

        # method to request the config
        def request_config(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x00\\x93", tty_usb, self)

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

        input_type_list = ["Gauge", "Potentiometer", "Volt Single Ended", "Volt Differential"]

        wx.StaticText(pnl, label="Enabled", pos=(20, vertical_pos))
        wx.StaticText(pnl, label="Input Type", pos=(100, vertical_pos))
        wx.StaticText(pnl, label="Warmup Time", pos=(200, vertical_pos))
        vertical_pos += vertical_pos_increment // 2

        w_ch0_enabled = wx.CheckBox(pnl, label="Ch0", pos=(20, vertical_pos))
        w_ch0_enabled.SetValue(True)
        w_ch0_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_input_type_ch_0 = wx.ComboBox(
            pnl, 500, value="Gauge", size=(90, 30), pos=(100, vertical_pos), choices=input_type_list
        )
        w_input_type_ch_0.Bind(wx.EVT_TEXT, set_custom_config)
        w_warmup_time_ch_0 = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(200, vertical_pos))
        w_warmup_time_ch_0.SetMaxLength(10)
        w_warmup_time_ch_0.WriteText("240")
        w_warmup_time_ch_0.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        w_ch1_enabled = wx.CheckBox(pnl, label="Ch1 - Thermistor", pos=(20, vertical_pos))
        w_ch1_enabled.SetValue(True)
        w_ch1_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_warmup_time_ch_1 = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(200, vertical_pos))
        w_warmup_time_ch_1.SetMaxLength(10)
        w_warmup_time_ch_1.WriteText("240")
        w_warmup_time_ch_1.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        w_ch2_enabled = wx.CheckBox(pnl, label="Ch2 - Pulse Counter", pos=(20, vertical_pos))
        w_ch2_enabled.SetValue(True)
        w_ch2_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_warmup_time_ch_1.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        vertical_pos = vertical_pos + vertical_pos_increment // 2
        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(300, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        w_set_config_btn = wx.Button(pnl, label="Request Config", pos=(300 + 90, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_config)

        configs_list = ["Custom", "Default Test"]
        wx.StaticText(pnl, label="Load preset configs", pos=(300, 20))
        w_load_config = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(300, 20 + vertical_pos_increment // 2),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_load_config.Bind(wx.EVT_COMBOBOX, load_config)
        w_load_config.SetStringSelection("Default Test")
        load_config(0)

        vertical_pos = vertical_pos + vertical_pos_increment
        self.SetSize((520, vertical_pos))
        self.SetTitle("PnodeChCfg")
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
