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
                w_data_wait_time.SetValue("0")
                w_num_sensors.SetValue("0")
                w_sensors_ids.SetValue("")
                w_ch_x_enabled.SetValue(True)
                w_ch_y_enabled.SetValue(True)
                w_ch_z_enabled.SetValue(False)
                w_sensor_models.SetValue(sensor_models[0])

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        # method to set the config
        def set_config(event):

            try:
                num_sensors = int(w_num_sensors.GetValue())

                enabled_channels_map = 0x00
                if w_ch_x_enabled.GetValue():
                    enabled_channels_map = enabled_channels_map | 0x04
                if w_ch_y_enabled.GetValue():
                    enabled_channels_map = enabled_channels_map | 0x02
                if w_ch_z_enabled.GetValue():
                    enabled_channels_map = enabled_channels_map | 0x01

                data_wait_time = int(w_data_wait_time.GetValue())

                if data_wait_time > (1 << 16) - 1:
                    msgb = wx.MessageDialog(
                        self, "Data wait time max value is 65535ms", "ERROR", wx.OK | wx.ICON_HAND
                    )
                    msgb.ShowModal()
                    return
            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            try:
                ids_sensors = w_sensors_ids.GetValue().split()
                if len(ids_sensors) != num_sensors:
                    msgb = wx.MessageDialog(
                        self,
                        "Number of ids is different from number of sensors reported",
                        "ERROR",
                        wx.OK | wx.ICON_HAND,
                    )
                    msgb.ShowModal()
                    return

                for sid in ids_sensors:
                    if int(sid) > ((1 << 12) - 1):
                        msgb = wx.MessageDialog(
                            self, "Max sensor id value is 4095", "ERROR", wx.OK | wx.ICON_HAND
                        )
                        msgb.ShowModal()
                        return

            except:
                msgb = wx.MessageDialog(self, "Could not parse ids", "ERROR", wx.OK | wx.ICON_HAND)
                msgb.ShowModal()
                return

            try:
                type_of_sensor = 4
                config_version = 0

                output = (
                    "\\x91"
                    + "\\x%0.2X" % type_of_sensor
                    + "\\x%0.2X" % config_version
                    + "\\x%0.2X" % num_sensors
                )

                output += "\\x%0.2X" % (
                    sensor_models.index(w_sensor_models.GetValue()) << 5 | enabled_channels_map
                )

                data_wait_hexa = "{number:0{size}x}".format(number=data_wait_time, size=4)
                output += "\\x" + data_wait_hexa[0:2] + "\\x" + data_wait_hexa[2:4]

                if num_sensors > 0:
                    temp_output_ids = ""
                    for sid in ids_sensors:
                        temp_output_ids += "%0.3X" % int(sid)

                    # If the number of sensors is odd, write one extra hexa digit of padding
                    if len(ids_sensors) % 2 != 0:
                        temp_output_ids += "0"

                    # Finally format the final result
                    for i in range(len(temp_output_ids)):
                        if i % 2 == 0:
                            output += "\\x" + temp_output_ids[i : i + 2]

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

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Data wait time (ms)", pos=(115, vertical_pos + 6))
        w_data_wait_time = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_data_wait_time.SetMaxLength(5)
        w_data_wait_time.WriteText("0")
        w_data_wait_time.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        num_sensors_list = [
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
        wx.StaticText(pnl, label="Num of sensors", pos=(115, vertical_pos + 6))
        w_num_sensors = wx.ComboBox(
            pnl, 500, value="1", size=(90, 30), pos=(20, vertical_pos), choices=num_sensors_list
        )
        w_num_sensors.Bind(wx.EVT_TEXT, set_custom_config)

        horizontal_pos_increment = 60
        w_ch_x_enabled = wx.CheckBox(
            pnl, label="ChX", pos=(250 + horizontal_pos_increment * 0, vertical_pos + 5)
        )
        w_ch_x_enabled.SetValue(True)
        w_ch_x_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_ch_y_enabled = wx.CheckBox(
            pnl, label="ChY", pos=(250 + horizontal_pos_increment * 1, vertical_pos + 5)
        )
        w_ch_y_enabled.SetValue(True)
        w_ch_y_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_ch_z_enabled = wx.CheckBox(
            pnl, label="ChZ", pos=(250 + horizontal_pos_increment * 2, vertical_pos + 5)
        )
        w_ch_z_enabled.SetValue(False)
        w_ch_z_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        sensor_models = [
            "DGSI - Geoflex",
            "Soil instruments - GEOSmart",
            "Roctest - Geostring",
            "Soil instruments - Smart IPI",
        ]
        wx.StaticText(pnl, label="Sensor Manufacturer/Model", pos=(230, vertical_pos + 5))
        w_sensor_models = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(20, vertical_pos),
            choices=sensor_models,
            style=wx.CB_READONLY,
        )
        vertical_pos += 30

        wx.StaticText(pnl, label="Sensors Ids", pos=(20, vertical_pos + 6))
        vertical_pos = vertical_pos + vertical_pos_increment
        w_sensors_ids = wx.TextCtrl(
            pnl,
            -1,
            size=(400, 30 + 2 * vertical_pos_increment),
            pos=(20, vertical_pos),
            style=wx.TE_MULTILINE,
        )
        w_sensors_ids.WriteText("1")
        w_sensors_ids.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + 3 * vertical_pos_increment

        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(260, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        w_set_config_btn = wx.Button(pnl, label="Request Config", pos=(350, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_config)

        configs_list = ["Custom", "Default"]
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

        self.SetSize((470, vertical_pos + (vertical_pos_increment * 3)))
        self.SetTitle("GeoflexChCfg")
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
