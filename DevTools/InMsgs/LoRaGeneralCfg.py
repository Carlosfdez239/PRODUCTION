#!/usr/bin/env python3
import os
import sys

import bitstring
import wx
from ls_utils import ls_send_message_uart

global_tty = ""


AM_TYPE = 0x84

MAC_VERSIONS = {
    "EU868_V1": 0,
    "EU868_WAN_V1_0": 1,
    "US915_V1": 2,
    "US915_WAN_V1_0": 3,
    "AS923_WAN_V1_0": 4,
    "AS925_WAN_V1_0": 5,
    "AU915_WAN_V1_0": 6,
}

MSG_VERSIONS = [0, 1]

MSG_VERSION_0_BITSTRING_FORMAT = (
    "uint:8, uint:4, uint:4, 4*bool, uint:4, uint:8, pad:3, bool, uint:4, uint:32, uint:16"
)

MSG_VERSION_1_BITSTRING_FORMAT = (
    "uint:8, uint:4, uint:4, 4*bool, uint:4, uint:8, pad:2, bool, bool, uint:4, uint:32, uint:16"
)


class Example(wx.Frame):
    def __init__(self, *args, **kw):
        super(Example, self).__init__(*args, **kw)

        self.init_ui()

    def init_ui(self):
        global global_tty

        def load_config(event):
            config = w_load_config.GetValue()

            if config == "Default":
                w_msg_version.SetValue("0")
                w_mac_version.SetValue("EU868_V1")
                w_use_500khz_ch.SetValue(False)
                w_radio_enabled.SetValue(False)
                w_etsi_enabled.SetValue(True)
                w_adr_enabled.SetValue(True)
                w_sf.SetValue("9")
                w_tx_power.SetValue("14")
                w_ch_dc_en.SetValue(False)
                w_ch_dc_en.Disable()
                w_use_rx2.SetValue(False)
                w_rx2_sf.SetValue("12")
                w_rx2_freq.SetValue("869525000")
                w_slot_time.SetValue("300")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Test Default":
                w_msg_version.SetValue("0")
                w_mac_version.SetValue("EU868_V1")
                w_use_500khz_ch.SetValue(False)
                w_radio_enabled.SetValue(True)
                w_etsi_enabled.SetValue(False)
                w_adr_enabled.SetValue(True)
                w_sf.SetValue("9")
                w_tx_power.SetValue("14")
                w_ch_dc_en.SetValue(False)
                w_ch_dc_en.Disable()
                w_use_rx2.SetValue(False)
                w_rx2_sf.SetValue("12")
                w_rx2_freq.SetValue("820000000")
                w_slot_time.SetValue("15")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Default FCC":
                w_msg_version.SetValue("0")
                w_mac_version.SetValue("US915_V1")
                w_use_500khz_ch.SetValue(False)
                w_radio_enabled.SetValue(False)
                w_etsi_enabled.SetValue(False)
                w_adr_enabled.SetValue(True)
                w_sf.SetValue("8")
                w_tx_power.SetValue("20")
                w_ch_dc_en.SetValue(False)
                w_ch_dc_en.Disable()
                w_use_rx2.SetValue(False)
                w_rx2_sf.SetValue("12")
                w_rx2_freq.SetValue("820000000")
                w_slot_time.SetValue("300")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

            elif config == "Test Default FCC":
                w_msg_version.SetValue("0")
                w_mac_version.SetValue("US915_V1")
                w_use_500khz_ch.SetValue(False)
                w_radio_enabled.SetValue(True)
                w_etsi_enabled.SetValue(False)
                w_adr_enabled.SetValue(True)
                w_sf.SetValue("8")
                w_tx_power.SetValue("20")
                w_ch_dc_en.SetValue(False)
                w_ch_dc_en.Disable()
                w_use_rx2.SetValue(False)
                w_rx2_sf.SetValue("12")
                w_rx2_freq.SetValue("820000000")
                w_slot_time.SetValue("15")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        # method to set the config
        def set_config(event):

            try:
                msg_version = int(w_msg_version.GetValue())
                mac_version = int(MAC_VERSIONS[w_mac_version.GetValue()])
                use_500khz_ch = int(w_use_500khz_ch.GetValue())
                radio_enabled = int(w_radio_enabled.GetValue())
                etsi_enabled = int(w_etsi_enabled.GetValue())
                adr_enabled = int(w_adr_enabled.GetValue())
                sf = int(w_sf.GetValue())
                tx_power = int(w_tx_power.GetValue())
                ch_dc_en = int(w_ch_dc_en.GetValue())
                use_rx2 = int(w_use_rx2.GetValue())
                rx2_sf = int(w_rx2_sf.GetValue())
                rx2_freq = int(w_rx2_freq.GetValue())
                slot_time = int(w_slot_time.GetValue())
            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            try:

                if msg_version == 0:

                    msg_str = "".join(
                        [
                            "\\x{:02x}".format(e)
                            for e in bitstring.pack(
                                MSG_VERSION_0_BITSTRING_FORMAT,
                                AM_TYPE,
                                msg_version,
                                mac_version,
                                use_500khz_ch,
                                radio_enabled,
                                etsi_enabled,
                                adr_enabled,
                                sf,
                                tx_power,
                                use_rx2,
                                rx2_sf,
                                rx2_freq,
                                slot_time,
                            ).bytes
                        ]
                    )
                else:

                    msg_str = "".join(
                        [
                            "\\x{:02x}".format(e)
                            for e in bitstring.pack(
                                MSG_VERSION_1_BITSTRING_FORMAT,
                                AM_TYPE,
                                msg_version,
                                mac_version,
                                use_500khz_ch,
                                radio_enabled,
                                etsi_enabled,
                                adr_enabled,
                                sf,
                                tx_power,
                                ch_dc_en,
                                use_rx2,
                                rx2_sf,
                                rx2_freq,
                                slot_time,
                            ).bytes
                        ]
                    )

            except:
                msgb = wx.MessageDialog(
                    self, "Error packing the message", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(msg_str, tty_usb, self)

        # method to request the config
        def request_config(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x00\\x84", tty_usb, self)

        def set_custom_config(event):
            w_load_config.SetStringSelection("Custom")

        def enable_channel_duty_cycle_restriction(event):
            try:
                msg_version = int(w_msg_version.GetValue())

                if msg_version == 0:
                    w_ch_dc_en.Disable()
                else:
                    w_ch_dc_en.Enable()
            except:
                msgb = wx.MessageDialog(
                    self, "Msg version is not an integer.", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        msg_version_string_list = [str(a) for a in MSG_VERSIONS]
        wx.StaticText(pnl, label="Msg Ver.", pos=(190, vertical_pos + 6))
        w_msg_version = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(165, 30),
            pos=(20, vertical_pos),
            choices=msg_version_string_list,
            style=wx.CB_READONLY,
        )
        w_msg_version.Bind(wx.EVT_TEXT, set_custom_config)
        w_msg_version.Bind(wx.EVT_TEXT, enable_channel_duty_cycle_restriction)
        vertical_pos = vertical_pos + vertical_pos_increment

        mac_version_list = [e[0] for e in sorted(list(MAC_VERSIONS.items()), key=lambda e: e[1])]
        wx.StaticText(pnl, label="MAC Ver.", pos=(190, vertical_pos + 6))
        w_mac_version = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(165, 30),
            pos=(20, vertical_pos),
            choices=mac_version_list,
            style=wx.CB_READONLY,
        )
        w_mac_version.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_use_500khz_ch = wx.CheckBox(pnl, label="Use 500kHz Ch", pos=(92, vertical_pos))
        w_use_500khz_ch.SetValue(False)
        w_use_500khz_ch.Bind(wx.EVT_CHECKBOX, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_radio_enabled = wx.CheckBox(pnl, label="Radio Enabled", pos=(92, vertical_pos))
        w_radio_enabled.SetValue(True)
        w_radio_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_etsi_enabled = wx.CheckBox(pnl, label="ETSI Enabled", pos=(92, vertical_pos))
        w_etsi_enabled.SetValue(True)
        w_etsi_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_adr_enabled = wx.CheckBox(pnl, label="ADR Enabled", pos=(92, vertical_pos))
        w_adr_enabled.SetValue(True)
        w_adr_enabled.Bind(wx.EVT_CHECKBOX, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        sf_list = ["6", "7", "8", "9", "10", "11", "12", "13"]
        wx.StaticText(pnl, label="SF", pos=(115, vertical_pos + 6))
        w_sf = wx.ComboBox(
            pnl, 500, value="9", size=(90, 30), pos=(20, vertical_pos), choices=sf_list
        )
        w_sf.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        tx_power_list = [
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
        ]
        wx.StaticText(pnl, label="Tx Power", pos=(115, vertical_pos + 6))
        w_tx_power = wx.ComboBox(
            pnl, 500, value="14", size=(90, 30), pos=(20, vertical_pos), choices=tx_power_list
        )
        w_tx_power.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_ch_dc_en = wx.CheckBox(
            pnl, label="Channel Duty Cycle Restriction", pos=(92, vertical_pos)
        )
        w_ch_dc_en.SetValue(False)
        w_ch_dc_en.Bind(wx.EVT_CHECKBOX, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_use_rx2 = wx.CheckBox(pnl, label="Use Rx2", pos=(92, vertical_pos))
        w_use_rx2.SetValue(False)
        w_use_rx2.Bind(wx.EVT_CHECKBOX, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Rx2 SF", pos=(115, vertical_pos + 6))
        w_rx2_sf = wx.ComboBox(
            pnl, 500, value="7", size=(90, 30), pos=(20, vertical_pos), choices=sf_list
        )
        w_rx2_sf.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Rx2 Freq", pos=(115, vertical_pos + 6))
        w_rx2_freq = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_rx2_freq.SetMaxLength(10)
        w_rx2_freq.WriteText("820000000")
        w_rx2_freq.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Slot Time", pos=(115, vertical_pos + 6))
        w_slot_time = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_slot_time.SetMaxLength(10)
        w_slot_time.WriteText("15")
        w_slot_time.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(260, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        w_set_config_btn = wx.Button(pnl, label="Request Config", pos=(370, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_config)

        configs_list = ["Custom", "Default", "Test Default", "Default FCC", "Test Default FCC"]
        wx.StaticText(pnl, label="Load preset configs", pos=(300, 30))
        w_load_config = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(160, 30),
            pos=(300, 30 + vertical_pos_increment),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_load_config.Bind(wx.EVT_COMBOBOX, load_config)
        w_load_config.SetStringSelection("Test Default")
        vertical_pos = vertical_pos + vertical_pos_increment
        load_config(0)

        self.SetSize((520, vertical_pos + vertical_pos_increment + 20))
        self.SetTitle("LoRaGeneralCfg")
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
        print(("Usage" + os.path.basename(__file__) + " [serial_tty] [-s IP]"))
        sys.exit(1)

    ex = wx.App()
    Example(None)
    ex.MainLoop()


if __name__ == "__main__":
    main()
