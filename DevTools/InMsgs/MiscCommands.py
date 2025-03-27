#!/usr/bin/env python3
import os
import sys
import uuid

import wx
from ls_utils import ls_send_message_uart


class Example(wx.Frame):
    def __init__(self, *args, **kw):
        super(Example, self).__init__(*args, **kw)

        self.init_ui()

    def init_ui(self):
        global global_tty

        # method to set the time
        def send_command(command):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(command, tty_usb, self)

        def get_health(event):
            send_command("\\x01")

        def get_data(event):
            send_command("\\x02")

        def get_node_info(event):
            send_command("\\x43\\x69\\x00\\x00")

        def get_extended_node_info(event):
            send_command("\\x0E")

        def do_coverage_test(event):
            random_hex_string = uuid.uuid4().hex
            token = (
                "\\x"
                + random_hex_string[:2]
                + "\\x"
                + random_hex_string[2:4]
                + "\\x"
                + random_hex_string[4:6]
                + "\\x"
                + random_hex_string[6:8]
            )
            send_command("\\x0A" + token)  # \\xAA\\xBB\\xCC\\xDD")
            print("Token:", token)

        def recover_all_data(event):
            send_command("\\x03\\x00\\x00\\x00\\x00\\x00\\xFF\\xFF\\xFF\\xFF")

        def reboot(event):
            send_command("\\x09")

        def factory_reset(event):
            msgb = wx.MessageDialog(
                self, "Are you sure?", "WARNING", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION
            )
            msgbox_response = msgb.ShowModal() == wx.ID_YES
            if msgbox_response:
                send_command("\\x08\\x75\\xB5\\x44\\xA2")

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        w_get_health_btn = wx.Button(pnl, label="Get health", pos=(20, vertical_pos))
        w_get_health_btn.Bind(wx.EVT_BUTTON, get_health)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_get_data_btn = wx.Button(pnl, label="Get data", pos=(20, vertical_pos))
        w_get_data_btn.Bind(wx.EVT_BUTTON, get_data)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_recover_data_btn = wx.Button(pnl, label="Recover all data", pos=(20, vertical_pos))
        w_recover_data_btn.Bind(wx.EVT_BUTTON, recover_all_data)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_get_node_info_btn = wx.Button(pnl, label="Get node info", pos=(20, vertical_pos))
        w_get_node_info_btn.Bind(wx.EVT_BUTTON, get_node_info)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_get_node_info_btn = wx.Button(pnl, label="Get ext. node info", pos=(20, vertical_pos))
        w_get_node_info_btn.Bind(wx.EVT_BUTTON, get_extended_node_info)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_coverage_test_btn = wx.Button(pnl, label="Do Coverage Test", pos=(20, vertical_pos))
        w_coverage_test_btn.Bind(wx.EVT_BUTTON, do_coverage_test)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_reboot_btn = wx.Button(pnl, label="Reboot", pos=(20, vertical_pos))
        w_reboot_btn.Bind(wx.EVT_BUTTON, reboot)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_factory_reset_btn = wx.Button(pnl, label="Factory reset", pos=(20, vertical_pos))
        w_factory_reset_btn.Bind(wx.EVT_BUTTON, factory_reset)
        vertical_pos = vertical_pos + vertical_pos_increment

        vertical_pos = vertical_pos + vertical_pos_increment
        self.SetSize((230, vertical_pos + 6))
        self.SetTitle("LSMiscCommands")
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
