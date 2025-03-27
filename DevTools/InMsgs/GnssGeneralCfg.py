#!/usr/bin/env python3
import sys

sys.path.append("../lib/")
import ls_json2msg
from ls_base import LSBaseTool, main  # Import the base class and main function
from wx_utils import ConfigType, LSConfigParam


class GnssGeneralCfgTool(LSBaseTool):
    MSG_TYPE = "setGnssGeneralCfg"
    AM_TYPE_HEX = "9F"

    CONSTELLATIONS = [
        "gpsQzss",
        "glonass",
        "galileo",
        "beidou",
    ]  # ZED-F9P-04B model does not support NavIC option.

    CONFIG_INPUT = {
        "sampleOffset": LSConfigParam("Sample offset (s)", 15, ConfigType.FIELD),
        "sampleNowSamples": LSConfigParam("SampleNow N Samples", 10, ConfigType.FIELD),
        "sampleNowFirstFixTimeout": LSConfigParam(
            "SampleNow FirstFixTimeOut", 48, ConfigType.FIELD
        ),
        "sampleNowTimeout": LSConfigParam("SampleNow timeout", 60, ConfigType.FIELD),
        "mode": LSConfigParam("Mode", "ROVER", ConfigType.DROPDOWN, ["ROVER", "BASE"]),
        "startBehavior": LSConfigParam(
            "StartBehavior", "WARM", ConfigType.DROPDOWN, ["COLD", "WARM"]
        ),
        "samplingEnabled": LSConfigParam("Enable Sampling", True, ConfigType.BOOL),
        "constellationsEnabled": LSConfigParam(
            "Constellations", 0b00111, ConfigType.BITWISE, CONSTELLATIONS
        ),
        "correctionsChScheduling": LSConfigParam("Channel Scheduling", 0, ConfigType.FIELD),
        "warmup": LSConfigParam("Warmup Time (s)", 15, ConfigType.FIELD),
        "sampleDuration": LSConfigParam("Sample Duration (s)", 30, ConfigType.FIELD),
        "installationModeEnabled": LSConfigParam("Enable Installation Mode", True, ConfigType.BOOL),
        "installationModePeriod": LSConfigParam("Installation Mode Period", 20, ConfigType.FIELD),
        "installationModeOffset": LSConfigParam("Installation Mode Offset", 0, ConfigType.FIELD),
        "installationModeLength": LSConfigParam("Installation Mode Length", 1, ConfigType.FIELD),
    }

    LEFT_PANEL_PARAMETERS = [
        CONFIG_INPUT["sampleOffset"],
        CONFIG_INPUT["warmup"],
        CONFIG_INPUT["sampleDuration"],
        CONFIG_INPUT["mode"],
        CONFIG_INPUT["startBehavior"],
        CONFIG_INPUT["correctionsChScheduling"],
        CONFIG_INPUT["samplingEnabled"],
        CONFIG_INPUT["constellationsEnabled"],
    ]

    RIGHT_PANEL_PARAMETERS = [
        CONFIG_INPUT["sampleNowSamples"],
        CONFIG_INPUT["sampleNowFirstFixTimeout"],
        CONFIG_INPUT["sampleNowTimeout"],
        CONFIG_INPUT["installationModeEnabled"],
        CONFIG_INPUT["installationModePeriod"],
        CONFIG_INPUT["installationModeOffset"],
        CONFIG_INPUT["installationModeLength"],
    ]

    def __init__(self, *args, **kwargs):
        super(GnssGeneralCfgTool, self).__init__(*args, **kwargs)
        self.msg_type = self.MSG_TYPE
        self.am_type_hex = self.AM_TYPE_HEX
        self.init_ui("GNSS General Config", self.LEFT_PANEL_PARAMETERS, self.RIGHT_PANEL_PARAMETERS)

    def build_config_binary(self):
        """Build the configuration binary message."""
        cfg = {
            key: self.content.config_inputs[param.name].get_value()
            for key, param in self.CONFIG_INPUT.items()
        }

        # Ensure NavIC is always treated as 0
        cfg["constellationsEnabled"]["navic"] = False  # Set NavIC to False, because
        # ZED-F9P-04B model does not support this option.

        config_json = {"type": self.msg_type, "version": 0, "cfg": cfg}

        return ls_json2msg.json2msg(config_json)


if __name__ == "__main__":
    main(GnssGeneralCfgTool)
