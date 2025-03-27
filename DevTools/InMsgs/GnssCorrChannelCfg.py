#!/usr/bin/env python3
import sys

sys.path.append("../lib/")
import ls_json2msg
from ls_base import LSBaseTool, main  # Import the base class and main function
from wx_utils import ConfigType, LSConfigParam


class GnssCorrChCfgTool(LSBaseTool):
    MSG_TYPE = "SetGnssCorrChCfgV1"
    AM_TYPE_HEX = "A3"

    CONFIG_INPUT = {
        "channels": [
            LSConfigParam(
                name="CH0",
                default=(True, 868100000),
                config_type=ConfigType.CHANNEL,
                id=0,
                value_key="frequency",
            ),
            LSConfigParam(
                name="CH1",
                default=(True, 868300000),
                config_type=ConfigType.CHANNEL,
                id=1,
                value_key="frequency",
            ),
            LSConfigParam(
                name="CH2",
                default=(True, 868500000),
                config_type=ConfigType.CHANNEL,
                id=2,
                value_key="frequency",
            ),
            LSConfigParam(
                name="CH3",
                default=(True, 869525000),
                config_type=ConfigType.CHANNEL,
                id=3,
                value_key="frequency",
            ),
            LSConfigParam(
                name="CH4",
                default=(True, 869850000),
                config_type=ConfigType.CHANNEL,
                id=4,
                value_key="frequency",
            ),
            LSConfigParam(
                name="CH5",
                default=(True, 865300000),
                config_type=ConfigType.CHANNEL,
                id=5,
                value_key="frequency",
            ),
            LSConfigParam(
                name="CH6",
                default=(True, 866000000),
                config_type=ConfigType.CHANNEL,
                id=6,
                value_key="frequency",
            ),
            LSConfigParam(
                name="CH7",
                default=(True, 866700000),
                config_type=ConfigType.CHANNEL,
                id=7,
                value_key="frequency",
            ),
        ],
        "txPower": LSConfigParam(name="TxPower", default=14, config_type=ConfigType.FIELD),
    }

    LEFT_PANEL_PARAMETERS = [
        CONFIG_INPUT["channels"][0],
        CONFIG_INPUT["channels"][1],
        CONFIG_INPUT["channels"][2],
        CONFIG_INPUT["channels"][3],
        CONFIG_INPUT["txPower"],
    ]

    RIGHT_PANEL_PARAMETERS = [
        CONFIG_INPUT["channels"][4],
        CONFIG_INPUT["channels"][5],
        CONFIG_INPUT["channels"][6],
        CONFIG_INPUT["channels"][7],
    ]

    def __init__(self, *args, **kwargs):
        super(GnssCorrChCfgTool, self).__init__(*args, **kwargs)
        self.msg_type = self.MSG_TYPE
        self.am_type_hex = self.AM_TYPE_HEX
        self.init_ui(
            "Corrections Channel Config", self.LEFT_PANEL_PARAMETERS, self.RIGHT_PANEL_PARAMETERS
        )

    def build_config_binary(self):
        """Build the configuration binary message."""
        channels = [
            self.content.config_inputs[ch.name].get_value() for ch in self.CONFIG_INPUT["channels"]
        ]
        tx_power = self.content.config_inputs[self.CONFIG_INPUT["txPower"].name].get_value()
        config_json = {
            "type": self.msg_type,
            "version": 0,
            "channels": channels,
            "txPower": tx_power,
        }

        return ls_json2msg.json2msg(config_json)


if __name__ == "__main__":
    main(GnssCorrChCfgTool)
