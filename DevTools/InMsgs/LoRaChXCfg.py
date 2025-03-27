#!/usr/bin/env python3
import os
import sys
from subprocess import PIPE, Popen

import wx
from ls_utils import ls_send_message_uart


class Example(wx.Frame):
    def __init__(self, *args, **kw):
        super(Example, self).__init__(*args, **kw)

        self.init_ui()

    def init_ui(self):
        global global_tty

        def load_config(event):
            group = w_group_num.GetValue()
            if group == "Group 0":
                load_config_group_0()
            elif group == "Group 1":
                load_config_group_1()
            elif group == "Group FCC Down":
                load_config_group_down_fcc()

        def load_config_group_0():
            config = w_load_config.GetValue()

            if config == "Default":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(False)
                w_ch7_enabled.SetValue(False)

                w_ch0_freq.SetValue("868100000")
                w_ch1_freq.SetValue("868300000")
                w_ch2_freq.SetValue("868500000")
                w_ch3_freq.SetValue("868850000")
                w_ch4_freq.SetValue("869050000")
                w_ch5_freq.SetValue("869525000")
                w_ch6_freq.SetValue("0")
                w_ch7_freq.SetValue("0")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Test Default":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(False)
                w_ch7_enabled.SetValue(False)

                w_ch0_freq.SetValue("868100000")
                w_ch1_freq.SetValue("868300000")
                w_ch2_freq.SetValue("868500000")
                w_ch3_freq.SetValue("868850000")
                w_ch4_freq.SetValue("869050000")
                w_ch5_freq.SetValue("869525000")
                w_ch6_freq.SetValue("0")
                w_ch7_freq.SetValue("0")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Singapore":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("920900000")
                w_ch1_freq.SetValue("921200000")
                w_ch2_freq.SetValue("921500000")
                w_ch3_freq.SetValue("921800000")
                w_ch4_freq.SetValue("922500000")
                w_ch5_freq.SetValue("922800000")
                w_ch6_freq.SetValue("923100000")
                w_ch7_freq.SetValue("923400000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "923A":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("917200000")
                w_ch1_freq.SetValue("917400000")
                w_ch2_freq.SetValue("917600000")
                w_ch3_freq.SetValue("917800000")
                w_ch4_freq.SetValue("918000000")
                w_ch5_freq.SetValue("918200000")
                w_ch6_freq.SetValue("918400000")
                w_ch7_freq.SetValue("918600000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Malaysia":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(False)
                w_ch6_enabled.SetValue(False)
                w_ch7_enabled.SetValue(False)

                w_ch0_freq.SetValue("869100000")
                w_ch1_freq.SetValue("869300000")
                w_ch2_freq.SetValue("869500000")
                w_ch3_freq.SetValue("869700000")
                w_ch4_freq.SetValue("869900000")
                w_ch5_freq.SetValue("0")
                w_ch6_freq.SetValue("0")
                w_ch7_freq.SetValue("0")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "FCC - 1":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("902300000")
                w_ch1_freq.SetValue("902500000")
                w_ch2_freq.SetValue("902700000")
                w_ch3_freq.SetValue("902900000")
                w_ch4_freq.SetValue("903100000")
                w_ch5_freq.SetValue("903300000")
                w_ch6_freq.SetValue("903500000")
                w_ch7_freq.SetValue("903700000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "FCC - 2":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("903900000")
                w_ch1_freq.SetValue("904100000")
                w_ch2_freq.SetValue("904300000")
                w_ch3_freq.SetValue("904500000")
                w_ch4_freq.SetValue("904700000")
                w_ch5_freq.SetValue("904900000")
                w_ch6_freq.SetValue("905100000")
                w_ch7_freq.SetValue("905300000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "FCC group 7":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("913500000")
                w_ch1_freq.SetValue("913700000")
                w_ch2_freq.SetValue("913900000")
                w_ch3_freq.SetValue("914100000")
                w_ch4_freq.SetValue("914300000")
                w_ch5_freq.SetValue("914500000")
                w_ch6_freq.SetValue("914700000")
                w_ch7_freq.SetValue("914900000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "923A":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("917200000")
                w_ch1_freq.SetValue("917400000")
                w_ch2_freq.SetValue("917600000")
                w_ch3_freq.SetValue("917800000")
                w_ch4_freq.SetValue("918000000")
                w_ch5_freq.SetValue("918200000")
                w_ch6_freq.SetValue("918400000")
                w_ch7_freq.SetValue("918600000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "FCC Down Ch Test":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("913300000")
                w_ch1_freq.SetValue("913300000")
                w_ch2_freq.SetValue("913300000")
                w_ch3_freq.SetValue("913300000")
                w_ch4_freq.SetValue("913300000")
                w_ch5_freq.SetValue("913300000")
                w_ch6_freq.SetValue("913300000")
                w_ch7_freq.SetValue("913300000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "923A Down":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("923300000")
                w_ch1_freq.SetValue("923900000")
                w_ch2_freq.SetValue("924500000")
                w_ch3_freq.SetValue("925100000")
                w_ch4_freq.SetValue("925700000")
                w_ch5_freq.SetValue("926300000")
                w_ch6_freq.SetValue("926900000")
                w_ch7_freq.SetValue("927500000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "926C":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("925200000")
                w_ch1_freq.SetValue("925400000")
                w_ch2_freq.SetValue("925600000")
                w_ch3_freq.SetValue("925800000")
                w_ch4_freq.SetValue("926000000")
                w_ch5_freq.SetValue("926200000")
                w_ch6_freq.SetValue("926400000")
                w_ch7_freq.SetValue("926600000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "866I":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("865300000")
                w_ch1_freq.SetValue("865500000")
                w_ch2_freq.SetValue("865700000")
                w_ch3_freq.SetValue("865900000")
                w_ch4_freq.SetValue("866100000")
                w_ch5_freq.SetValue("866300000")
                w_ch6_freq.SetValue("866500000")
                w_ch7_freq.SetValue("866700000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LoraWAN EU868 (EU)":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("868100000")
                w_ch1_freq.SetValue("868300000")
                w_ch2_freq.SetValue("868500000")
                w_ch3_freq.SetValue("867100000")
                w_ch4_freq.SetValue("867300000")
                w_ch5_freq.SetValue("867500000")
                w_ch6_freq.SetValue("867700000")
                w_ch7_freq.SetValue("867900000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LoraWAN US915 (FCC) 0-15":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("902300000")
                w_ch1_freq.SetValue("902500000")
                w_ch2_freq.SetValue("902700000")
                w_ch3_freq.SetValue("902900000")
                w_ch4_freq.SetValue("903100000")
                w_ch5_freq.SetValue("903300000")
                w_ch6_freq.SetValue("903500000")
                w_ch7_freq.SetValue("903700000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LoraWAN AS923 (922S)":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("923200000")
                w_ch1_freq.SetValue("923400000")
                w_ch2_freq.SetValue("922200000")
                w_ch3_freq.SetValue("922400000")
                w_ch4_freq.SetValue("922600000")
                w_ch5_freq.SetValue("922800000")
                w_ch6_freq.SetValue("923000000")
                w_ch7_freq.SetValue("922000000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LoraWAN AU915 (923A) 0-15":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("915200000")
                w_ch1_freq.SetValue("915400000")
                w_ch2_freq.SetValue("915600000")
                w_ch3_freq.SetValue("915800000")
                w_ch4_freq.SetValue("916000000")
                w_ch5_freq.SetValue("916200000")
                w_ch6_freq.SetValue("916400000")
                w_ch7_freq.SetValue("916600000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        def load_config_group_1():
            config = w_load_config.GetValue()

            if config == "Default":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(False)
                w_ch1_enabled.SetValue(False)
                w_ch2_enabled.SetValue(False)
                w_ch3_enabled.SetValue(False)
                w_ch4_enabled.SetValue(False)
                w_ch5_enabled.SetValue(False)
                w_ch6_enabled.SetValue(False)
                w_ch7_enabled.SetValue(False)

                w_ch0_freq.SetValue("0")
                w_ch1_freq.SetValue("0")
                w_ch2_freq.SetValue("0")
                w_ch3_freq.SetValue("0")
                w_ch4_freq.SetValue("0")
                w_ch5_freq.SetValue("0")
                w_ch6_freq.SetValue("0")
                w_ch7_freq.SetValue("0")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Test Default":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(False)
                w_ch1_enabled.SetValue(False)
                w_ch2_enabled.SetValue(False)
                w_ch3_enabled.SetValue(False)
                w_ch4_enabled.SetValue(False)
                w_ch5_enabled.SetValue(False)
                w_ch6_enabled.SetValue(False)
                w_ch7_enabled.SetValue(False)

                w_ch0_freq.SetValue("0")
                w_ch1_freq.SetValue("0")
                w_ch2_freq.SetValue("0")
                w_ch3_freq.SetValue("0")
                w_ch4_freq.SetValue("0")
                w_ch5_freq.SetValue("0")
                w_ch6_freq.SetValue("0")
                w_ch7_freq.SetValue("0")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Singapore":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("920900000")
                w_ch1_freq.SetValue("921200000")
                w_ch2_freq.SetValue("921500000")
                w_ch3_freq.SetValue("921800000")
                w_ch4_freq.SetValue("922500000")
                w_ch5_freq.SetValue("922800000")
                w_ch6_freq.SetValue("923100000")
                w_ch7_freq.SetValue("923400000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Malaysia":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(False)
                w_ch6_enabled.SetValue(False)
                w_ch7_enabled.SetValue(False)

                w_ch0_freq.SetValue("869100000")
                w_ch1_freq.SetValue("869300000")
                w_ch2_freq.SetValue("869500000")
                w_ch3_freq.SetValue("869700000")
                w_ch4_freq.SetValue("869900000")
                w_ch5_freq.SetValue("0")
                w_ch6_freq.SetValue("0")
                w_ch7_freq.SetValue("0")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "FCC - 1":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("902300000")
                w_ch1_freq.SetValue("902500000")
                w_ch2_freq.SetValue("902700000")
                w_ch3_freq.SetValue("902900000")
                w_ch4_freq.SetValue("903100000")
                w_ch5_freq.SetValue("903300000")
                w_ch6_freq.SetValue("903500000")
                w_ch7_freq.SetValue("903700000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "FCC - 2":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("903900000")
                w_ch1_freq.SetValue("904100000")
                w_ch2_freq.SetValue("904300000")
                w_ch3_freq.SetValue("904500000")
                w_ch4_freq.SetValue("904700000")
                w_ch5_freq.SetValue("904900000")
                w_ch6_freq.SetValue("905100000")
                w_ch7_freq.SetValue("905300000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "FCC Down Ch Test":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(False)
                w_ch1_enabled.SetValue(False)
                w_ch2_enabled.SetValue(False)
                w_ch3_enabled.SetValue(False)
                w_ch4_enabled.SetValue(False)
                w_ch5_enabled.SetValue(False)
                w_ch6_enabled.SetValue(False)
                w_ch7_enabled.SetValue(False)

                w_ch0_freq.SetValue("")
                w_ch1_freq.SetValue("")
                w_ch2_freq.SetValue("")
                w_ch3_freq.SetValue("")
                w_ch4_freq.SetValue("")
                w_ch5_freq.SetValue("")
                w_ch6_freq.SetValue("")
                w_ch7_freq.SetValue("")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LoraWAN US915 (FCC) 0-15":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("903900000")
                w_ch1_freq.SetValue("904100000")
                w_ch2_freq.SetValue("904300000")
                w_ch3_freq.SetValue("904500000")
                w_ch4_freq.SetValue("904700000")
                w_ch5_freq.SetValue("904900000")
                w_ch6_freq.SetValue("905100000")
                w_ch7_freq.SetValue("905300000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "LoraWAN AU915 (923A) 0-15":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("916800000")
                w_ch1_freq.SetValue("917000000")
                w_ch2_freq.SetValue("917200000")
                w_ch3_freq.SetValue("917400000")
                w_ch4_freq.SetValue("917600000")
                w_ch5_freq.SetValue("917800000")
                w_ch6_freq.SetValue("918000000")
                w_ch7_freq.SetValue("918200000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        def load_config_group_down_fcc():
            config = w_load_config.GetValue()

            if config == "Default":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("923300000")
                w_ch1_freq.SetValue("923900000")
                w_ch2_freq.SetValue("924500000")
                w_ch3_freq.SetValue("925100000")
                w_ch4_freq.SetValue("925700000")
                w_ch5_freq.SetValue("926300000")
                w_ch6_freq.SetValue("926900000")
                w_ch7_freq.SetValue("927500000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Test Default":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("923300000")
                w_ch1_freq.SetValue("923900000")
                w_ch2_freq.SetValue("924500000")
                w_ch3_freq.SetValue("925100000")
                w_ch4_freq.SetValue("925700000")
                w_ch5_freq.SetValue("926300000")
                w_ch6_freq.SetValue("926900000")
                w_ch7_freq.SetValue("927500000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Singapore":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(False)
                w_ch1_enabled.SetValue(False)
                w_ch2_enabled.SetValue(False)
                w_ch3_enabled.SetValue(False)
                w_ch4_enabled.SetValue(False)
                w_ch5_enabled.SetValue(False)
                w_ch6_enabled.SetValue(False)
                w_ch7_enabled.SetValue(False)

                w_ch0_freq.SetValue("")
                w_ch1_freq.SetValue("")
                w_ch2_freq.SetValue("")
                w_ch3_freq.SetValue("")
                w_ch4_freq.SetValue("")
                w_ch5_freq.SetValue("")
                w_ch6_freq.SetValue("")
                w_ch7_freq.SetValue("")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "FCC - 1":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(False)
                w_ch1_enabled.SetValue(False)
                w_ch2_enabled.SetValue(False)
                w_ch3_enabled.SetValue(False)
                w_ch4_enabled.SetValue(False)
                w_ch5_enabled.SetValue(False)
                w_ch6_enabled.SetValue(False)
                w_ch7_enabled.SetValue(False)

                w_ch0_freq.SetValue("")
                w_ch1_freq.SetValue("")
                w_ch2_freq.SetValue("")
                w_ch3_freq.SetValue("")
                w_ch4_freq.SetValue("")
                w_ch5_freq.SetValue("")
                w_ch6_freq.SetValue("")
                w_ch7_freq.SetValue("")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "FCC - 2":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(False)
                w_ch1_enabled.SetValue(False)
                w_ch2_enabled.SetValue(False)
                w_ch3_enabled.SetValue(False)
                w_ch4_enabled.SetValue(False)
                w_ch5_enabled.SetValue(False)
                w_ch6_enabled.SetValue(False)
                w_ch7_enabled.SetValue(False)

                w_ch0_freq.SetValue("")
                w_ch1_freq.SetValue("")
                w_ch2_freq.SetValue("")
                w_ch3_freq.SetValue("")
                w_ch4_freq.SetValue("")
                w_ch5_freq.SetValue("")
                w_ch6_freq.SetValue("")
                w_ch7_freq.SetValue("")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "FCC Down Ch Test":
                w_msg_version.SetValue("0")

                w_ch0_enabled.SetValue(True)
                w_ch1_enabled.SetValue(True)
                w_ch2_enabled.SetValue(True)
                w_ch3_enabled.SetValue(True)
                w_ch4_enabled.SetValue(True)
                w_ch5_enabled.SetValue(True)
                w_ch6_enabled.SetValue(True)
                w_ch7_enabled.SetValue(True)

                w_ch0_freq.SetValue("913300000")
                w_ch1_freq.SetValue("913900000")
                w_ch2_freq.SetValue("914500000")
                w_ch3_freq.SetValue("915100000")
                w_ch4_freq.SetValue("915700000")
                w_ch5_freq.SetValue("916300000")
                w_ch6_freq.SetValue("916900000")
                w_ch7_freq.SetValue("917500000")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        # method to set the config
        def set_config(event):

            try:
                group = w_group_num.GetValue()
                if group == "Group 0":
                    group_id = "0"
                elif group == "Group 1":
                    group_id = "1"
                else:  # FCC Down channels
                    group_id = "0"  # hack: fem com si fos 0 i despres canviem el primer byte
                channels_type = int(w_msg_version.GetValue())

                enabled_channels_map = 0
                if w_ch0_enabled.GetValue():
                    enabled_channels_map = enabled_channels_map | 0x80
                if w_ch1_enabled.GetValue():
                    enabled_channels_map = enabled_channels_map | 0x40
                if w_ch2_enabled.GetValue():
                    enabled_channels_map = enabled_channels_map | 0x20
                if w_ch3_enabled.GetValue():
                    enabled_channels_map = enabled_channels_map | 0x10
                if w_ch4_enabled.GetValue():
                    enabled_channels_map = enabled_channels_map | 0x08
                if w_ch5_enabled.GetValue():
                    enabled_channels_map = enabled_channels_map | 0x04
                if w_ch6_enabled.GetValue():
                    enabled_channels_map = enabled_channels_map | 0x02
                if w_ch7_enabled.GetValue():
                    enabled_channels_map = enabled_channels_map | 0x01

                ch_freq = [
                    int(w_ch0_freq.GetValue()),
                    int(w_ch1_freq.GetValue()),
                    int(w_ch2_freq.GetValue()),
                    int(w_ch3_freq.GetValue()),
                    int(w_ch4_freq.GetValue()),
                    int(w_ch5_freq.GetValue()),
                    int(w_ch6_freq.GetValue()),
                    int(w_ch7_freq.GetValue()),
                ]

                if 1 == channels_type:
                    drs = [int(e.GetValue(), 16) for e in w_ch_dr]
                    ch_freq = [f // 100 + (dr << 24) for f, dr in zip(ch_freq, drs)]

            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            try:
                print(
                    [
                        "java",
                        "-jar",
                        "jars/LoraChXCfg.jar",
                        group_id,
                        str(channels_type << 4),
                        str(enabled_channels_map),
                    ]
                    + [str(e) for e in ch_freq]
                )
                msg_str = Popen(
                    [
                        "java",
                        "-jar",
                        "jars/LoraChXCfg.jar",
                        group_id,
                        str(channels_type << 4),
                        str(enabled_channels_map),
                    ]
                    + [str(e) for e in ch_freq],
                    stdout=PIPE,
                )
                (output, err) = msg_str.communicate()
                msg_str.wait()
            except:
                msgb = wx.MessageDialog(
                    self, "Error executing jars/LoraChXCfg.jar", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return
            # change the amtype to LSAMTYPE_IN_LORA_FCC_DOWN_CH_CFG, as the java message is not done yet,
            # we use the one for group 0 and then change the amtype
            if group == "Group FCC Down":
                output = b"\\x8e" + output[4:]

            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(output, tty_usb, self)

        # method to request the config
        def request_grp0_config(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x00\\x85", tty_usb, self)

        def request_grp1_config(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x00\\x86", tty_usb, self)

        def request_fcc_down_config(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x00\\x8e", tty_usb, self)

        def set_custom_config(event):
            w_load_config.SetStringSelection("Custom")
            for e in w_ch_dr:
                e.Enable(1 == int(w_msg_version.GetValue()))
                e.SetValue("F0")

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 15
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        version_list = ["0", "1"]
        wx.StaticText(pnl, label="Version type", pos=(115, vertical_pos + 6))
        w_msg_version = wx.ComboBox(
            pnl, 500, value="0", size=(90, 30), pos=(20, vertical_pos), choices=version_list
        )
        w_msg_version.Bind(wx.EVT_TEXT, set_custom_config)
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
        w_ch3_enabled = wx.CheckBox(
            pnl, label="Ch3", pos=(20 + horizontal_pos_increment * 3, vertical_pos)
        )
        w_ch3_enabled.SetValue(True)

        vertical_pos = vertical_pos + vertical_pos_increment
        w_ch3_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_ch4_enabled = wx.CheckBox(
            pnl, label="Ch4", pos=(20 + horizontal_pos_increment * 0, vertical_pos)
        )
        w_ch4_enabled.SetValue(True)
        w_ch4_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_ch5_enabled = wx.CheckBox(
            pnl, label="Ch5", pos=(20 + horizontal_pos_increment * 1, vertical_pos)
        )
        w_ch5_enabled.SetValue(True)
        w_ch5_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_ch6_enabled = wx.CheckBox(
            pnl, label="Ch6", pos=(20 + horizontal_pos_increment * 2, vertical_pos)
        )
        w_ch6_enabled.SetValue(False)
        w_ch6_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        w_ch7_enabled = wx.CheckBox(
            pnl, label="Ch7", pos=(20 + horizontal_pos_increment * 3, vertical_pos)
        )
        w_ch7_enabled.SetValue(False)
        w_ch7_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        ch_vertical_pos = vertical_pos

        wx.StaticText(pnl, label="Ch0 Freq", pos=(115, vertical_pos + 6))
        w_ch0_freq = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_ch0_freq.SetMaxLength(10)
        w_ch0_freq.WriteText("820000000")
        w_ch0_freq.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Ch1 Freq", pos=(115, vertical_pos + 6))
        w_ch1_freq = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_ch1_freq.SetMaxLength(10)
        w_ch1_freq.WriteText("820000000")
        w_ch1_freq.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Ch2 Freq", pos=(115, vertical_pos + 6))
        w_ch2_freq = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_ch2_freq.SetMaxLength(10)
        w_ch2_freq.WriteText("820000000")
        w_ch2_freq.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Ch3 Freq", pos=(115, vertical_pos + 6))
        w_ch3_freq = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_ch3_freq.SetMaxLength(10)
        w_ch3_freq.WriteText("820000000")
        w_ch3_freq.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Ch4 Freq", pos=(115, vertical_pos + 6))
        w_ch4_freq = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_ch4_freq.SetMaxLength(10)
        w_ch4_freq.WriteText("820000000")
        w_ch4_freq.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Ch5 Freq", pos=(115, vertical_pos + 6))
        w_ch5_freq = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_ch5_freq.SetMaxLength(10)
        w_ch5_freq.WriteText("820000000")
        w_ch5_freq.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Ch6 Freq", pos=(115, vertical_pos + 6))
        w_ch6_freq = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_ch6_freq.SetMaxLength(10)
        w_ch6_freq.WriteText("820000000")
        w_ch6_freq.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Ch7 Freq", pos=(115, vertical_pos + 6))
        w_ch7_freq = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_ch7_freq.SetMaxLength(10)
        w_ch7_freq.WriteText("820000000")
        w_ch7_freq.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_ch_dr = []
        for i in range(8):
            wx.StaticText(
                pnl, label="DR", pos=(190, ch_vertical_pos + i * vertical_pos_increment + 6)
            )
            w = wx.TextCtrl(
                pnl, -1, size=(35, 30), pos=(210, ch_vertical_pos + i * vertical_pos_increment)
            )
            w.SetMaxLength(2)
            w.WriteText("F0")
            w_ch_dr.append(w)

        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(205, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        w_req_cfg_0_btn = wx.Button(
            pnl, label="Request Grp0 Cfg", pos=(300, vertical_pos - 2 * vertical_pos_increment)
        )
        w_req_cfg_0_btn.Bind(wx.EVT_BUTTON, request_grp0_config)

        w_req_cfg_1_btn = wx.Button(
            pnl, label="Request Grp1 Cfg", pos=(300, vertical_pos - vertical_pos_increment)
        )
        w_req_cfg_1_btn.Bind(wx.EVT_BUTTON, request_grp1_config)

        w_req_cfg_fcc_btn = wx.Button(pnl, label="Request FCC Down Cfg", pos=(300, vertical_pos))
        w_req_cfg_fcc_btn.Bind(wx.EVT_BUTTON, request_fcc_down_config)

        configs_list = ["Group 0", "Group 1", "Group FCC Down"]
        wx.StaticText(pnl, label="Group to configure", pos=(260, 10))
        w_group_num = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(260, 30),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_group_num.Bind(wx.EVT_COMBOBOX, load_config)
        w_group_num.SetStringSelection("Group 0")

        configs_list = [
            "Custom",
            "Default",
            "Test Default",
            "Singapore",
            "Malaysia",
            "FCC - 1",
            "FCC - 2",
            "FCC group 7",
            "923A",
            "926C",
            "866I",
            "LoraWAN EU868 (EU)",
            "LoraWAN US915 (FCC) 0-15",
            "LoraWAN AS923 (922S)",
            "LoraWAN AU915 (923A) 0-15",
            "FCC Down Ch Test",
            "923A Down",
        ]
        wx.StaticText(pnl, label="Load preset configs", pos=(260, 10 + 2 * vertical_pos_increment))
        w_load_config = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(260, 30 + 2 * vertical_pos_increment),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_load_config.Bind(wx.EVT_COMBOBOX, load_config)
        w_load_config.SetStringSelection("Test Default")
        load_config(0)

        vertical_pos = vertical_pos + vertical_pos_increment
        self.SetSize((480, vertical_pos + vertical_pos_increment))
        self.SetTitle("LoRaChXCfg")
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
