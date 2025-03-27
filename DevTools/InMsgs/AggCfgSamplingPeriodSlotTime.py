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

            if config == "SP 15":
                w_sampling_period.SetValue("15")
                w_slot_time.SetValue("10")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "SP 300":
                w_sampling_period.SetValue("300")
                w_slot_time.SetValue("240")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "SP 30 minutes":
                w_sampling_period.SetValue("1800")
                w_slot_time.SetValue("300")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        # method to set the config
        def set_config(event):
            try:
                sampling_period = int(w_sampling_period.GetValue())
                slot_time = int(w_slot_time.GetValue())

            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            try:
                msg_str = Popen(
                    [
                        "java",
                        "-jar",
                        "jars/SamplingPeriodSlotTimeAggCfg.jar",
                        str(sampling_period),
                        str(slot_time),
                    ],
                    stdout=PIPE,
                )
                (output, err) = msg_str.communicate()
                msg_str.wait()
            except:
                msgb = wx.MessageDialog(
                    self,
                    "Error executing jars/SamplingPeriodSlotTimeAggCfg.jar",
                    "ERROR",
                    wx.OK | wx.ICON_HAND,
                )
                msgb.ShowModal()
                return

            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(output, tty_usb, self)

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

        wx.StaticText(pnl, label="Sampling Period", pos=(115, vertical_pos + 6))
        w_sampling_period = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_sampling_period.SetMaxLength(10)
        w_sampling_period.WriteText("1800")
        w_sampling_period.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Slot Time", pos=(115, vertical_pos + 6))
        w_slot_time = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_slot_time.SetMaxLength(10)
        w_slot_time.WriteText("1800")
        w_slot_time.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(260, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        configs_list = ["Custom", "SP 15", "SP 300", "SP 30 minutes"]
        wx.StaticText(pnl, label="Load preset configs", pos=(250, 16))
        w_load_config = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(250, 10 + vertical_pos_increment),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_load_config.Bind(wx.EVT_COMBOBOX, load_config)
        w_load_config.SetStringSelection("SP 15")
        vertical_pos = vertical_pos + vertical_pos_increment
        load_config(0)

        self.SetSize((470, vertical_pos + vertical_pos_increment))
        self.SetTitle("AggCfgSamplingPeriodSlotTime")
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
