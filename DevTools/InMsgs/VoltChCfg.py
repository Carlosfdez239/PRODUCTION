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
                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(False)
                w_ch3_enabled.SetValue(False)

                w_output_power_ch0.SetValue("0V")
                w_output_power_ch1.SetValue("0V")
                w_output_power_ch2.SetValue("0V")
                w_output_power_ch3.SetValue("0V")

                w_input_type_ch0.SetValue("Voltage")
                w_input_type_ch1.SetValue("Voltage")
                w_input_type_ch2.SetValue("Voltage")
                w_input_type_ch3.SetValue("Voltage")

                w_warmup_time_ch0.SetValue("0")
                w_warmup_time_ch1.SetValue("0")
                w_warmup_time_ch2.SetValue("0")
                w_warmup_time_ch3.SetValue("0")

                w_warmup_units_ch0.SetValue("ms")
                w_warmup_units_ch1.SetValue("ms")
                w_warmup_units_ch2.SetValue("ms")
                w_warmup_units_ch3.SetValue("ms")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Default Test":
                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)

                w_output_power_ch0.SetValue("0V")
                w_output_power_ch1.SetValue("0V")
                w_output_power_ch2.SetValue("0V")
                w_output_power_ch3.SetValue("0V")

                w_input_type_ch0.SetValue("Current")
                w_input_type_ch1.SetValue("Current")
                w_input_type_ch2.SetValue("Current")
                w_input_type_ch3.SetValue("Current")

                w_warmup_time_ch0.SetValue("0")
                w_warmup_time_ch1.SetValue("0")
                w_warmup_time_ch2.SetValue("0")
                w_warmup_time_ch3.SetValue("0")

                w_warmup_units_ch0.SetValue("ms")
                w_warmup_units_ch1.SetValue("ms")
                w_warmup_units_ch2.SetValue("ms")
                w_warmup_units_ch3.SetValue("ms")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Warmup Test":
                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(False)
                w_ch2_enabled.SetValue(False)
                w_ch3_enabled.SetValue(False)

                w_input_type_ch0.SetValue("Potentiometer")
                w_input_type_ch1.SetValue("Potentiometer")
                w_input_type_ch2.SetValue("Potentiometer")
                w_input_type_ch3.SetValue("Potentiometer")

                w_output_power_ch0.SetValue("0V")
                w_output_power_ch1.SetValue("0V")
                w_output_power_ch2.SetValue("0V")
                w_output_power_ch3.SetValue("0V")

                w_warmup_time_ch0.SetValue("3000")
                w_warmup_time_ch1.SetValue("3000")
                w_warmup_time_ch2.SetValue("3000")
                w_warmup_time_ch3.SetValue("3000")

                w_warmup_units_ch0.SetValue("ms")
                w_warmup_units_ch1.SetValue("ms")
                w_warmup_units_ch2.SetValue("ms")
                w_warmup_units_ch3.SetValue("ms")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Passive Sensors Test":
                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)

                w_input_type_ch0.SetValue("Potentiometer")
                w_input_type_ch1.SetValue("Thermistor")
                w_input_type_ch2.SetValue("Gauge")
                w_input_type_ch3.SetValue("PTC")

                w_output_power_ch0.SetValue("0V")
                w_output_power_ch1.SetValue("0V")
                w_output_power_ch2.SetValue("0V")
                w_output_power_ch3.SetValue("0V")

                w_warmup_time_ch0.SetValue("0")
                w_warmup_time_ch1.SetValue("0")
                w_warmup_time_ch2.SetValue("0")
                w_warmup_time_ch3.SetValue("0")

                w_warmup_units_ch0.SetValue("ms")
                w_warmup_units_ch1.SetValue("ms")
                w_warmup_units_ch2.SetValue("ms")
                w_warmup_units_ch3.SetValue("ms")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Current Sensors Test":
                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(False)
                w_ch2_enabled.SetValue(False)
                w_ch3_enabled.SetValue(False)

                w_input_type_ch0.SetValue("Current")
                w_input_type_ch1.SetValue("Current")
                w_input_type_ch2.SetValue("Current")
                w_input_type_ch3.SetValue("Current")

                w_output_power_ch0.SetValue("12V")
                w_output_power_ch1.SetValue("12V")
                w_output_power_ch2.SetValue("12V")
                w_output_power_ch3.SetValue("12V")

                w_warmup_time_ch0.SetValue("50")
                w_warmup_time_ch1.SetValue("50")
                w_warmup_time_ch2.SetValue("50")
                w_warmup_time_ch3.SetValue("50")

                w_warmup_units_ch0.SetValue("ms")
                w_warmup_units_ch1.SetValue("ms")
                w_warmup_units_ch2.SetValue("ms")
                w_warmup_units_ch3.SetValue("ms")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Voltage Sensors Test":
                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(False)
                w_ch2_enabled.SetValue(False)
                w_ch3_enabled.SetValue(False)

                w_input_type_ch0.SetValue("Voltage")
                w_input_type_ch1.SetValue("Voltage")
                w_input_type_ch2.SetValue("Voltage")
                w_input_type_ch3.SetValue("Voltage")

                w_output_power_ch0.SetValue("12V")
                w_output_power_ch1.SetValue("12V")
                w_output_power_ch2.SetValue("12V")
                w_output_power_ch3.SetValue("12V")

                w_warmup_time_ch0.SetValue("50")
                w_warmup_time_ch1.SetValue("50")
                w_warmup_time_ch2.SetValue("50")
                w_warmup_time_ch3.SetValue("50")

                w_warmup_units_ch0.SetValue("ms")
                w_warmup_units_ch1.SetValue("ms")
                w_warmup_units_ch2.SetValue("ms")
                w_warmup_units_ch3.SetValue("ms")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        # method to set the config
        def set_config(event):
            def w_out_pow_to_int(w_type):
                if w_type == "0V":
                    return 0
                if w_type == "12V":
                    return 1
                if w_type == "24V":
                    return 2
                else:
                    return 255

            def w_in_type_to_int(w_type):
                if w_type == "Voltage":
                    return 0
                if w_type == "Gauge":
                    return 1
                if w_type == "Thermistor":
                    return 2
                if w_type == "Current":
                    return 3
                if w_type == "PTC":
                    return 4
                if w_type == "Potentiometer":
                    return 5
                if w_type == "Volt4V5":
                    return 6
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
                if w_ch3_enabled.GetValue():
                    enabled_channels_map = enabled_channels_map | 0x08

                input_type_0 = w_in_type_to_int(w_input_type_ch0.GetValue())
                input_type_1 = w_in_type_to_int(w_input_type_ch1.GetValue())
                input_type_2 = w_in_type_to_int(w_input_type_ch2.GetValue())
                input_type_3 = w_in_type_to_int(w_input_type_ch3.GetValue())

                output_power_0 = w_out_pow_to_int(w_output_power_ch0.GetValue())
                output_power_1 = w_out_pow_to_int(w_output_power_ch1.GetValue())
                output_power_2 = w_out_pow_to_int(w_output_power_ch2.GetValue())
                output_power_3 = w_out_pow_to_int(w_output_power_ch3.GetValue())

                warmup_time_0 = int(w_warmup_time_ch0.GetValue())
                warmup_time_1 = int(w_warmup_time_ch1.GetValue())
                warmup_time_2 = int(w_warmup_time_ch2.GetValue())
                warmup_time_3 = int(w_warmup_time_ch3.GetValue())

                warmup_units_0 = w_warmup_units_ch0.GetValue()
                warmup_units_1 = w_warmup_units_ch1.GetValue()
                warmup_units_2 = w_warmup_units_ch2.GetValue()
                warmup_units_3 = w_warmup_units_ch3.GetValue()

            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            warmup_units_mask = 0xFE00
            if warmup_units_0 == "s":
                warmup_time_0 = warmup_time_0 | warmup_units_mask
            if warmup_units_1 == "s":
                warmup_time_1 = warmup_time_1 | warmup_units_mask
            if warmup_units_2 == "s":
                warmup_time_2 = warmup_time_2 | warmup_units_mask
            if warmup_units_3 == "s":
                warmup_time_3 = warmup_time_3 | warmup_units_mask

            volt_mode = 0 << 5
            output = "\\x8f"
            output += "\\x%02X" % (volt_mode | enabled_channels_map)
            output += "\\x%02X" % input_type_0
            output += "\\x%02X" % output_power_0
            output += "\\x%02X" % (warmup_time_0 >> 8) + "\\x%02X" % (warmup_time_0 & 0x00FF)
            output += "\\x%02X" % input_type_1
            output += "\\x%02X" % output_power_1
            output += "\\x%02X" % (warmup_time_1 >> 8) + "\\x%02X" % (warmup_time_1 & 0x00FF)
            output += "\\x%02X" % input_type_2
            output += "\\x%02X" % output_power_2
            output += "\\x%02X" % (warmup_time_2 >> 8) + "\\x%02X" % (warmup_time_2 & 0x00FF)
            output += "\\x%02X" % input_type_3
            output += "\\x%02X" % output_power_3
            output += "\\x%02X" % (warmup_time_3 >> 8) + "\\x%02X" % (warmup_time_3 & 0x00FF)
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(output, tty_usb, self)

        # method to request the config
        def request_config(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x00\\x8f", tty_usb, self)

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
        vertical_pos = vertical_pos + 2 * vertical_pos_increment

        input_type_list = [
            "Voltage",
            "Gauge",
            "Thermistor",
            "Current",
            "PTC",
            "Potentiometer",
            "Volt4V5",
        ]
        output_power_list = ["0V", "12V", "24V"]
        warmup_units_list = ["s", "ms"]

        wx.StaticText(pnl, label="Enabled", pos=(20, vertical_pos))
        wx.StaticText(pnl, label="Input Type", pos=(100, vertical_pos))
        wx.StaticText(pnl, label="Output Power", pos=(200, vertical_pos))
        wx.StaticText(pnl, label="Warmup Time", pos=(300, vertical_pos))
        wx.StaticText(pnl, label="Warmup Units", pos=(400, vertical_pos))
        vertical_pos += vertical_pos_increment // 2

        w_ch0_enabled = wx.CheckBox(pnl, label="Ch0", pos=(20, vertical_pos))
        w_ch0_enabled.SetValue(True)
        w_ch0_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_input_type_ch0 = wx.ComboBox(
            pnl,
            500,
            value="Voltage",
            size=(90, 30),
            pos=(100, vertical_pos),
            choices=input_type_list,
        )
        w_input_type_ch0.Bind(wx.EVT_TEXT, set_custom_config)
        w_output_power_ch0 = wx.ComboBox(
            pnl, 500, value="0V", size=(90, 30), pos=(200, vertical_pos), choices=output_power_list
        )
        w_output_power_ch0.Bind(wx.EVT_TEXT, set_custom_config)
        w_warmup_time_ch0 = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(300, vertical_pos))
        w_warmup_time_ch0.SetMaxLength(10)
        w_warmup_time_ch0.WriteText("240")
        w_warmup_time_ch0.Bind(wx.EVT_TEXT, set_custom_config)
        w_warmup_units_ch0 = wx.ComboBox(
            pnl, 500, value="ms", size=(90, 30), pos=(400, vertical_pos), choices=warmup_units_list
        )
        w_warmup_units_ch0.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        w_ch1_enabled = wx.CheckBox(pnl, label="Ch1", pos=(20, vertical_pos))
        w_ch1_enabled.SetValue(True)
        w_ch1_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_input_type_ch1 = wx.ComboBox(
            pnl,
            500,
            value="Voltage",
            size=(90, 30),
            pos=(100, vertical_pos),
            choices=input_type_list,
        )
        w_input_type_ch1.Bind(wx.EVT_TEXT, set_custom_config)
        w_output_power_ch1 = wx.ComboBox(
            pnl, 500, value="0V", size=(90, 30), pos=(200, vertical_pos), choices=output_power_list
        )
        w_output_power_ch1.Bind(wx.EVT_TEXT, set_custom_config)
        w_warmup_time_ch1 = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(300, vertical_pos))
        w_warmup_time_ch1.SetMaxLength(10)
        w_warmup_time_ch1.WriteText("240")
        w_warmup_time_ch1.Bind(wx.EVT_TEXT, set_custom_config)
        w_warmup_units_ch1 = wx.ComboBox(
            pnl, 500, value="ms", size=(90, 30), pos=(400, vertical_pos), choices=warmup_units_list
        )
        w_warmup_units_ch1.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        w_ch2_enabled = wx.CheckBox(pnl, label="Ch2", pos=(20, vertical_pos))
        w_ch2_enabled.SetValue(True)
        w_ch2_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_input_type_ch2 = wx.ComboBox(
            pnl,
            500,
            value="Voltage",
            size=(90, 30),
            pos=(100, vertical_pos),
            choices=input_type_list,
        )
        w_input_type_ch2.Bind(wx.EVT_TEXT, set_custom_config)
        w_output_power_ch2 = wx.ComboBox(
            pnl, 500, value="0V", size=(90, 30), pos=(200, vertical_pos), choices=output_power_list
        )
        w_output_power_ch2.Bind(wx.EVT_TEXT, set_custom_config)
        w_warmup_time_ch2 = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(300, vertical_pos))
        w_warmup_time_ch2.SetMaxLength(10)
        w_warmup_time_ch2.WriteText("240")
        w_warmup_time_ch2.Bind(wx.EVT_TEXT, set_custom_config)
        w_warmup_units_ch2 = wx.ComboBox(
            pnl, 500, value="ms", size=(90, 30), pos=(400, vertical_pos), choices=warmup_units_list
        )
        w_warmup_units_ch2.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        w_ch3_enabled = wx.CheckBox(pnl, label="Ch3", pos=(20, vertical_pos))
        w_ch3_enabled.SetValue(True)
        w_input_type_ch3 = wx.ComboBox(
            pnl,
            500,
            value="Voltage",
            size=(90, 30),
            pos=(100, vertical_pos),
            choices=input_type_list,
        )
        w_input_type_ch3.Bind(wx.EVT_TEXT, set_custom_config)
        w_output_power_ch3 = wx.ComboBox(
            pnl, 500, value="0V", size=(90, 30), pos=(200, vertical_pos), choices=output_power_list
        )
        w_output_power_ch3.Bind(wx.EVT_TEXT, set_custom_config)
        w_warmup_time_ch3 = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(300, vertical_pos))
        w_warmup_time_ch3.SetMaxLength(10)
        w_warmup_time_ch3.WriteText("240")
        w_warmup_time_ch3.Bind(wx.EVT_TEXT, set_custom_config)
        w_warmup_units_ch3 = wx.ComboBox(
            pnl, 500, value="ms", size=(90, 30), pos=(400, vertical_pos), choices=warmup_units_list
        )
        w_warmup_units_ch3.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        vertical_pos = vertical_pos + vertical_pos_increment // 2
        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(400, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        w_set_config_btn = wx.Button(pnl, label="Request Config", pos=(400 + 90, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_config)

        configs_list = [
            "Custom",
            "Default Test",
            "Warmup Test",
            "Passive Sensors Test",
            "Current Sensors Test",
            "Voltage Sensors Test",
        ]
        wx.StaticText(pnl, label="Load preset configs", pos=(400, 20))
        w_load_config = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(400, 20 + vertical_pos_increment // 2),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_load_config.Bind(wx.EVT_COMBOBOX, load_config)
        w_load_config.SetStringSelection("Default Test")
        load_config(0)

        vertical_pos = vertical_pos + 2 * vertical_pos_increment
        self.SetSize((620, vertical_pos))
        self.SetTitle("VoltChCfg")
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
