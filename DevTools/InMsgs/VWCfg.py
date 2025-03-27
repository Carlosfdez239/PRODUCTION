#!/usr/bin/env python3
import binascii
import os
import struct
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

            # Preset configurations
            configs = {
                "Default": {
                    "message_version": "1",
                    "voltage_threshold": "400",
                    "ch_enabled": [True, False, False, False, False, False],
                    "types": ["C", "C", "C", "C", "C", "C"],
                    "start_freq": "1400",
                    "end_freq": "3500",
                    "duration": "50",
                },
                "Default Test": {
                    "message_version": "1",
                    "voltage_threshold": "400",
                    "ch_enabled": [True, True, True, True, True, True],
                    "types": [
                        "Custom",
                        "Custom",
                        "Custom",
                        "Custom",
                        "Custom",
                        "Custom",
                    ],
                    "start_freq": "800",
                    "end_freq": "2000",
                    "duration": "100",
                },
                "30 minutes": {
                    "message_version": "1",
                    "voltage_threshold": "400",
                    "ch_enabled": [True, True, True, True, True, True],
                    "types": ["A", "A", "A", "A", "A", "A"],
                    "start_freq": "1000",
                    "end_freq": "2000",
                    "duration": "75",
                },
                "One Day": {
                    "message_version": "1",
                    "voltage_threshold": "400",
                    "ch_enabled": [True, True, True, True, True, True],
                    "types": ["A", "A", "A", "A", "A", "A"],
                    "start_freq": "1000",
                    "end_freq": "2000",
                    "duration": "75",
                },
            }

            if config in configs:
                cfg = configs[config]
                w_message_version.SetValue(cfg["message_version"])
                w_voltage_threshold.SetValue(cfg["voltage_threshold"])
                for i, chk in enumerate(
                    [
                        w_ch0_enabled,
                        w_ch1_enabled,
                        w_ch2_enabled,
                        w_ch3_enabled,
                        w_ch4_enabled,
                        w_ch5_enabled,
                    ]
                ):
                    chk.SetValue(cfg["ch_enabled"][i])
                for i, cbox in enumerate(
                    [
                        w_type_ch0,
                        w_type_ch1,
                        w_type_ch2,
                        w_type_ch3,
                        w_type_ch4,
                        w_type_ch5,
                    ]
                ):
                    cbox.SetValue(cfg["types"][i])
                w_custom_start_freq.SetValue(cfg["start_freq"])
                w_custom_end_freq.SetValue(cfg["end_freq"])
                w_custom_duration.SetValue(cfg["duration"])

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        def set_config(event):
            def w_type_to_int(w_type):
                if w_type == "A":
                    return 0
                if w_type == "B":
                    return 1
                if w_type == "C":
                    return 2
                if w_type == "D":
                    return 3
                if w_type == "Custom":
                    return 4

            try:
                message_version = int(w_message_version.GetValue())
                voltage_threshold = int(w_voltage_threshold.GetValue())
                enabled_channels_map = 0
                if w_ch0_enabled.GetValue():
                    enabled_channels_map |= 0x01
                if w_ch1_enabled.GetValue():
                    enabled_channels_map |= 0x02
                if w_ch2_enabled.GetValue():
                    enabled_channels_map |= 0x04
                if w_ch3_enabled.GetValue():
                    enabled_channels_map |= 0x08
                if w_ch4_enabled.GetValue():
                    enabled_channels_map |= 0x10
                if w_ch5_enabled.GetValue():
                    enabled_channels_map |= 0x20

                type_0 = w_type_to_int(w_type_ch0.GetValue())
                type_1 = w_type_to_int(w_type_ch1.GetValue())
                type_2 = w_type_to_int(w_type_ch2.GetValue())
                type_3 = w_type_to_int(w_type_ch3.GetValue())
                type_4 = w_type_to_int(w_type_ch4.GetValue())
                type_5 = w_type_to_int(w_type_ch5.GetValue())

                start_freq = int(w_custom_start_freq.GetValue())
                end_freq = int(w_custom_end_freq.GetValue())
                duration = int(w_custom_duration.GetValue())

            except ValueError as e:
                msgb = wx.MessageDialog(
                    self,
                    f"Some field is not an integer: {e}",
                    "ERROR",
                    wx.OK | wx.ICON_HAND,
                )
                msgb.ShowModal()
                return

            try:
                # Pack the values using struct
                packer = struct.Struct("!BHBBBBBBBHHH")
                packed_data = packer.pack(
                    message_version,  # 1 byte
                    voltage_threshold,  # 2 bytes
                    enabled_channels_map,  # 1 bytes
                    type_0,
                    type_1,
                    type_2,
                    type_3,
                    type_4,
                    type_5,  # 1 byte each
                    start_freq,  # 2 bytes
                    end_freq,  # 2 bytes
                    duration,  # 2 bytes
                )

                # Convert the packed data to hex format
                cmd = binascii.hexlify(packed_data).decode()
                cmd = "\\x" + "\\x".join(cmd[i : i + 2] for i in range(0, len(cmd), 2))

                send_command("\\x80" + cmd)

            except Exception as e:
                msgb = wx.MessageDialog(
                    self, f"Error packing data: {e}", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

        def set_custom_config(event):
            w_load_config.SetStringSelection("Custom")

        def send_command(command):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(command, tty_usb, self)

        # method to request the config
        def request_config(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(b"\\x00\\x80", tty_usb, self)

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Message Version", pos=(115, vertical_pos + 6))
        w_message_version = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_message_version.SetMaxLength(10)
        w_message_version.WriteText("1")
        w_message_version.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Voltage Threshold", pos=(115, vertical_pos + 6))
        w_voltage_threshold = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_voltage_threshold.SetMaxLength(10)
        w_voltage_threshold.WriteText("400")
        w_voltage_threshold.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        horizontal_pos_increment = 50
        w_ch0_enabled = wx.CheckBox(
            pnl, label="Ch0", pos=(20 + horizontal_pos_increment * 0, vertical_pos)
        )
        w_ch0_enabled.SetValue(True)
        w_ch0_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_ch1_enabled = wx.CheckBox(
            pnl, label="Ch1", pos=(20 + horizontal_pos_increment * 1, vertical_pos)
        )
        w_ch1_enabled.SetValue(True)
        w_ch1_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_ch2_enabled = wx.CheckBox(
            pnl, label="Ch2", pos=(20 + horizontal_pos_increment * 2, vertical_pos)
        )
        w_ch2_enabled.SetValue(True)
        w_ch2_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment
        w_ch3_enabled = wx.CheckBox(
            pnl, label="Ch3", pos=(20 + horizontal_pos_increment * 0, vertical_pos)
        )
        w_ch3_enabled.SetValue(True)
        w_ch3_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_ch4_enabled = wx.CheckBox(
            pnl, label="Ch4", pos=(20 + horizontal_pos_increment * 1, vertical_pos)
        )
        w_ch4_enabled.SetValue(True)
        w_ch4_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_ch5_enabled = wx.CheckBox(
            pnl, label="Ch5", pos=(20 + horizontal_pos_increment * 2, vertical_pos)
        )
        w_ch5_enabled.SetValue(True)
        w_ch5_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        sweep_type_list = ["A", "B", "C", "D", "Custom"]
        wx.StaticText(pnl, label="Sweep Type Ch 0", pos=(115, vertical_pos + 6))
        w_type_ch0 = wx.ComboBox(
            pnl,
            500,
            value="9",
            size=(90, 30),
            pos=(20, vertical_pos),
            choices=sweep_type_list,
        )
        w_type_ch0.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Sweep Type Ch 1", pos=(115, vertical_pos + 6))
        w_type_ch1 = wx.ComboBox(
            pnl,
            500,
            value="9",
            size=(90, 30),
            pos=(20, vertical_pos),
            choices=sweep_type_list,
        )
        w_type_ch1.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Sweep Type Ch 2", pos=(115, vertical_pos + 6))
        w_type_ch2 = wx.ComboBox(
            pnl,
            500,
            value="9",
            size=(90, 30),
            pos=(20, vertical_pos),
            choices=sweep_type_list,
        )
        w_type_ch2.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Sweep Type Ch 3", pos=(115, vertical_pos + 6))
        w_type_ch3 = wx.ComboBox(
            pnl,
            500,
            value="9",
            size=(90, 30),
            pos=(20, vertical_pos),
            choices=sweep_type_list,
        )
        w_type_ch3.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Sweep Type Ch 4", pos=(115, vertical_pos + 6))
        w_type_ch4 = wx.ComboBox(
            pnl,
            500,
            value="9",
            size=(90, 30),
            pos=(20, vertical_pos),
            choices=sweep_type_list,
        )
        w_type_ch4.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Sweep Type Ch 5", pos=(115, vertical_pos + 6))
        w_type_ch5 = wx.ComboBox(
            pnl,
            500,
            value="9",
            size=(90, 30),
            pos=(20, vertical_pos),
            choices=sweep_type_list,
        )
        w_type_ch5.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Custom Start Freq", pos=(115, vertical_pos + 6))
        w_custom_start_freq = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_custom_start_freq.SetMaxLength(10)
        w_custom_start_freq.WriteText("1800")
        w_custom_start_freq.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Custom End Freq", pos=(115, vertical_pos + 6))
        w_custom_end_freq = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_custom_end_freq.SetMaxLength(10)
        w_custom_end_freq.WriteText("2000")
        w_custom_end_freq.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Custom Duration", pos=(115, vertical_pos + 6))
        w_custom_duration = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_custom_duration.SetMaxLength(10)
        w_custom_duration.WriteText("100")
        w_custom_duration.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(260, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        w_set_config_btn = wx.Button(pnl, label="Request Config", pos=(350, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_config)

        configs_list = ["Custom", "Default", "Default Test", "30 minutes", "One Day"]
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

        self.SetSize((470, vertical_pos + vertical_pos_increment))
        self.SetTitle("VWCfg")
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
