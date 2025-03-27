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
                w_mac_version.SetValue("0")
                w_dev_eui.SetValue("0000000000000000")
                w_app_eui.SetValue("0000000000000000")
                w_max_time_without_downlink_in_min.SetValue("1440")
                w_join_retry_max_time_divisor.SetValue("0")

                w_join_retry_min_time_multiply.SetValue("0")
                w_join_retry_multiplier_when_fail.SetValue("1")
                w_max_num_link_checks_send_before_reconnect.SetValue("4")

                w_activation.SetValue("ABP")
                w_frame_cnt_mode.SetValue("32")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        # method to set the config

        def set_config(event):

            try:
                mac_version = int(w_mac_version.GetValue())
                dev_eui = w_dev_eui.GetValue()
                app_eui = w_app_eui.GetValue()
                max_time_without_downlink_in_min = int(
                    w_max_time_without_downlink_in_min.GetValue()
                )
                join_retry_max_time_divisor = int(w_join_retry_max_time_divisor.GetValue())
                join_retry_min_time_multiply = int(w_join_retry_min_time_multiply.GetValue())
                join_retry_multiplier_when_fail = int(w_join_retry_multiplier_when_fail.GetValue())
                max_num_link_checks_send_before_reconnect = int(
                    w_max_num_link_checks_send_before_reconnect.GetValue()
                )
                if w_activation.GetValue() == "ABP":
                    activation = 0
                else:
                    activation = 1
                if w_frame_cnt_mode.GetValue() == "16":
                    frame_cnt_mode = 0
                else:
                    frame_cnt_mode = 1
            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            try:
                msg2send = "94"
                msg2send += "%02X" % mac_version
                msg2send += dev_eui
                msg2send += app_eui
                msg2send += "%04X" % max_time_without_downlink_in_min
                msg2send += "%02X" % join_retry_max_time_divisor
                msg2send += "%02X" % (
                    ((join_retry_min_time_multiply & 0x3F) << 2)
                    | ((join_retry_multiplier_when_fail & 0x03) << 0)
                )
                msg2send += "%02X" % (max_num_link_checks_send_before_reconnect)
                msg2send += "%02X" % (((activation & 0x01) << 7) | ((frame_cnt_mode & 0x01) << 6))
                # a = (((activation & 0x01) << 7) | ((frame_cnt_mode & 0x01) << 6))

                output = ""
                i = 0
                for cur in msg2send:
                    if i % 2 == 0:
                        output += "\\x"
                    output += cur
                    i += 1
            except:
                msgb = wx.MessageDialog(
                    self, "Error executing jars/LoraJoinCfg.jar", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(output, tty_usb, self)

        # method to request the config
        def request_config(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x00\\x94", tty_usb, self)

        def set_custom_config(event):
            w_load_config.SetStringSelection("Custom")

        def request_session(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x0F", tty_usb, self)

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        mac_version_list = ["0"]
        wx.StaticText(pnl, label="MAC Version", pos=(115, vertical_pos + 6))
        w_mac_version = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(90, 30),
            pos=(20, vertical_pos),
            choices=mac_version_list,
            style=wx.CB_READONLY,
        )
        w_mac_version.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="DevEUI", pos=(195, vertical_pos + 6))
        w_dev_eui = wx.TextCtrl(pnl, -1, size=(170, 30), pos=(20, vertical_pos))
        w_dev_eui.SetMaxLength(16)
        w_dev_eui.WriteText("")
        w_dev_eui.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="AppEUI", pos=(195, vertical_pos + 6))
        w_app_eui = wx.TextCtrl(pnl, -1, size=(170, 30), pos=(20, vertical_pos))
        w_app_eui.SetMaxLength(16)
        w_app_eui.WriteText("")
        w_app_eui.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="MaxTimeWithoutDownlinkInMin:", pos=(115, vertical_pos + 6))
        w_max_time_without_downlink_in_min = wx.TextCtrl(
            pnl, -1, size=(90, 30), pos=(20, vertical_pos)
        )
        w_max_time_without_downlink_in_min.SetMaxLength(10)
        w_max_time_without_downlink_in_min.WriteText("60")
        w_max_time_without_downlink_in_min.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="JoinRetryMaxTimeDivisor (+1)", pos=(115, vertical_pos + 6))
        w_join_retry_max_time_divisor = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_join_retry_max_time_divisor.SetMaxLength(10)
        w_join_retry_max_time_divisor.WriteText("0")
        w_join_retry_max_time_divisor.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="JoinRetryMinTimeMultiply (+1)", pos=(115, vertical_pos + 6))
        w_join_retry_min_time_multiply = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_join_retry_min_time_multiply.SetMaxLength(10)
        w_join_retry_min_time_multiply.WriteText("0")
        w_join_retry_min_time_multiply.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="JoinRetryMultiplierWhenFail (+1)", pos=(115, vertical_pos + 6))
        w_join_retry_multiplier_when_fail = wx.TextCtrl(
            pnl, -1, size=(90, 30), pos=(20, vertical_pos)
        )
        w_join_retry_multiplier_when_fail.SetMaxLength(10)
        w_join_retry_multiplier_when_fail.WriteText("1")
        w_join_retry_multiplier_when_fail.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="MaxNumLinkChecksSendBeforeReconnect", pos=(115, vertical_pos + 6))
        w_max_num_link_checks_send_before_reconnect = wx.TextCtrl(
            pnl, -1, size=(90, 30), pos=(20, vertical_pos)
        )
        w_max_num_link_checks_send_before_reconnect.SetMaxLength(10)
        w_max_num_link_checks_send_before_reconnect.WriteText("4")
        w_max_num_link_checks_send_before_reconnect.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        activation_list = ["ABP", "OTAA"]
        wx.StaticText(pnl, label="Activation", pos=(115, vertical_pos + 6))
        w_activation = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(90, 30),
            pos=(20, vertical_pos),
            choices=activation_list,
            style=wx.CB_READONLY,
        )
        w_activation.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        frame_cnt_mode_list = ["16", "32"]
        wx.StaticText(pnl, label="FrameCntMode", pos=(115, vertical_pos + 6))
        w_frame_cnt_mode = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(90, 30),
            pos=(20, vertical_pos),
            choices=frame_cnt_mode_list,
            style=wx.CB_READONLY,
        )
        w_frame_cnt_mode.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_req_session_btn = wx.Button(pnl, label="Request Join Session", pos=(20, vertical_pos))
        w_req_session_btn.Bind(wx.EVT_BUTTON, request_session)

        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(260, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        w_req_config_btn = wx.Button(pnl, label="Request Config", pos=(350, vertical_pos))
        w_req_config_btn.Bind(wx.EVT_BUTTON, request_config)

        configs_list = ["Custom", "Default"]
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
        w_load_config.SetStringSelection("Test Default")
        vertical_pos = vertical_pos + vertical_pos_increment
        load_config(0)

        self.SetSize((475, vertical_pos + vertical_pos_increment))
        self.SetTitle("LoRaJoinCfg")
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
