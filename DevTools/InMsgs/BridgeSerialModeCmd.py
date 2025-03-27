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
                w_modeid.SetValue("0")
                w_baudrate.SetValue("115200")
                w_databits.SetValue("8")
                w_stopbits.SetValue("1")
                w_parity.SetValue("No")
                w_guardtime.SetValue("100")
                w_charseq.SetValue("+++")
                w_disctimeout.SetValue("10")
                w_inactimeout.SetValue("10")

            # update on textctrls change the drop down to custom, change it back
            w_load_config.SetStringSelection(config)

        # method to set the config
        def send_command(event):
            def w_stopbits_to_int(w_sb):
                if w_sb == "0.5":
                    return 0
                elif w_sb == "1":
                    return 1
                elif w_sb == "1.5":
                    return 2
                elif w_sb == "2":
                    return 3
                else:
                    raise Exception("w_stopbits_to_int no value")

            def w_parity_to_int(w_p):
                if w_p == "No":
                    return 0
                elif w_p == "Even":
                    return 1
                elif w_p == "Odd":
                    return 2
                else:
                    raise Exception("w_parity_to_int no value")

            def w_charseq_to_hex(w_c):
                char_len = len(w_c)
                out = ""
                if char_len == 0 or char_len > 3:
                    raise Exception("Invalid exit char sequence")
                for a in w_c:
                    out += "%0.2X" % ord(a)
                # Fill the remaining positions if necessary
                for i in range(char_len, 3):
                    out += "00"
                return out, char_len

            try:
                modeid = int(w_modeid.GetValue())
                baudrate = int(w_baudrate.GetValue())
                databits = int(w_databits.GetValue())
                stopbits = w_stopbits_to_int(w_stopbits.GetValue())
                parity = w_parity_to_int(w_parity.GetValue())
                guardtime = int(w_guardtime.GetValue())
                charseqhex, charseqlen = w_charseq_to_hex(w_charseq.GetValue())
                disctimeout = int(w_disctimeout.GetValue())
                inactimeout = int(w_inactimeout.GetValue())
                # command = int(w_command.GetValue());
                # dig_subtype = w_typeSensors_to_int(w_type_sensors.GetValue())
            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            try:
                stopbitandparity = (stopbits & 0x03) | ((parity & 0x03) << 2)

                output = (
                    "12"
                    + "%0.2X" % modeid
                    + "%0.8X" % baudrate
                    + "%0.2X" % databits
                    + "%0.2X" % stopbitandparity
                    + "%0.4X" % guardtime
                    + charseqhex
                    + "%0.2X" % charseqlen
                    + "%0.4X" % disctimeout
                    + "%0.4X" % inactimeout
                )
                output = "\\x" + "\\x".join(a + b for a, b in zip(output[::2], output[1::2]))
            except:
                msgb = wx.MessageDialog(
                    self, "Error creating message", "ERROR", wx.OK | wx.ICON_HAND
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

        wx.StaticText(pnl, label="ModeId", pos=(115, vertical_pos + 6))
        w_modeid = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_modeid.SetMaxLength(3)
        w_modeid.WriteText("0")
        w_modeid.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        baud_rate_list = [
            "300",
            "600",
            "1200",
            "2400",
            "4800",
            "9600",
            "19200",
            "38400",
            "57600",
            "115200",
        ]
        wx.StaticText(pnl, label="Baud Rate", pos=(115, vertical_pos + 6))
        w_baudrate = wx.ComboBox(
            pnl, 500, value="1", size=(90, 30), pos=(20, vertical_pos), choices=baud_rate_list
        )
        w_baudrate.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        data_bits_list = ["8", "9"]
        wx.StaticText(pnl, label="Data Bits", pos=(115, vertical_pos + 6))
        w_databits = wx.ComboBox(
            pnl, 500, value="1", size=(90, 30), pos=(20, vertical_pos), choices=data_bits_list
        )
        w_databits.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        stop_bits_list = ["0.5", "1", "1.5", "2"]
        wx.StaticText(pnl, label="Stop Bits", pos=(115, vertical_pos + 6))
        w_stopbits = wx.ComboBox(
            pnl, 500, value="1", size=(90, 30), pos=(20, vertical_pos), choices=stop_bits_list
        )
        w_stopbits.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        parity_list = ["No", "Even", "Odd"]
        wx.StaticText(pnl, label="Parity", pos=(115, vertical_pos + 6))
        w_parity = wx.ComboBox(
            pnl, 500, value="1", size=(90, 30), pos=(20, vertical_pos), choices=parity_list
        )
        w_parity.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Exit GuardTimeMiliSec", pos=(115, vertical_pos + 6))
        w_guardtime = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_guardtime.SetMaxLength(5)
        w_guardtime.WriteText("100")
        w_guardtime.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="Exit Char sequence", pos=(115, vertical_pos + 6))
        w_charseq = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_charseq.SetMaxLength(3)
        w_charseq.WriteText("+++")
        w_charseq.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="CableDisconnectionTimeoutSec", pos=(115, vertical_pos + 6))
        w_disctimeout = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_disctimeout.SetMaxLength(5)
        w_disctimeout.WriteText("10")
        w_disctimeout.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        wx.StaticText(pnl, label="InactivityTimeoutSec", pos=(115, vertical_pos + 6))
        w_inactimeout = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_inactimeout.SetMaxLength(5)
        w_inactimeout.WriteText("10")
        w_inactimeout.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos = vertical_pos + vertical_pos_increment

        w_send_cmd = wx.Button(
            pnl, label="Send Command", size=(120, 30), pos=(500 - (120 + 6), vertical_pos)
        )
        w_send_cmd.Bind(wx.EVT_BUTTON, send_command)

        configs_list = ["Custom", "Default"]
        wx.StaticText(pnl, label="Load preset configs", pos=(300, 26))
        w_load_config = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(500 - (200 + 6), 26 + vertical_pos_increment - 10),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_load_config.Bind(wx.EVT_COMBOBOX, load_config)
        w_load_config.SetStringSelection("Default")
        load_config(0)

        self.SetSize((500, vertical_pos + (vertical_pos_increment * 3)))
        self.SetTitle("Bridge Serial Mode Cmd")
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
