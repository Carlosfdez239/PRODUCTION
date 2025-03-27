#!/usr/bin/env python3
import hashlib
import os
import sys
from subprocess import PIPE, Popen

import wx
from ls_utils import ls_send_message_uart

# Following seeds are the defaults for generating the encryption keys on the
# gateway.
sign_salt = "lpvid433J17WI9qM"
crypt_salt = "wu5FJtk22T29W9nw"


class Example(wx.Frame):
    def __init__(self, *args, **kw):
        super(Example, self).__init__(*args, **kw)

        self.init_ui()

    def init_ui(self):
        global global_tty

        def load_config(event):
            config = w_load_config.GetValue()

            if config == "Default":
                w_net_id.SetValue("0")
                w_net_pass.SetValue("test")

                # update on textctrls change the drop down to custom, change it back
                w_load_config.SetStringSelection(config)

        # method to set the config
        def set_config_crc_no_ok(event):
            set_config(False)

        def set_config_crc_ok(event):
            set_config(True)

        def get_signkey(netid, netpass):
            seed = (netid + netpass + sign_salt).encode("utf-8")
            return hashlib.sha1(seed).hexdigest()[
                :32
            ]  # keys are 16 bytes, so its 32 hex characters

        def get_cryptkey(netid, netpass):
            seed = (netid + netpass + crypt_salt).encode("utf-8")
            return hashlib.sha1(seed).hexdigest()[
                :32
            ]  # keys are 16 bytes, so its 32 hex characters

        def set_config(crc_ok):
            try:
                net_id = int(w_net_id.GetValue())
                net_pass = w_net_pass.GetValue()
                net_key = get_signkey(str(net_id), net_pass)
                app_key = get_cryptkey(str(net_id), net_pass)
                print("Password:{}\nNet_key:{}\nApp_key:{}\n".format(net_pass, net_key, app_key))

            except ValueError:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            try:
                msg_str = Popen(
                    ["java", "-jar", "jars/LoraKeysCfg.jar", net_key, app_key, str(net_id)],
                    stdout=PIPE,
                )
                (output, err) = msg_str.communicate()
                msg_str.wait()
            except:
                msgb = wx.MessageDialog(
                    self, "Error executing jars/LoraKeysCfg.jar", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            if crc_ok is False:
                output = output[: len(output) - 8] + b"\x00\x01"

            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(output, tty_usb, self)

        # method to request the config
        def request_config(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x00\\x8D", tty_usb, self)

        def set_custom_config(event):
            w_load_config.SetStringSelection("Custom")

        tty_prefix = "/dev/ttyUSB"
        vertical_pos_increment = 35
        vertical_pos = 10 + vertical_pos_increment

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Net Id", pos=(115, vertical_pos + 6))
        w_net_id = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_net_id.SetMaxLength(10)
        w_net_id.WriteText("")
        w_net_id.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Password", pos=(295, vertical_pos + 6))
        w_net_pass = wx.TextCtrl(pnl, -1, size=(270, 30), pos=(20, vertical_pos))
        w_net_pass.SetMaxLength(32)
        w_net_pass.WriteText("")
        w_net_pass.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_wrong_crc_btn = wx.Button(pnl, label="Set config with wrong CRC", pos=(20, vertical_pos))
        w_wrong_crc_btn.Bind(wx.EVT_BUTTON, set_config_crc_no_ok)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(260, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config_crc_ok)

        w_set_config_btn = wx.Button(pnl, label="Request Config", pos=(350, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_config)

        vertical_pos = vertical_pos + vertical_pos_increment

        configs_list = ["Default"]
        wx.StaticText(pnl, label="Load preset configs", pos=(260, 10))
        w_load_config = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(260, 30),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_load_config.Bind(wx.EVT_COMBOBOX, load_config)
        w_load_config.SetStringSelection("Default")
        load_config(0)

        self.SetSize((500, vertical_pos + vertical_pos_increment + 15))
        self.SetTitle("LoRaPassword")
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
