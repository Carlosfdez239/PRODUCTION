#!/usr/bin/env python3
import os
import struct
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

        def get_input():
            try:
                version = 0
                node_id = int(w_node_id.GetValue())
            except Exception:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return [None] * 2
            return version, node_id

        def send_msg(byte_values):
            output = "".join(["\\x{:02X}".format(e) for e in byte_values])
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(output, tty_usb, self)

        # method to set the config
        def set_config_v1(event):
            version, node_id = get_input()
            if version is None:
                return

            byte_values = [0x7]
            byte_values += list(struct.pack(">I", 0xBA6512FA))
            byte_values += list(struct.pack(">H", node_id))
            send_msg(byte_values)

        def set_config_v2(event):
            version, node_id = get_input()
            if version is None:
                return

            byte_values = [0x14]
            byte_values += list(struct.pack(">I", 0xBA6512FA))
            byte_values += [version << 6]
            byte_values += list(struct.pack(">I", node_id))
            send_msg(byte_values)

        def get_node_info(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x43\\x69\\x00\\x00", tty_usb, self)

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Node ID", pos=(115, vertical_pos + 6))
        w_node_id = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_node_id.SetMaxLength(10)
        w_node_id.WriteText("1800")
        vertical_pos = vertical_pos + vertical_pos_increment

        w_set_config_btn = wx.Button(pnl, label="Set IDs<65k", pos=(20, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config_v1)

        w_set_config_btn = wx.Button(pnl, label="Set IDs>65k", pos=(120, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config_v2)

        w_set_config_btn = wx.Button(pnl, label="Get Node Info", pos=(225, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, get_node_info)
        vertical_pos += vertical_pos_increment

        self.SetSize((340, vertical_pos + vertical_pos_increment))
        self.SetTitle("SetNodeId")
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
