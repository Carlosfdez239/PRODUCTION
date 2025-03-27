#!/usr/bin/env python3

import argparse

import wx
from ls_utils import ls_send_message_uart
from wx_utils import DualConfigPanel


def format_bytestring(hex_string):
    """Convert a hex string to a formatted byte string with double backslashes."""
    return "".join(f"\\x{byte:02X}" for byte in bytes.fromhex(hex_string))


class LSBaseTool(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(LSBaseTool, self).__init__(*args, **kwargs)
        self.global_tty = ""
        self.use_socket = False
        self.server_ip = ""
        self.msg_type = ""
        self.am_type_hex = ""

    def init_ui(self, title="Example", left_panel_parameters=[], right_panel_parameters=[]):
        """Initialize the UI components."""
        self.SetTitle(title)

        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create and add DualConfigPanel
        self.content = DualConfigPanel(self, panel, left_panel_parameters, right_panel_parameters)
        main_sizer.Add(self.content, flag=wx.EXPAND | wx.ALL, border=10)

        panel.SetSizer(main_sizer)

        self.bind_events()
        self.Layout()
        self.Fit()
        self.Centre()

    def bind_events(self):
        """Bind events to UI components."""
        self.content.w_get_config_btn.Bind(wx.EVT_BUTTON, self.on_request_config)
        self.content.w_set_config_btn.Bind(wx.EVT_BUTTON, self.on_set_config)

    def on_set_config(self, event):
        """Handle setting configuration to the node."""
        tty = self.get_tty()
        mote_msg = self.build_config_binary()
        if mote_msg:
            self.send_msg_to_node(tty, mote_msg)

    def on_request_config(self, event):
        """Handle requesting configuration from the node."""
        tty = self.get_tty()
        output = f"\\x00\\x{self.am_type_hex}"
        ls_send_message_uart(output, tty, self)

    def load_default(self, event):
        """Reset the configuration inputs to their default values."""
        for config_item in (
            self.content.default_config["left"] + self.content.default_config["right"]
        ):
            component = self.content.config_inputs[config_item.name]
            component.set_value(config_item.default)

    def get_tty(self):
        """Retrieve the tty device path."""
        return f"/dev/ttyUSB{self.content.usb.get_value()}"

    def build_config_binary(self):
        """Build the configuration binary message."""
        raise NotImplementedError("This method should be implemented in a subclass.")

    def send_msg_to_node(self, tty, msg, format=True):
        """Send a message to the node."""
        if format:
            byte_string = format_bytestring(msg)
        else:
            byte_string = msg

        ls_send_message_uart(byte_string, tty, self)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="LS Serial DevTool for configuring nodes.")
    parser.add_argument(
        "tty",
        nargs="?",
        default="/dev/ttyUSB0",
        help="Serial TTY (default: /dev/ttyUSB0)",
    )
    parser.add_argument("-s", "--server", type=str, help="Server IP address")
    return parser.parse_args()


def main(app_class):
    """Main function to start the application."""
    args = parse_arguments()

    app = wx.App()
    frame = app_class(None)
    frame.global_tty = args.tty
    if args.server:
        frame.use_socket = True
        frame.server_ip = args.server
    frame.Show()
    app.MainLoop()
