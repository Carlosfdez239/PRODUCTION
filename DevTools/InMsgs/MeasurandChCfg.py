#!/usr/bin/env python3
#
# file:     MeasurandChCfg.py
#
# brief:    Python tool used to create and send the Measurand configuration message to the Digital Node.
#
# author:   Worldsensing
#
# license:  (C) Copyright 2020 Worldsensing, http://www.worldsensing.com
#
import os
import sys

import wx
from ls_utils import ls_send_message_uart

ProtocolsList = ["Regular", "Low Power"]
MaxSegments = {
    "Original": 100,
    "Extended": 200,
}
AbsoluteMaxSegments = {
    "Original": 127,
    "Extended": 255,
}
TypeOfSensor = {
    "Original": 6,
    "Extended": 8,
}
CfgTypeList = ["Original", "Extended"]
configs_list = ["Custom", "Default", "Max Segments"]
tty_prefix = "/dev/ttyUSB"


class MeasurandChCfg(wx.Frame):
    def __init__(self, *args, **kw):
        super(MeasurandChCfg, self).__init__(*args, **kw)
        self.init_ui()

    # Function used to set up the fields in the UI when the tool starts
    #
    # @param event: Needed to allow the wx library to call this function when the user interacts with the UI
    #
    def load_config(self, event):
        config = self.w_load_config.GetValue()

        if config == "Default":
            self.w_num_segments.SetValue("0")
            # update on textctrls change the drop down to custom, change it back
            self.w_load_config.SetStringSelection(config)
            self.w_protocol.SetValue(ProtocolsList[0])
            self.w_type.SetValue(CfgTypeList[0])

        if config == "Max Segments":
            self.w_num_segments.SetValue(str(MaxSegments[self.w_type.GetValue()]))
            # update on textctrls change the drop down to custom, change it back
            self.w_load_config.SetStringSelection(config)

    # This function checks the input values from de UI and then creates the message needed to send the
    # configuration to the node
    #
    # @param event: Needed to allow the wx library to call this function when the user interacts with the UI
    #
    def set_config(self, event):

        try:
            num_segments = int(self.w_num_segments.GetValue())

        except:
            msgb = wx.MessageDialog(
                self, "Number of segments is not an integer", "ERROR", wx.OK | wx.ICON_HAND
            )
            msgb.ShowModal()
            self.w_num_segments.SetValue("0")
            return

        try:
            cfg = self.w_type.GetValue()
            if (
                cfg not in CfgTypeList
                or cfg not in MaxSegments.keys()
                or cfg not in TypeOfSensor.keys()
            ):
                msgb = wx.MessageDialog(
                    self,
                    "Unknown configuration type",
                    "ERROR",
                    wx.OK | wx.ICON_HAND,
                )
                msgb.ShowModal()
                self.w_type.SetValue(CfgTypeList[0])
                return
        except:
            msgb = wx.MessageDialog(
                self, "Error getting the config type", "ERROR", wx.OK | wx.ICON_HAND
            )
            msgb.ShowModal()
            self.w_protocol.SetValue(ProtocolsList[0])
            return

        if num_segments > AbsoluteMaxSegments[cfg]:
            s = "The number of sensors is greater than the maximum configurable value.\n"
            s += "The max is 127 for the Original cfg and 255 for the Extended."
            msgb = wx.MessageDialog(
                self,
                s,
                "ERROR",
                wx.OK | wx.ICON_HAND,
            )
            msgb.ShowModal()
            self.w_num_segments.SetValue("0")
            return
        elif num_segments > MaxSegments[cfg]:
            s = "The number of sensors is greater than the maximum allowed.\n"
            s += "The max is 100 for the Original cfg and 200 for the Extended."
            msgb = wx.MessageDialog(
                self,
                s,
                "WARNING",
                wx.OK | wx.ICON_HAND,
            )
            msgb.ShowModal()

        protocol = self.w_protocol.GetValue()

        try:
            if protocol not in ProtocolsList:
                msgb = wx.MessageDialog(self, "Unknown protocol", "ERROR", wx.OK | wx.ICON_HAND)
                msgb.ShowModal()
                self.w_protocol.SetValue(ProtocolsList[0])
                return

            num_protocol = int(ProtocolsList.index(protocol))

        except:
            msgb = wx.MessageDialog(
                self, "Error getting the protocol", "ERROR", wx.OK | wx.ICON_HAND
            )
            msgb.ShowModal()
            self.w_protocol.SetValue(ProtocolsList[0])
            return

        try:
            type_of_sensor = TypeOfSensor[cfg]
            config_version = 0

            print(type_of_sensor)
            output = "\\x91" + "\\x%0.2X" % type_of_sensor + "\\x%0.2X" % config_version

            output += "\\x%0.2X" % num_protocol + "\\x%0.2X" % num_segments

        except:
            msgb = wx.MessageDialog(self, "Error creating message", "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()
            return

        tty_usb = tty_prefix + self.w_tty_usb.GetValue()
        ls_send_message_uart(output, tty_usb, self)

    # This function sends a command to the node to request the actual configuration
    #
    # @param event: Needed to allow the wx library to call this function when the user interacts with the UI
    #
    def request_config(self, event):
        tty_usb = tty_prefix + self.w_tty_usb.GetValue()
        ls_send_message_uart("\\x00\\x91", tty_usb, self)

    # Function called when a field in the UI is changed
    #
    # @param event: Nedded to allow the wx library to call this function when the user interacts with the UI
    #
    def set_custom_config(self, event):
        self.w_load_config.SetStringSelection("Custom")

    # This function defines all the fields that are in the UI (Buttons, Dropdowns, Text fields) in order to
    # display all the elements correctly
    #
    def init_ui(self):

        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        self.w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        self.w_tty_usb.SetMaxLength(10)
        self.w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Cfg Type", pos=(155, vertical_pos + 6))
        self.w_type = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(130, 30),
            pos=(20, vertical_pos),
            choices=CfgTypeList,
            style=wx.CB_READONLY,
        )
        self.w_type.Bind(wx.EVT_TEXT, self.set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Protocol", pos=(155, vertical_pos + 6))
        self.w_protocol = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(130, 30),
            pos=(20, vertical_pos),
            choices=ProtocolsList,
            style=wx.CB_READONLY,
        )
        self.w_protocol.Bind(wx.EVT_TEXT, self.set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Num of segments", pos=(115, vertical_pos + 6))
        self.w_num_segments = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        self.w_num_segments.Bind(wx.EVT_TEXT, self.set_custom_config)

        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(250, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, self.set_config)

        w_set_config_btn = wx.Button(pnl, label="Req. Config", pos=(360, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, self.request_config)

        wx.StaticText(pnl, label="Load preset configs", pos=(250, 20))
        self.w_load_config = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(250, 20 + vertical_pos_increment - 10),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        self.w_load_config.Bind(wx.EVT_COMBOBOX, self.load_config)
        self.w_load_config.SetStringSelection("Default")
        self.load_config(None)

        self.SetSize((490, vertical_pos + (vertical_pos_increment * 3)))
        self.SetTitle("MeasurandChCfg")
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
        global_tty = tty_prefix + "0"  # Use default tty
    else:
        print("Usage" + os.path.basename(__file__) + " [serial_tty] [-s IP]")
        sys.exit(1)

    ex = wx.App()
    MeasurandChCfg(None)
    ex.MainLoop()


if __name__ == "__main__":
    main()
