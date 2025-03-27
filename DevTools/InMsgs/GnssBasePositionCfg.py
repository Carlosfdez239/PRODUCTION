#!/usr/bin/env python3

import sys

sys.path.append("../lib/")
import ls_json2msg
from ls_base import LSBaseTool, main
from wx_utils import ConfigType, LSConfigParam


class GnssBasePositionCfgTool(LSBaseTool):
    MSG_TYPE = "SetGnssBasePositionCfgV1"
    AM_TYPE_HEX = "A1"

    CONFIG_INPUT = {
        "position": {
            "latitude": LSConfigParam("Latitude (deg)", 0, ConfigType.FIELD),
            "longitude": LSConfigParam("Longitude (deg)", 0, ConfigType.FIELD),
            "altitude": LSConfigParam("Altitude (m)", 0, ConfigType.FIELD),
        },
        "accuracy": LSConfigParam("Accuracy (mm)", 15, ConfigType.FIELD),
        "invalidationDate": LSConfigParam("Invalidation date", None, ConfigType.DATE),
        "baseNodeId": LSConfigParam("Base ID", 0, ConfigType.FIELD),
    }

    PANEL_PARAMETERS = [
        CONFIG_INPUT["position"]["latitude"],
        CONFIG_INPUT["position"]["longitude"],
        CONFIG_INPUT["position"]["altitude"],
        CONFIG_INPUT["accuracy"],
        CONFIG_INPUT["invalidationDate"],
        CONFIG_INPUT["baseNodeId"],
    ]

    def __init__(self, *args, **kwargs):
        super(GnssBasePositionCfgTool, self).__init__(*args, **kwargs)
        self.msg_type = self.MSG_TYPE
        self.am_type_hex = self.AM_TYPE_HEX
        self.init_ui("GNSS Base Position Config", self.PANEL_PARAMETERS, [])

    def build_config_binary(self):
        """Build the configuration binary message."""

        position = {}
        pos_config = self.CONFIG_INPUT["position"]
        for key in pos_config:
            position[key] = self.content.config_inputs[pos_config[key].name].get_value()

        accuracy = self.content.config_inputs[self.CONFIG_INPUT["accuracy"].name].get_value()
        invalidation_date = self.content.config_inputs[
            self.CONFIG_INPUT["invalidationDate"].name
        ].get_value()

        base_node_id = self.content.config_inputs[self.CONFIG_INPUT["baseNodeId"].name].get_value()

        config_json = {
            "type": self.msg_type,
            "version": 0,
            "position": position,
            "accuracy": accuracy,
            "invalidationDate": invalidation_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "baseNodeId": base_node_id,
        }
        print(config_json)
        return ls_json2msg.json2msg(config_json)


if __name__ == "__main__":
    main(GnssBasePositionCfgTool)
