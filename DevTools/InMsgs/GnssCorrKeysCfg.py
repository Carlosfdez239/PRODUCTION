#!/usr/bin/env python3

import sys

sys.path.append("../lib/")
import ls_json2msg
import wx
from ls_base import LSBaseTool, main
from wx_utils import ConfigType, LSConfigParam


class GnssCorrKeysCfgTool(LSBaseTool):
    MSG_TYPE = "SetGnssCorrKeysCfgV1"
    AM_TYPE_HEX = "A2"

    CONFIG_INPUT = {
        "cryptKey": LSConfigParam("CryptKey", "BCD93C64D7AD221E21C7D40BCE1B163B", ConfigType.FIELD),
        "signKey": LSConfigParam("SignKey", "F043374EB889A25268B944E4231D68E2", ConfigType.FIELD),
    }

    LEFT_PANEL_PARAMETERS = [
        CONFIG_INPUT["cryptKey"],
        CONFIG_INPUT["signKey"],
    ]

    def __init__(self, *args, **kwargs):
        super(GnssCorrKeysCfgTool, self).__init__(*args, **kwargs)
        self.msg_type = self.MSG_TYPE
        self.am_type_hex = self.AM_TYPE_HEX
        self.init_ui("GNSS Correction Keys Config", self.LEFT_PANEL_PARAMETERS, [])

    def build_config_binary(self):
        """Build the configuration binary message."""
        cfg = {
            key: self.content.config_inputs[param.name].get_value()
            for key, param in self.CONFIG_INPUT.items()
        }

        if cfg["cryptKey"] == 0:
            cfg["cryptKey"] = "00000000000000000000000000000000"

        if cfg["signKey"] == 0:
            cfg["signKey"] = "00000000000000000000000000000000"

        try:
            crypt_key = cfg["cryptKey"]
            sign_key = cfg["signKey"]
        except:
            msgb = wx.MessageDialog(
                self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
            )
            msgb.ShowModal()
            return

        try:
            config_json = {
                "type": self.msg_type,
                "version": 0,
                "cryptKey": crypt_key,
                "signKey": sign_key,
            }
            print(config_json)
            return ls_json2msg.json2msg(config_json)
        except:
            msgb = wx.MessageDialog(
                self,
                "Error executing the parsing library",
                "ERROR",
                wx.OK | wx.ICON_HAND,
            )
            msgb.ShowModal()
            return None


if __name__ == "__main__":
    main(GnssCorrKeysCfgTool)
