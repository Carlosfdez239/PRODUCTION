#!/usr/bin/env python3
import os
import sys

import bitstring
import wx
from bitstring import BitArray
from ls_utils import ls_send_message_uart

global_tty = ""

MAXIMUM_THRESHOLD_MAX_VALUE = 9000
MAXIMUM_THRESHOLD_MIN_VALUE = -8999
MINIMUM_THRESHOLD_MIN_VALUE = -9000
MINIMUM_THRESHOLD_MAX_VALUE = 8999

MAXIMUM_THRESHOLD_DEFAULT_VALUE = 45
MINIMUM_THRESHOLD_DEFAULT_VALUE = -45
MAXIMUM_Y_THRESHOLD_DEFAULT_VALUE = 90
MINIMUM_Y_THRESHOLD_DEFAULT_VALUE = 80
ABS_TH_ALERT_OFF_DELAY_DEFAULT_VALUE = 8

MAXIMUM_ALERT_SAMPLING_PERIOD = 86400
MINIMUM_ALERT_SAMPLING_PERIOD = 0


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

                w_abs_th_alert_off.SetValue(str(ABS_TH_ALERT_OFF_DELAY_DEFAULT_VALUE))

                w_ch1_enabled_alert.SetValue(False)
                w_ch2_enabled_alert.SetValue(False)
                w_ch3_enabled_alert.SetValue(False)

                w_abs_th_axis_1max.SetValue(str(MAXIMUM_THRESHOLD_DEFAULT_VALUE))
                w_abs_th_axis_2max.SetValue(str(MAXIMUM_THRESHOLD_DEFAULT_VALUE))
                w_abs_th_axis_3max.SetValue(str(MAXIMUM_Y_THRESHOLD_DEFAULT_VALUE))

                w_abs_th_axis_1min.SetValue(str(MINIMUM_THRESHOLD_DEFAULT_VALUE))
                w_abs_th_axis_2min.SetValue(str(MINIMUM_THRESHOLD_DEFAULT_VALUE))
                w_abs_th_axis_3min.SetValue(str(MINIMUM_Y_THRESHOLD_DEFAULT_VALUE))

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "TiltConfigTest":
                w_message_version.SetValue("0")
                w_reserved.SetValue("0")
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)

                w_abs_th_alert_off.SetValue(str(1))

                w_ch1_enabled_alert.SetValue(False)
                w_ch2_enabled_alert.SetValue(False)
                w_ch3_enabled_alert.SetValue(False)

                w_abs_th_axis_1max.SetValue(str(90.01))
                w_abs_th_axis_2max.SetValue(str(10))
                w_abs_th_axis_3max.SetValue(str(0))

                w_abs_th_axis_1min.SetValue(str(-10))
                w_abs_th_axis_2min.SetValue(str(-90.01))
                w_abs_th_axis_3min.SetValue(str(0))

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        # method to set the config

        def set_config(event):
            w_config_warnings.SetValue("")
            valid_config = True
            try:
                configuration_array = BitArray()
                message_version = int(w_message_version.GetValue())
                if message_version != 0:
                    w_config_warnings.WriteText("Version valid value is 0\n")
                    valid_config = False
                if message_version > 7:
                    return
                configuration_array.append(bitstring.pack("uint:3", (message_version)))

                reserved_value = int(w_reserved.GetValue())
                if reserved_value != 0:
                    w_config_warnings.WriteText("Reserved valid value is 0\n")
                    valid_config = False
                if reserved_value > 1:
                    return
                configuration_array.append(bitstring.pack("uint:1", (reserved_value)))

                if (
                    (w_ch3_enabled.GetValue() == 0 and w_ch3_enabled_alert.GetValue() == 1)
                    or (w_ch2_enabled.GetValue() == 0 and w_ch2_enabled_alert.GetValue() == 1)
                    or (w_ch1_enabled.GetValue() == 0 and w_ch1_enabled_alert.GetValue()) == 1
                ):
                    w_config_warnings.WriteText(
                        "A channel alert cannot be activated if the channel is not enabled\n"
                    )
                    valid_config = False

                configuration_array.append(bitstring.pack("uint:1", (w_ch3_enabled.GetValue())))
                configuration_array.append(bitstring.pack("uint:1", (w_ch2_enabled.GetValue())))
                configuration_array.append(bitstring.pack("uint:1", (w_ch1_enabled.GetValue())))

                configuration_array.append(
                    bitstring.pack("uint:1", (w_ch3_enabled_alert.GetValue()))
                )
                configuration_array.append(
                    bitstring.pack("uint:1", (w_ch2_enabled_alert.GetValue()))
                )
                configuration_array.append(
                    bitstring.pack("uint:1", (w_ch1_enabled_alert.GetValue()))
                )

                abs_th_alert_off_value = int(w_abs_th_alert_off.GetValue())
                if abs_th_alert_off_value < 0 or abs_th_alert_off_value > 15:
                    w_config_warnings.WriteText(
                        "Absolute threshold alert off value valid range is [0-15]\n"
                    )
                    valid_config = False
                configuration_array.append(bitstring.pack("uint:4", (abs_th_alert_off_value)))

                abs_th_max_axis_1 = float(str(w_abs_th_axis_1max.GetValue()))
                formatted_abs_th_max_axis_1 = int(
                    str("{:.2f}".format(abs_th_max_axis_1)).replace(".", "")
                )
                if (
                    formatted_abs_th_max_axis_1 < MAXIMUM_THRESHOLD_MIN_VALUE
                    or formatted_abs_th_max_axis_1 > MAXIMUM_THRESHOLD_MAX_VALUE
                ):
                    w_config_warnings.WriteText(
                        "Absolute threshold maximum axis 1 valid range is [-89.99 , 90.00]\n"
                    )
                    valid_config = False

                abs_th_min_axis_1 = float(str(w_abs_th_axis_1min.GetValue()))
                formatted_abs_th_min_axis_1 = int(
                    str("{:.2f}".format(abs_th_min_axis_1)).replace(".", "")
                )
                if (
                    formatted_abs_th_min_axis_1 < MINIMUM_THRESHOLD_MIN_VALUE
                    or formatted_abs_th_min_axis_1 > MINIMUM_THRESHOLD_MAX_VALUE
                ):
                    w_config_warnings.WriteText(
                        "Absolute threshold minimum axis 1 valid range is [-90.00 , 89.99]\n"
                    )
                    valid_config = False

                if formatted_abs_th_max_axis_1 <= formatted_abs_th_min_axis_1:
                    w_config_warnings.WriteText(
                        "Axis 1: The maximum threshold should be greater than the minimum threshold\n"
                    )
                    valid_config = False

                configuration_array.append(bitstring.pack("int:15", (formatted_abs_th_max_axis_1)))
                configuration_array.append(bitstring.pack("int:15", (formatted_abs_th_min_axis_1)))

                abs_th_max_axis_2 = float(str(w_abs_th_axis_2max.GetValue()))
                formatted_abs_th_max_axis_2 = int(
                    str("{:.2f}".format(abs_th_max_axis_2)).replace(".", "")
                )
                if (
                    formatted_abs_th_max_axis_2 < MAXIMUM_THRESHOLD_MIN_VALUE
                    or formatted_abs_th_max_axis_2 > MAXIMUM_THRESHOLD_MAX_VALUE
                ):
                    w_config_warnings.WriteText(
                        "Absolute threshold maximum axis 2 valid range is [-89.99 , 90.00]\n"
                    )
                    valid_config = False

                abs_th_min_axis_2 = float(str(w_abs_th_axis_2min.GetValue()))
                formatted_abs_th_min_axis_2 = int(
                    str("{:.2f}".format(abs_th_min_axis_2)).replace(".", "")
                )
                if (
                    formatted_abs_th_min_axis_2 < MINIMUM_THRESHOLD_MIN_VALUE
                    or formatted_abs_th_min_axis_2 > MINIMUM_THRESHOLD_MAX_VALUE
                ):
                    w_config_warnings.WriteText(
                        "Absolute threshold minimum axis 2 valid range is [-90.00 , 89.99]\n"
                    )
                    valid_config = False

                if formatted_abs_th_max_axis_2 <= formatted_abs_th_min_axis_2:
                    w_config_warnings.WriteText(
                        "Axis 2: The maximum threshold should be greater than the minimum threshold\n"
                    )
                    valid_config = False

                configuration_array.append(bitstring.pack("int:15", (formatted_abs_th_max_axis_2)))
                configuration_array.append(bitstring.pack("int:15", (formatted_abs_th_min_axis_2)))

                abs_th_max_axis_3 = float(str(w_abs_th_axis_3max.GetValue()))
                formatted_abs_th_max_axis_3 = int(
                    str("{:.2f}".format(abs_th_max_axis_3)).replace(".", "")
                )
                if (
                    abs_th_max_axis_3 < MAXIMUM_THRESHOLD_MIN_VALUE
                    or abs_th_max_axis_3 > MAXIMUM_THRESHOLD_MAX_VALUE
                ):
                    w_config_warnings.WriteText(
                        "Absolute threshold maximum axis 3 valid range is [-89.99 , 90.00]\n"
                    )
                    valid_config = False

                abs_th_min_axis_3 = float(str(w_abs_th_axis_3min.GetValue()))
                formatted_abs_th_min_axis_3 = int(
                    str("{:.2f}".format(abs_th_min_axis_3)).replace(".", "")
                )
                if (
                    formatted_abs_th_min_axis_3 < MINIMUM_THRESHOLD_MIN_VALUE
                    or formatted_abs_th_min_axis_3 > MINIMUM_THRESHOLD_MAX_VALUE
                ):
                    w_config_warnings.WriteText(
                        "Absolute threshold minimum axis 3 valid range is [-90.00 , 89.99]\n"
                    )
                    valid_config = False

                if formatted_abs_th_max_axis_3 <= formatted_abs_th_min_axis_3:
                    w_config_warnings.WriteText(
                        "Axis 3: The maximum threshold should be greater than the minimum threshold\n"
                    )
                    valid_config = False

                configuration_array.append(bitstring.pack("int:15", (formatted_abs_th_max_axis_3)))
                configuration_array.append(bitstring.pack("int:15", (formatted_abs_th_min_axis_3)))

                if w_send_alert_sampling.GetValue() == 1:
                    alert_sampling_period = int(w_sampling_period_alert.GetValue())
                    if (
                        alert_sampling_period > MAXIMUM_ALERT_SAMPLING_PERIOD
                        or alert_sampling_period < MINIMUM_ALERT_SAMPLING_PERIOD
                    ):
                        w_config_warnings.WriteText("Alert SP: Invalid sampling period\n")
                        valid_config = False

                    configuration_array.append(bitstring.pack("uint:24", (alert_sampling_period)))

                if valid_config is False:
                    msgb = wx.MessageDialog(
                        self,
                        "Seems that you want to send and invalid configuration, do you want to continue?",
                        "WARNING",
                        wx.OK | wx.CANCEL | wx.ICON_HAND,
                    )
                    result = msgb.ShowModal()
                    if wx.ID_CANCEL == result:
                        return

            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            if w_send_alert_sampling.GetValue() == 1:
                output = "C1" + "00"  # AMTYPE AGGCFG + MSG VERSION/RESERVED FIELDS
            else:
                output = "9B"  # AMTYPE CHCFG

            output += bytes.hex(configuration_array.tobytes())
            output = "\\x" + "\\x".join(a + b for a, b in zip(output[::2], output[1::2]))
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(output, tty_usb, self)

        # method to request the config
        def request_config(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x00\\x9B", tty_usb, self)

        def set_custom_config(event):
            w_load_config.SetStringSelection("Custom")

        def display_agg_cfg_dialog(event):
            if w_send_alert_sampling.GetValue() == 1:
                w_sampling_period_alert.Enable()
                msgb = wx.MessageDialog(
                    self,
                    "Sending the Alert Sampling Period with the configuration message will send an"
                    "aggregated configuration message",
                    "INFO",
                    wx.OK | wx.ICON_HAND,
                )
                result = msgb.ShowModal()
                if wx.ID_CANCEL == result:
                    return
            else:
                w_sampling_period_alert.Disable()

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
        w_message_version.WriteText("0")
        w_message_version.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="Reserved bits", pos=(20, vertical_pos + 6))
        w_reserved = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(130, vertical_pos))
        w_reserved.SetMaxLength(1)
        w_reserved.WriteText("0")
        w_reserved.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="Enabled Channels", pos=(20, vertical_pos + 6))
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

        wx.StaticText(pnl, label="Enabled Alert Channels", pos=(20, vertical_pos + 6))
        vertical_pos += vertical_pos_increment

        w_ch1_enabled_alert = wx.CheckBox(pnl, label="Ch1", pos=(40, vertical_pos))
        w_ch1_enabled_alert.SetValue(True)
        w_ch1_enabled_alert.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_ch2_enabled_alert = wx.CheckBox(pnl, label="Ch2", pos=(120, vertical_pos))
        w_ch2_enabled_alert.SetValue(True)
        w_ch2_enabled_alert.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_ch3_enabled_alert = wx.CheckBox(pnl, label="Ch3", pos=(200, vertical_pos))
        w_ch3_enabled_alert.SetValue(True)
        w_ch3_enabled_alert.Bind(wx.EVT_CHECKBOX, set_custom_config)

        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="Abs Th Alert Off Delay", pos=(20, vertical_pos + 6))
        w_abs_th_alert_off = wx.TextCtrl(pnl, -1, size=(60, 30), pos=(186, vertical_pos))
        w_abs_th_alert_off.SetMaxLength(2)
        w_abs_th_alert_off.SetValue(str(ABS_TH_ALERT_OFF_DELAY_DEFAULT_VALUE))
        w_abs_th_alert_off.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="Absolute threshold Axis 1", pos=(20, vertical_pos + 6))
        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="Upper:", pos=(20, vertical_pos + 3))
        w_abs_th_axis_1max = wx.TextCtrl(pnl, -1, size=(60, 30), pos=(66, vertical_pos))
        w_abs_th_axis_1max.SetMaxLength(6)
        w_abs_th_axis_1max.SetValue(str(MAXIMUM_THRESHOLD_DEFAULT_VALUE))
        w_abs_th_axis_1max.Bind(wx.EVT_TEXT, set_custom_config)

        wx.StaticText(pnl, label="Lower:", pos=(140, vertical_pos + 3))
        w_abs_th_axis_1min = wx.TextCtrl(pnl, -1, size=(60, 30), pos=(186, vertical_pos))
        w_abs_th_axis_1min.SetMaxLength(6)
        w_abs_th_axis_1min.SetValue(str(MINIMUM_THRESHOLD_DEFAULT_VALUE))
        w_abs_th_axis_1min.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="Absolute threshold Axis 2", pos=(20, vertical_pos + 6))
        vertical_pos += 30

        wx.StaticText(pnl, label="Upper:", pos=(20, vertical_pos + 6))
        w_abs_th_axis_2max = wx.TextCtrl(pnl, -1, size=(60, 30), pos=(66, vertical_pos))
        w_abs_th_axis_2max.SetMaxLength(6)
        w_abs_th_axis_2max.SetValue(str(MAXIMUM_THRESHOLD_DEFAULT_VALUE))
        w_abs_th_axis_2max.Bind(wx.EVT_TEXT, set_custom_config)

        wx.StaticText(pnl, label="Lower:", pos=(140, vertical_pos + 6))
        w_abs_th_axis_2min = wx.TextCtrl(pnl, -1, size=(60, 30), pos=(186, vertical_pos))
        w_abs_th_axis_2min.SetMaxLength(6)
        w_abs_th_axis_2min.SetValue(str(MINIMUM_THRESHOLD_DEFAULT_VALUE))
        w_abs_th_axis_2min.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="Absolute threshold Axis 3", pos=(20, vertical_pos + 6))
        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="Upper:", pos=(20, vertical_pos + 6))
        w_abs_th_axis_3max = wx.TextCtrl(pnl, -1, size=(60, 30), pos=(66, vertical_pos))
        w_abs_th_axis_3max.SetMaxLength(6)
        w_abs_th_axis_3max.SetValue(str(MAXIMUM_Y_THRESHOLD_DEFAULT_VALUE))
        w_abs_th_axis_3max.Bind(wx.EVT_TEXT, set_custom_config)

        wx.StaticText(pnl, label="Lower:", pos=(140, vertical_pos + 6))
        w_abs_th_axis_3min = wx.TextCtrl(pnl, -1, size=(60, 30), pos=(186, vertical_pos))
        w_abs_th_axis_3min.SetMaxLength(6)
        w_abs_th_axis_3min.SetValue(str(MINIMUM_Y_THRESHOLD_DEFAULT_VALUE))
        w_abs_th_axis_3min.Bind(wx.EVT_TEXT, set_custom_config)

        wx.StaticText(pnl, label="Config warnings:", pos=(300, 100))
        w_config_warnings = wx.TextCtrl(
            pnl, -1, size=(300, 300), pos=(300, 130), style=wx.TE_MULTILINE | wx.TE_READONLY
        )
        w_config_warnings.SetBackgroundColour(wx.Colour(230, 230, 230))
        w_config_warnings.SetValue("")

        w_send_alert_sampling = wx.CheckBox(
            pnl, label="Send Alert SP", pos=(300, vertical_pos - 15)
        )
        w_send_alert_sampling.SetValue(False)
        w_send_alert_sampling.Bind(wx.EVT_CHECKBOX, display_agg_cfg_dialog)

        w_sampling_period_alert = wx.TextCtrl(pnl, -1, size=(60, 30), pos=(420, vertical_pos - 21))
        w_sampling_period_alert.SetMaxLength(5)
        w_sampling_period_alert.Disable()
        vertical_pos += vertical_pos_increment

        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(300, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        w_set_config_btn = wx.Button(pnl, label="Request Config", pos=(300 + 90, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_config)
        vertical_pos += vertical_pos_increment

        configs_list = ["Custom", "Default", "TiltConfigTest"]
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
        w_load_config.SetStringSelection("Default")
        load_config(0)

        vertical_pos = vertical_pos + vertical_pos_increment
        self.SetSize((620, vertical_pos))
        self.SetTitle("Tilt360AlertChCfg")
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
