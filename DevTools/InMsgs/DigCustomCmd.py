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
                w_command.SetValue("255")
                w_type_sensors.SetValue("GeoFlex")
            elif config == "GeoFlex - Autosetup Addr":
                w_command.SetValue("0")
                w_type_sensors.SetValue("GeoFlex")

            # update on textctrls change the drop down to custom, change it back
            w_load_config.SetStringSelection(config)

        # method to set the config
        def send_command(event):
            def w_type_sensors_to_int(w_type):
                if w_type == "GSI":
                    return 0
                elif w_type == "Sisgeo Legacy":
                    return 1
                elif w_type == "MDT":
                    return 2
                elif w_type == "Sisgeo V3":
                    return 3
                elif w_type == "GeoFlex":
                    return 4
                elif w_type == "Original Measurand":
                    return 6
                elif w_type == "Extended Measurand":
                    return 8
                else:
                    return 255

            try:
                command = int(w_command.GetValue())
                dig_subtype = w_type_sensors_to_int(w_type_sensors.GetValue())

            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            try:
                output = "\\x10" + "\\x%0.2X" % dig_subtype + "\\x%0.2X" % command

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

        dig_types_list = [
            "GSI",
            "Sisgeo Legacy",
            "MDT",
            "Sisgeo V3",
            "GeoFlex",
            "Original Measurand",
            "Extended Measurand",
        ]
        wx.StaticText(pnl, label="Digital subtype", pos=(170, vertical_pos + 6))
        w_type_sensors = wx.ComboBox(
            pnl, 500, value="1", size=(150, 30), pos=(20, vertical_pos), choices=dig_types_list
        )
        w_type_sensors.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Command code", pos=(115, vertical_pos + 6))
        w_command = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_command.SetMaxLength(5)
        w_command.WriteText("0")
        w_command.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_send_cmd = wx.Button(
            pnl, label="Send Command", size=(120, 30), pos=(500 - (120 + 6), vertical_pos)
        )
        w_send_cmd.Bind(wx.EVT_BUTTON, send_command)

        configs_list = ["Custom", "Default", "GeoFlex - Autosetup Addr"]
        wx.StaticText(pnl, label="Load preset configs", pos=(300, 20 + 6))
        w_load_config = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(500 - (200 + 6), 20 + 6 + vertical_pos_increment - 10),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_load_config.Bind(wx.EVT_COMBOBOX, load_config)
        w_load_config.SetStringSelection("Default")
        load_config(0)

        self.SetSize((500, vertical_pos + (vertical_pos_increment * 2) + 6))
        self.SetTitle("DigCustomCommands")
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
