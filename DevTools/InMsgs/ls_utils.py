from subprocess import PIPE, Popen

import wx

use_socket = False
server_ip = "192.168.1.1"


def ls_send_message_uart(message, tty, panel):
    global use_socket
    global server_ip

    print(message)
    try:
        if use_socket is False:
            send_msg_uart = Popen(["../lib/ls_send_message_uart", message, tty], stdout=PIPE)
        else:
            send_msg_uart = Popen(
                ["../lib/ls_send_message_uart", message, tty, "-s", server_ip], stdout=PIPE
            )
        (output, err) = send_msg_uart.communicate()
        exit_code = send_msg_uart.wait()
        if 0 != exit_code:
            msgb = wx.MessageDialog(
                panel,
                "Error executing ../lib/ls_send_message_uart: " + output,
                "ERROR",
                wx.OK | wx.ICON_HAND,
            )
            msgb.ShowModal()
            return False
    except:
        msgb = wx.MessageDialog(
            panel, "Error executing ../lib/ls_send_message_uart", "ERROR", wx.OK | wx.ICON_HAND
        )
        msgb.ShowModal()
        return False

    return True
