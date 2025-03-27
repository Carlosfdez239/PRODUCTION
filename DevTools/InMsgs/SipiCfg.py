#!/usr/bin/env python
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

            if config == "Default Uniaxial":
                w_enabled.SetValue(True)
                w_number_sensors.SetValue("1")
                w_type_sensors.SetValue("Uniaxial")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Default Biaxial":
                w_enabled.SetValue(True)
                w_number_sensors.SetValue("1")
                w_type_sensors.SetValue("Biaxial")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        # method to set the config

        def set_config(event):
            def w_type_sensors_to_int(w_type):
                if w_type == "Uniaxial":
                    return 0
                if w_type == "Biaxial":
                    return 1
                else:
                    return 255

            try:
                enabled = int(w_enabled.GetValue())
                number_sensors = int(w_number_sensors.GetValue())
                type_sensors = w_type_sensors_to_int(w_type_sensors.GetValue())

            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            sipi_mode = 1 << 5
            output = "\\x8f"
            output += "\\x%02X" % (sipi_mode | enabled)
            output += "\\x%02X" % number_sensors
            output += "\\x%02X" % type_sensors

            ls_send_message_uart(output, global_tty, self)

        # method to request the config
        def request_config(event):
            ls_send_message_uart("\\x00\\x8f", global_tty, self)

        def set_custom_config(event):
            w_load_config.SetStringSelection("Custom")

        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)
        type_sensor_list = ["Uniaxial", "Biaxial"]

        wx.StaticText(pnl, label="Enabled", pos=(20, vertical_pos))
        wx.StaticText(pnl, label="Number of sensors", pos=(100, vertical_pos))
        wx.StaticText(pnl, label="Type of sensors", pos=(240, vertical_pos))
        vertical_pos += vertical_pos_increment // 2
        w_enabled = wx.CheckBox(pnl, label="", pos=(20, vertical_pos))
        w_enabled.SetValue(True)
        w_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)

        sensors_range_list = [
            "0",
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
        ]
        w_number_sensors = wx.ComboBox(
            pnl, 500, size=(100, 30), pos=(100, vertical_pos), choices=sensors_range_list
        )
        w_number_sensors.SetValue("1")
        w_number_sensors.Bind(wx.EVT_TEXT, set_custom_config)

        w_type_sensors = wx.ComboBox(
            pnl, 500, value="0V", size=(120, 30), pos=(240, vertical_pos), choices=type_sensor_list
        )
        w_type_sensors.SetValue("Biaxial")
        w_type_sensors.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        vertical_pos = vertical_pos + vertical_pos_increment // 2
        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(400, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        w_set_config_btn = wx.Button(pnl, label="Request Config", pos=(400 + 90, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_config)

        configs_list = ["Default Uniaxial", "Default Biaxial", "Custom"]
        wx.StaticText(pnl, label="Load preset configs", pos=(380, 20))
        w_load_config = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(380, 20 + vertical_pos_increment // 2),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_load_config.Bind(wx.EVT_COMBOBOX, load_config)
        w_load_config.SetStringSelection("Default Biaxial")
        load_config(0)

        self.SetSize((620, vertical_pos + 100))
        self.SetTitle("SipiCfg")
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
