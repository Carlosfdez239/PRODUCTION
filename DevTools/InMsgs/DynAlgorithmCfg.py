#!/usr/bin/env python3
import math
import os
import sys
import traceback

import ls_json2msg
import serialbsc
import wx
from remote_configs import convert_to_remote_config_python3

global_tty = ""

plus_minus_sign_ascii = "\u00B1"

# General fields
default_msg_version = "1"
default_alert_mode = False
max_version_value = (1 << 4) - 1
max_enable_triggered_event_reporting = (1 << 1) - 1

# MTVV size fields
max_samples_to_discard_mtvv_value = (1 << 22) - 1
max_wake_up_threshold_mtvv_value = (1 << 16) - 1
max_trans_threshold_mtvv_value = 100.00
min_trans_threshold_mtvv_value = 55.00
max_stop_time_num_windows_mtvv_value = (1 << 4) - 1
max_num_windows_event_mtvv_value = (1 << 7) - 1

# PPV size fields
max_wake_up_threshold_ppv_value = (1 << 16) - 1
max_samples_to_discard_ppv_value = (1 << 22) - 1
max_trans_threshold_ppv_value = 60.00
min_trans_threshold_ppv_value = 0.00
max_stop_time_num_windows_ppv_value = (1 << 4) - 1
max_num_windows_event_ppv_value = (1 << 7) - 1
min_num_windows_value = 1
low_pass_filter_max_value = 1000

OUTPUT_PARAMETER_LIST = (
    "No output parameter",  # "No algorithm"
    "MTVV (Wm weight)",  # "ISO 2631-2"
    "PPV",  # "DIN 4150-3"
)

HIGH_PASS_FILTER_DICT = {
    "Disabled": 0,
    "247": 247,
    "62.084": 62.084,
    "15.545": 15.545,
    "3.862": 3.862,
    "0.954": 0.954,
    "0.238": 0.238,
}

MTVV_DYNAMIC_RANGE_LIST = (
    plus_minus_sign_ascii + " 2g",
    plus_minus_sign_ascii + " 4g",
    plus_minus_sign_ascii + " 8g",
)

MTVV_SAMPLES_IN_WINDOW_LIST = ("125", "250", "500", "1000", "2000", "4000")

PPV_SAMPLES_IN_WINDOW_LIST = ("128", "256", "512", "1024", "2048", "4096")

PPV_RAW_SAMPLING_FREQ_DICT = {
    "125 Hz": 125,
    "250 Hz": 250,
    "500 Hz": 500,
    "1000 Hz": 1000,
    "2000 Hz": 2000,
    "4000 Hz": 4000,
}

PPV_BUILGING_TYPE_DICT = {
    "Dwellings and more restrictive": "0-30 mm/s",
    "Commercial": "0-60 mm/s",
    plus_minus_sign_ascii + " 8g": plus_minus_sign_ascii + " 8g",
}

RAW_DATA_SCHEDULING_MODE_LIST = ("Disabled", "Every event", "Storage threshold")

RAW_DATA_OPERATING_MODE_LIST = ("All axes", "X axis", "Y axis", "Z axis")


class MyPanels(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent)
        self.parent = parent


class MyFrame(wx.Frame):

    tty_prefix = "/dev/ttyUSB"
    vertical_pos = 20
    left_vertical_pos = 20
    horizontal_pos = 20
    vertical_pos_increment = 35
    horizontal_pos_increment = 150
    bottom_padding = 40
    right_from_pos = 230
    right_from_pos_raw = 150
    side_width = 740 - right_from_pos

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)
        self.parent = parent
        self.panel = wx.Panel(self, -1)

        self.leftpanel = MyPanels(self.panel, 1)
        self.rightpanel = MyPanels(self.panel, 1)

        self.basicsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.basicsizer.Add(self.leftpanel, 1, wx.EXPAND)
        self.basicsizer.Add(self.rightpanel, 1, wx.EXPAND)
        self.panel.SetSizer(self.basicsizer)

        self.init_ui()

        self.Centre()

    def create_new_panel(self):
        self.rightpanel = MyPanels(self.panel, 1)
        self.basicsizer.Add(self.rightpanel, 1, wx.EXPAND)
        self.display_algorithm_cfg()
        self.rightpanel.parent.Layout()
        self.Show(True)
        self.Centre()

    def display_new_configuration(self, event):
        self.destroy_panel()
        self.create_new_panel()

    def destroy_panel(self):
        self.rightpanel.Destroy()
        self.vertical_pos = 20
        self.horizontal_pos = 20

    def add_raw_data_cfg_to_display(self):
        wx.StaticText(
            self.rightpanel, label="Raw Data Storage Cfgs", pos=(100, self.vertical_pos + 6)
        )
        self.vertical_pos += self.vertical_pos_increment

        wx.StaticText(self.rightpanel, label="Scheduling Mode", pos=(0, self.vertical_pos + 6))
        self.w_scheduling_mode_raw_data_storage = wx.ComboBox(
            self.rightpanel,
            500,
            value=RAW_DATA_SCHEDULING_MODE_LIST[0],
            size=(200, 30),
            pos=(self.right_from_pos_raw, self.vertical_pos),
            choices=RAW_DATA_SCHEDULING_MODE_LIST,
            style=wx.TE_READONLY,
        )
        self.vertical_pos += self.vertical_pos_increment

        wx.StaticText(self.rightpanel, label="Operating Mode", pos=(0, self.vertical_pos + 6))
        self.w_operating_mode_raw_data_storage = wx.ComboBox(
            self.rightpanel,
            500,
            value=RAW_DATA_OPERATING_MODE_LIST[0],
            size=(200, 30),
            pos=(self.right_from_pos_raw, self.vertical_pos),
            choices=RAW_DATA_OPERATING_MODE_LIST,
            style=wx.TE_READONLY,
        )
        self.vertical_pos += self.vertical_pos_increment + self.bottom_padding

    def display_algorithm_cfg(self):

        output_parameter = self.w_output_parameter.GetValue()
        horizontal_size = 370

        if output_parameter in "No output parameter":
            pass
        elif output_parameter in "MTVV (Wm weight)":

            wx.StaticText(
                self.rightpanel,
                label="High Pass Filter Coef (*10^⁻5)",
                pos=(0, self.vertical_pos + 6),
            )
            self.w_high_pass_filter_mtvv = wx.ComboBox(
                self.rightpanel,
                500,
                value=list(HIGH_PASS_FILTER_DICT.keys())[0],
                size=(120, 30),
                pos=(self.right_from_pos, self.vertical_pos),
                choices=list(HIGH_PASS_FILTER_DICT.keys()),
                style=wx.TE_READONLY,
            )
            self.w_high_pass_filter_mtvv.Bind(wx.EVT_TEXT, self.hpf_coef_to_hpf_freq)
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel,
                label="High Pass Filter Frequency (Hz)",
                pos=(0, self.vertical_pos + 6),
            )
            self.w_high_pass_filter_freq_mtvv = wx.TextCtrl(
                self.rightpanel,
                500,
                size=(120, 30),
                pos=(self.right_from_pos, self.vertical_pos),
                style=wx.TE_READONLY,
            )
            self.w_high_pass_filter_freq_mtvv.SetForegroundColour("Grey")
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel, label="Samples To Discard", pos=(0, self.vertical_pos + 6)
            )
            self.w_samples_to_discard_mtvv = wx.TextCtrl(
                self.rightpanel, -1, size=(120, 30), pos=(self.right_from_pos, self.vertical_pos)
            )
            self.w_samples_to_discard_mtvv.SetMaxLength(7)
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(self.rightpanel, label="Dynamic Range", pos=(0, self.vertical_pos + 6))
            self.w_dynamic_range_mtvv = wx.ComboBox(
                self.rightpanel,
                500,
                value=MTVV_DYNAMIC_RANGE_LIST[0],
                size=(120, 30),
                pos=(self.right_from_pos, self.vertical_pos),
                choices=MTVV_DYNAMIC_RANGE_LIST,
                style=wx.TE_READONLY,
            )
            self.w_dynamic_range_mtvv.Bind(wx.EVT_TEXT, self.wake_up_threshold_to_raw_threshold)
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel, label="Wake Up Threshold (Law dB)", pos=(0, self.vertical_pos + 6)
            )
            self.w_wake_up_threshold_law_mtvv = wx.TextCtrl(
                self.rightpanel, -1, size=(120, 30), pos=(self.right_from_pos, self.vertical_pos)
            )
            self.w_wake_up_threshold_law_mtvv.SetMaxLength(5)
            self.w_wake_up_threshold_law_mtvv.Bind(
                wx.EVT_TEXT, self.wake_up_threshold_to_raw_threshold
            )
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel, label="Wake Up Threshold (ug)", pos=(0, self.vertical_pos + 6)
            )
            self.w_wake_up_threshold_ug_mtvv = wx.TextCtrl(
                self.rightpanel,
                -1,
                size=(120, 30),
                pos=(self.right_from_pos, self.vertical_pos),
                style=wx.TE_READONLY,
            )
            self.w_wake_up_threshold_ug_mtvv.SetForegroundColour("Grey")
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel, label="Wake Up Threshold (raw)", pos=(0, self.vertical_pos + 6)
            )
            self.w_wake_up_threshold_raw_mtvv = wx.TextCtrl(
                self.rightpanel,
                -1,
                size=(120, 30),
                pos=(self.right_from_pos, self.vertical_pos),
                style=wx.TE_READONLY,
            )
            self.w_wake_up_threshold_raw_mtvv.SetForegroundColour("Grey")
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel,
                label="Transmission Threshold (Law dB)",
                pos=(0, self.vertical_pos + 6),
            )
            self.w_trans_threshold_mtvv = wx.TextCtrl(
                self.rightpanel, -1, size=(120, 30), pos=(self.right_from_pos, self.vertical_pos)
            )
            self.w_trans_threshold_mtvv.SetMaxLength(6)
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel, label="Samples In Window", pos=(0, self.vertical_pos + 6)
            )
            self.w_samples_in_window_mtvv = wx.ComboBox(
                self.rightpanel,
                500,
                value=MTVV_SAMPLES_IN_WINDOW_LIST[0],
                size=(120, 30),
                pos=(self.right_from_pos, self.vertical_pos),
                choices=MTVV_SAMPLES_IN_WINDOW_LIST,
                style=wx.TE_READONLY,
            )
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel, label="Stop Time (num windows)", pos=(0, self.vertical_pos + 6)
            )
            self.w_stop_time_mtvv = wx.TextCtrl(
                self.rightpanel, -1, size=(120, 30), pos=(self.right_from_pos, self.vertical_pos)
            )
            self.w_stop_time_mtvv.SetMaxLength(2)
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel, label="Max Windows Event", pos=(0, self.vertical_pos + 6)
            )
            self.w_num_max_windows_event_mtvv = wx.TextCtrl(
                self.rightpanel, -1, size=(120, 30), pos=(self.right_from_pos, self.vertical_pos)
            )
            self.w_num_max_windows_event_mtvv.SetMaxLength(3)
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel, label="Max Windows Single Event", pos=(0, self.vertical_pos + 6)
            )
            self.w_num_max_windows_single_event_mtvv = wx.TextCtrl(
                self.rightpanel, -1, size=(120, 30), pos=(self.right_from_pos, self.vertical_pos)
            )
            self.w_num_max_windows_single_event_mtvv.SetMaxLength(3)
            self.vertical_pos += self.vertical_pos_increment * 2

            wx.StaticText(
                self.rightpanel, label="Alert/Raw Storage Threshold", pos=(0, self.vertical_pos + 6)
            )
            self.w_alert_and_raw_storage_thd_mtvv = wx.TextCtrl(
                self.rightpanel, -1, size=(120, 30), pos=(self.right_from_pos, self.vertical_pos)
            )
            self.w_alert_and_raw_storage_thd_mtvv.SetMaxLength(6)
            self.vertical_pos += self.vertical_pos_increment * 2

            self.add_raw_data_cfg_to_display()

            horizontal_size = self.right_from_pos + self.side_width

        elif output_parameter in "PPV":

            wx.StaticText(
                self.rightpanel, label="Raw Sampling Frequency", pos=(0, self.vertical_pos + 6)
            )
            self.w_raw_sampling_freq_ppv = wx.ComboBox(
                self.rightpanel,
                500,
                value=list(PPV_RAW_SAMPLING_FREQ_DICT)[0],
                size=(120, 30),
                pos=(self.right_from_pos, self.vertical_pos),
                choices=list(PPV_RAW_SAMPLING_FREQ_DICT),
                style=wx.TE_READONLY,
            )
            self.w_raw_sampling_freq_ppv.Bind(wx.EVT_TEXT, self.hpf_coef_to_hpf_freq)
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel,
                label="High Pass Filter Coef (*10^⁻5)",
                pos=(0, self.vertical_pos + 6),
            )
            self.w_high_pass_filter_ppv = wx.ComboBox(
                self.rightpanel,
                500,
                value=list(HIGH_PASS_FILTER_DICT.keys())[0],
                size=(120, 30),
                pos=(self.right_from_pos, self.vertical_pos),
                choices=list(HIGH_PASS_FILTER_DICT.keys()),
                style=wx.TE_READONLY,
            )
            self.w_high_pass_filter_ppv.Bind(wx.EVT_TEXT, self.hpf_coef_to_hpf_freq)
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel,
                label="High Pass Filter Frequency (Hz)",
                pos=(0, self.vertical_pos + 6),
            )
            self.w_high_pass_filter_freq_ppv = wx.TextCtrl(
                self.rightpanel,
                500,
                size=(120, 30),
                pos=(self.right_from_pos, self.vertical_pos),
                style=wx.TE_READONLY,
            )
            self.w_high_pass_filter_freq_ppv.SetForegroundColour("Grey")
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel, label="Samples To Discard", pos=(0, self.vertical_pos + 6)
            )
            self.w_samples_to_discard_ppv = wx.TextCtrl(
                self.rightpanel, -1, size=(120, 30), pos=(self.right_from_pos, self.vertical_pos)
            )
            self.w_samples_to_discard_ppv.SetMaxLength(7)
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(self.rightpanel, label="Building Type", pos=(0, self.vertical_pos + 6))
            self.w_building_type_ppv = wx.ComboBox(
                self.rightpanel,
                500,
                value=list(PPV_BUILGING_TYPE_DICT.keys())[0],
                size=(120, 30),
                pos=(self.right_from_pos, self.vertical_pos),
                choices=list(PPV_BUILGING_TYPE_DICT.keys()),
                style=wx.TE_READONLY,
            )
            self.w_building_type_ppv.Bind(wx.EVT_TEXT, self.set_dynamic_range_ppv)
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(self.rightpanel, label="Dynamic Range", pos=(0, self.vertical_pos + 6))
            self.w_dynamic_range_ppv = wx.TextCtrl(
                self.rightpanel,
                500,
                size=(120, 30),
                pos=(self.right_from_pos, self.vertical_pos),
                style=wx.TE_READONLY | wx.TE_RICH,
            )
            self.w_dynamic_range_ppv.SetForegroundColour("Grey")
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel, label="Wake Up Threshold (mm/s)", pos=(0, self.vertical_pos + 6)
            )
            self.w_wake_up_threshold_mm_s_ppv = wx.TextCtrl(
                self.rightpanel, -1, size=(120, 30), pos=(self.right_from_pos, self.vertical_pos)
            )
            self.w_wake_up_threshold_mm_s_ppv.SetMaxLength(5)
            self.w_wake_up_threshold_mm_s_ppv.Bind(
                wx.EVT_TEXT, self.wake_up_threshold_to_raw_threshold
            )
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel, label="Wake Up Threshold (ug)", pos=(0, self.vertical_pos + 6)
            )
            self.w_wake_up_threshold_ug_ppv = wx.TextCtrl(
                self.rightpanel,
                -1,
                size=(120, 30),
                pos=(self.right_from_pos, self.vertical_pos),
                style=wx.TE_READONLY,
            )
            self.w_wake_up_threshold_ug_ppv.SetForegroundColour("Grey")
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel, label="Wake Up Threshold (raw)", pos=(0, self.vertical_pos + 6)
            )
            self.w_wake_up_threshold_raw_ppv = wx.TextCtrl(
                self.rightpanel,
                -1,
                size=(120, 30),
                pos=(self.right_from_pos, self.vertical_pos),
                style=wx.TE_READONLY,
            )
            self.w_wake_up_threshold_raw_ppv.SetForegroundColour("Grey")
            self.w_wake_up_threshold_raw_ppv.SetMaxLength(5)
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel,
                label="Transmission Threshold (mm/s)",
                pos=(0, self.vertical_pos + 6),
            )
            self.w_trans_threshold_ppv = wx.TextCtrl(
                self.rightpanel, -1, size=(120, 30), pos=(self.right_from_pos, self.vertical_pos)
            )
            self.w_trans_threshold_ppv.SetMaxLength(6)
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel, label="Samples In Window", pos=(0, self.vertical_pos + 6)
            )
            self.w_samples_in_window_ppv = wx.ComboBox(
                self.rightpanel,
                500,
                value=PPV_SAMPLES_IN_WINDOW_LIST[0],
                size=(120, 30),
                pos=(self.right_from_pos, self.vertical_pos),
                choices=PPV_SAMPLES_IN_WINDOW_LIST,
                style=wx.TE_READONLY,
            )
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel, label="Stop Time (num windows)", pos=(0, self.vertical_pos + 6)
            )
            self.w_stop_time_ppv = wx.TextCtrl(
                self.rightpanel, -1, size=(120, 30), pos=(self.right_from_pos, self.vertical_pos)
            )
            self.w_stop_time_ppv.SetMaxLength(2)
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel, label="Max Windows Event", pos=(0, self.vertical_pos + 6)
            )
            self.w_num_max_windows_event_ppv = wx.TextCtrl(
                self.rightpanel, -1, size=(120, 30), pos=(self.right_from_pos, self.vertical_pos)
            )
            self.w_num_max_windows_event_ppv.SetMaxLength(3)
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel, label="Max Windows Single Event", pos=(0, self.vertical_pos + 6)
            )
            self.w_num_max_windows_single_event_ppv = wx.TextCtrl(
                self.rightpanel, -1, size=(120, 30), pos=(self.right_from_pos, self.vertical_pos)
            )
            self.w_num_max_windows_single_event_ppv.SetMaxLength(3)
            self.vertical_pos += self.vertical_pos_increment

            wx.StaticText(
                self.rightpanel, label="Low Pass Filter (Hz)", pos=(0, self.vertical_pos + 6)
            )
            self.w_low_pass_filter_ppv = wx.TextCtrl(
                self.rightpanel, -1, size=(120, 30), pos=(self.right_from_pos, self.vertical_pos)
            )
            self.w_low_pass_filter_ppv.SetMaxLength(4)
            self.vertical_pos += self.vertical_pos_increment * 2

            wx.StaticText(
                self.rightpanel, label="Alert/Raw Storage Threshold", pos=(0, self.vertical_pos + 6)
            )
            self.w_alert_and_raw_storage_thd_ppv = wx.TextCtrl(
                self.rightpanel, -1, size=(120, 30), pos=(self.right_from_pos, self.vertical_pos)
            )
            self.w_alert_and_raw_storage_thd_ppv.SetMaxLength(6)
            self.vertical_pos += self.vertical_pos_increment * 2

            self.add_raw_data_cfg_to_display()

            horizontal_size = 740

        else:
            return

        self.load_config(0)
        self.SetSize((horizontal_size, max(self.vertical_pos, self.left_vertical_pos) + 10))

    def get_mtvv_threshold(self, value, name):
        try:
            mtvv_threshold = float(value)
        except:
            raise Exception(name + " is not an integer")

        if (
            mtvv_threshold > max_trans_threshold_mtvv_value
            or mtvv_threshold < min_trans_threshold_mtvv_value
        ):
            raise Exception(name + " is out of range")

        if (mtvv_threshold * 100) % 5 != 0:
            raise Exception(name + " is not an acceptable value")

        return mtvv_threshold

    def get_ppv_threshold(self, value, name):
        try:
            ppv_threshold = float(value)
        except:
            raise Exception(name + " is not an integer")

        if (
            ppv_threshold > max_trans_threshold_ppv_value
            or ppv_threshold < min_trans_threshold_ppv_value
        ):
            raise Exception(name + " is out of range")

        return ppv_threshold

    def build_raw_data_config_binary(self, config_json):
        config_json["outputParameterCfg"][
            "rawDataStorageSchedulingMode"
        ] = self.w_scheduling_mode_raw_data_storage.GetValue()
        config_json["outputParameterCfg"][
            "rawDataStorageOperatingMode"
        ] = self.w_operating_mode_raw_data_storage.GetValue()

        # method to set the config

    def build_config_binary(self, event):

        config_json = {}

        config_json["type"] = "setVibrationRegulationCfgV1"
        config_json["outputParameterCfg"] = {}

        try:

            output_parameter_str = self.w_output_parameter.GetValue()
            config_json["outputParameter"] = output_parameter_str

            try:
                config_json["cfgVersion"] = int(self.w_message_version.GetValue())
            except:
                raise Exception("Message Version invalid")

            config_json["alertMode"] = int(self.w_alert_mode.GetValue())

            if "No output parameter" in output_parameter_str:
                if int(self.w_alert_mode.GetValue()):
                    raise Exception("Alert mode must be disabled")
                pass

            elif "MTVV (Wm weight)" in output_parameter_str:

                config_json["outputParameterCfg"]["highPassFilter"] = HIGH_PASS_FILTER_DICT[
                    self.w_high_pass_filter_mtvv.GetValue()
                ]

                try:
                    samples_to_discard = int(self.w_samples_to_discard_mtvv.GetValue())
                except:
                    raise Exception("Samples to discard is not an integer")

                if samples_to_discard > max_samples_to_discard_mtvv_value:
                    raise Exception("Samples to discard value is outside the range")

                config_json["outputParameterCfg"]["samplesToDiscard"] = samples_to_discard

                config_json["outputParameterCfg"][
                    "dynamicRange"
                ] = self.w_dynamic_range_mtvv.GetValue()

                try:
                    wake_up_threshold = int(self.w_wake_up_threshold_law_mtvv.GetValue())
                except:
                    raise Exception("Wake Up Threshold is not an integer")

                if wake_up_threshold > max_wake_up_threshold_mtvv_value:
                    raise Exception("Wake Up Threshold is outside the range")

                config_json["outputParameterCfg"]["wakeUpThreshold"] = wake_up_threshold

                transmission_threshold = self.get_mtvv_threshold(
                    self.w_trans_threshold_mtvv.GetValue(), "Transmission threshold"
                )
                config_json["outputParameterCfg"]["transmissionThreshold"] = transmission_threshold

                config_json["outputParameterCfg"]["samplesInWindow"] = int(
                    self.w_samples_in_window_mtvv.GetValue()
                )

                try:
                    stop_time_windows = int(self.w_stop_time_mtvv.GetValue())
                except:
                    raise Exception("Stop Time is not an integer")

                if (
                    stop_time_windows > max_stop_time_num_windows_mtvv_value
                    or min_num_windows_value > stop_time_windows
                ):
                    raise Exception("Stop Time is outside the range")

                config_json["outputParameterCfg"]["stoppageTime"] = stop_time_windows

                try:
                    max_windows_event = int(self.w_num_max_windows_event_mtvv.GetValue())
                except:
                    raise Exception("Max Windows Event is not an integer")

                if (
                    max_windows_event > max_num_windows_event_mtvv_value
                    or min_num_windows_value > max_windows_event
                ):
                    raise Exception("Max Windows Event is outside the range")

                if max_windows_event < stop_time_windows:
                    raise Exception("Max Windows Event cannot be lower than Stop Time Windows")

                config_json["outputParameterCfg"]["maxWindowsPerEvent"] = max_windows_event

                try:
                    max_windows_single_event = int(
                        self.w_num_max_windows_single_event_mtvv.GetValue()
                    )
                except:
                    raise Exception("Max Windows Single Event is not an integer")

                if (
                    max_windows_single_event > max_num_windows_event_mtvv_value
                    or min_num_windows_value > max_windows_single_event
                ):
                    raise Exception("Max Windows Single Event is outside the range")

                config_json["outputParameterCfg"]["shortEventNumWindows"] = max_windows_single_event

                alert_and_raw_storage_thd = self.get_mtvv_threshold(
                    self.w_alert_and_raw_storage_thd_mtvv.GetValue(), "Alert Threshold"
                )
                config_json["outputParameterCfg"][
                    "alertAndRawStorageThreshold"
                ] = alert_and_raw_storage_thd

                self.build_raw_data_config_binary(config_json)

            elif "PPV" in output_parameter_str:

                config_json["outputParameterCfg"]["samplingFrequency"] = PPV_RAW_SAMPLING_FREQ_DICT[
                    self.w_raw_sampling_freq_ppv.GetValue()
                ]

                config_json["outputParameterCfg"]["highPassFilter"] = HIGH_PASS_FILTER_DICT[
                    self.w_high_pass_filter_ppv.GetValue()
                ]

                try:
                    samples_to_discard = int(self.w_samples_to_discard_ppv.GetValue())
                except:
                    raise Exception("Samples to discard is not an integer")

                if samples_to_discard > max_samples_to_discard_ppv_value:
                    raise Exception("Samples to discard value is outside the range")

                config_json["outputParameterCfg"]["samplesToDiscard"] = samples_to_discard

                config_json["outputParameterCfg"][
                    "dynamicRange"
                ] = self.w_dynamic_range_ppv.GetValue()

                try:
                    wake_up_threshold = float(self.w_wake_up_threshold_mm_s_ppv.GetValue())
                except:
                    raise Exception("Wake Up Threshold is not an integer")

                if wake_up_threshold > max_wake_up_threshold_ppv_value:
                    raise Exception("Wake Up Threshold value is outside the range")

                config_json["outputParameterCfg"]["wakeUpThreshold"] = wake_up_threshold

                transmission_threshold = self.get_ppv_threshold(
                    self.w_trans_threshold_ppv.GetValue(), "Transmission threshold"
                )
                config_json["outputParameterCfg"]["transmissionThreshold"] = transmission_threshold

                config_json["outputParameterCfg"]["samplesInWindow"] = int(
                    self.w_samples_in_window_ppv.GetValue()
                )

                try:
                    stop_time_windows = int(self.w_stop_time_ppv.GetValue())
                except:
                    raise Exception("Stop Time is not an integer")

                if (
                    stop_time_windows > max_stop_time_num_windows_ppv_value
                    or min_num_windows_value > stop_time_windows
                ):
                    raise Exception("Stop Time is outside the range")

                config_json["outputParameterCfg"]["stoppageTime"] = stop_time_windows

                try:
                    max_windows_event = int(self.w_num_max_windows_event_ppv.GetValue())
                except:
                    raise Exception("Max Windows Event is not an integer")

                if (
                    max_windows_event > max_num_windows_event_ppv_value
                    or min_num_windows_value > max_windows_event
                ):
                    raise Exception("Max Windows Event is outside the range")

                config_json["outputParameterCfg"]["maxWindowsPerEvent"] = max_windows_event

                if max_windows_event < stop_time_windows:
                    raise Exception("Max Windows Event cannot be lower than Stop Time Windows")

                try:
                    max_windows_single_event = int(
                        self.w_num_max_windows_single_event_ppv.GetValue()
                    )
                except:
                    raise Exception("Max Windows Single Event is not an integer")

                if (
                    max_windows_single_event > max_num_windows_event_ppv_value
                    or min_num_windows_value > max_windows_single_event
                ):
                    raise Exception("Max Windows Single Event is outside the range")

                config_json["outputParameterCfg"]["shortEventNumWindows"] = max_windows_single_event

                try:
                    low_pass_filter = int(self.w_low_pass_filter_ppv.GetValue())
                except:
                    raise Exception("Low Pass Filter is not an integer")

                if low_pass_filter > low_pass_filter_max_value:
                    raise Exception("Low Pass Filter is outside the range")

                config_json["outputParameterCfg"]["lowPassFilterCutOff"] = low_pass_filter

                alert_and_raw_storage_thd = self.get_ppv_threshold(
                    self.w_alert_and_raw_storage_thd_ppv.GetValue(), "Alert Threshold"
                )
                config_json["outputParameterCfg"][
                    "alertAndRawStorageThreshold"
                ] = alert_and_raw_storage_thd

                self.build_raw_data_config_binary(config_json)

            else:
                raise Exception("Unknown output parameter!")

            print(config_json)
            mote_msg = ls_json2msg.json2msg(config_json)
            print(mote_msg)
            return mote_msg

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, traceback.format_exc())
            msgb = wx.MessageDialog(self, str(e), "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()

    def set_config(self, event):
        tty = self.tty_prefix + self.w_tty_usb.GetValue()
        mote_msg = self.build_config_binary(event)
        if mote_msg:
            self.send_msg_to_node(tty, mote_msg)

    def set_remote_config(self, event):
        tty = self.tty_prefix + self.w_tty_usb.GetValue()
        mote_msg = self.build_config_binary(event)
        if mote_msg:
            remote_mote_msg = convert_to_remote_config_python3(mote_msg, self.w_token.GetValue())
            self.send_msg_to_node(tty, remote_mote_msg)

    def load_raw_data_config(self):
        self.w_scheduling_mode_raw_data_storage.SetValue(RAW_DATA_SCHEDULING_MODE_LIST[0])
        self.w_operating_mode_raw_data_storage.SetValue(RAW_DATA_OPERATING_MODE_LIST[0])

    def load_config(self, event):
        try:

            output_parameter_str = self.w_output_parameter.GetValue()
            self.w_message_version.SetValue(default_msg_version)
            self.w_alert_mode.SetValue(default_alert_mode)

            if "No output parameter" in output_parameter_str:
                pass

            elif "MTVV (Wm weight)" in output_parameter_str:
                self.w_high_pass_filter_mtvv.SetValue("62.084")
                self.hpf_coef_to_hpf_freq(None)
                self.w_samples_to_discard_mtvv.SetValue("2539")
                self.w_dynamic_range_mtvv.SetValue(MTVV_DYNAMIC_RANGE_LIST[0])
                self.w_wake_up_threshold_law_mtvv.SetValue("96")
                self.w_trans_threshold_mtvv.SetValue("60.00")
                self.w_samples_in_window_mtvv.SetValue("1000")
                self.w_stop_time_mtvv.SetValue("5")
                self.w_num_max_windows_event_mtvv.SetValue("60")
                self.w_num_max_windows_single_event_mtvv.SetValue("5")
                self.w_alert_and_raw_storage_thd_mtvv.SetValue("60.00")
                self.load_raw_data_config()

            elif "PPV" in output_parameter_str:
                self.w_raw_sampling_freq_ppv.SetValue("1000 Hz")
                self.w_high_pass_filter_ppv.SetValue("62.084")
                self.hpf_coef_to_hpf_freq(None)
                self.w_samples_to_discard_ppv.SetValue("2539")
                self.w_building_type_ppv.SetValue(list(PPV_BUILGING_TYPE_DICT.keys())[0])
                self.w_dynamic_range_ppv.SetValue(
                    PPV_BUILGING_TYPE_DICT[list(PPV_BUILGING_TYPE_DICT.keys())[0]]
                )
                self.w_wake_up_threshold_mm_s_ppv.SetValue("10")
                self.w_trans_threshold_ppv.SetValue("20")
                self.w_samples_in_window_ppv.SetValue("2048")
                self.w_stop_time_ppv.SetValue("5")
                self.w_num_max_windows_event_ppv.SetValue("30")
                self.w_num_max_windows_single_event_ppv.SetValue("5")
                self.w_low_pass_filter_ppv.SetValue("1000")
                self.w_alert_and_raw_storage_thd_ppv.SetValue("20")
                self.load_raw_data_config()

            else:
                raise Exception("Unknown output_parameter!")

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, traceback.format_exc())
            msgb = wx.MessageDialog(self, str(e), "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()

    # method to request the config
    def request_config(self, event):
        try:

            tty_usb = "/dev/ttyUSB" + self.w_tty_usb.GetValue()

            msg_json = {"type": "iget_dynCfg"}
            mote_msg = ls_json2msg.json2msg(msg_json)

            self.send_msg_to_node(tty_usb, mote_msg)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, traceback.format_exc())
            msgb = wx.MessageDialog(self, str(e), "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()

    def send_msg_to_node(self, tty, msg):
        ser = serialbsc.open_serial(tty)
        serialbsc.send_message_to_mote(ser, msg)
        serialbsc.close_serial(ser)

    def hpf_coef_to_hpf_freq(self, event):
        try:
            output_parameter_str = self.w_output_parameter.GetValue()

            if "No output parameter" in output_parameter_str:
                pass

            elif "MTVV (Wm weight)" in output_parameter_str:
                coef = HIGH_PASS_FILTER_DICT[self.w_high_pass_filter_mtvv.GetValue()]
                sampling_freq = 1000
                hpf_freq = coef * sampling_freq / 100000.0
                self.w_high_pass_filter_freq_mtvv.SetValue("{0:.4f}".format(hpf_freq))

            elif "PPV" in output_parameter_str:
                coef = HIGH_PASS_FILTER_DICT[self.w_high_pass_filter_ppv.GetValue()]
                sampling_freq = PPV_RAW_SAMPLING_FREQ_DICT[self.w_raw_sampling_freq_ppv.GetValue()]
                hpf_freq = coef * sampling_freq / 100000.0
                self.w_high_pass_filter_freq_ppv.SetValue("{0:.4f}".format(hpf_freq))

        except Exception as e:
            msgb = wx.MessageDialog(self, str(e), "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()

    def wake_up_threshold_to_raw_threshold(self, event):
        try:
            output_parameter_str = self.w_output_parameter.GetValue()

            if "No output parameter" in output_parameter_str:
                pass

            elif "MTVV (Wm weight)" in output_parameter_str:
                law_db_threshold = self.w_wake_up_threshold_law_mtvv.GetValue()

                if law_db_threshold != "":
                    law_db = float(law_db_threshold)
                    acc_mtvv_threshold = pow(10, (law_db / 20)) * pow(10, -6)

                    ug_mtvv_threshold = acc_mtvv_threshold * 1000000 / 9.80665
                    self.w_wake_up_threshold_ug_mtvv.SetValue("{0:.4f}".format(ug_mtvv_threshold))

                    dynamic_range = int(self.w_dynamic_range_mtvv.GetValue()[2])
                    scale = 256000 * 2 / dynamic_range
                    raw_mtvv_threshold = round(
                        ug_mtvv_threshold * pow(10, -6) * scale / (pow(2, 3))
                    )
                    self.w_wake_up_threshold_raw_mtvv.SetValue(
                        str(min(max_wake_up_threshold_mtvv_value, raw_mtvv_threshold))
                    )

            elif "PPV" in output_parameter_str:
                mm_s_threshold = self.w_wake_up_threshold_mm_s_ppv.GetValue()

                if mm_s_threshold != "":
                    wake_up_theshold = float(mm_s_threshold)
                    acc_ppv_threshold = 2 * math.pi * wake_up_theshold

                    ug_ppv_threshold = (acc_ppv_threshold * 1000) / 9.80665
                    self.w_wake_up_threshold_ug_ppv.SetValue("{0:.4f}".format(ug_ppv_threshold))

                    dynamic_range = int(self.w_dynamic_range_ppv.GetValue()[2])
                    scale = 256000 * 2 / dynamic_range
                    ppv_mtvv_threshold = round(ug_ppv_threshold * pow(10, -6) * scale / (pow(2, 3)))

                    self.w_wake_up_threshold_raw_ppv.SetValue(
                        str(min(max_wake_up_threshold_ppv_value, ppv_mtvv_threshold))
                    )

            else:
                raise Exception("Unknown output_parameter!")

        except Exception as e:
            msgb = wx.MessageDialog(self, str(e), "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()

    def set_dynamic_range_ppv(self, event):
        try:
            dynamic_range_value = PPV_BUILGING_TYPE_DICT[self.w_building_type_ppv.GetValue()]
            self.w_dynamic_range_ppv.SetValue(dynamic_range_value)

        except Exception as e:
            msgb = wx.MessageDialog(self, str(e), "ERROR", wx.OK | wx.ICON_HAND)
            msgb.ShowModal()

        self.wake_up_threshold_to_raw_threshold(0)

    def init_ui(self):
        global global_tty

        wx.StaticText(self.leftpanel, label="ttyUSB Number", pos=(115, self.left_vertical_pos + 6))
        self.w_tty_usb = wx.TextCtrl(
            self.leftpanel, -1, size=(90, 30), pos=(20, self.left_vertical_pos)
        )
        self.w_tty_usb.SetMaxLength(10)
        self.w_tty_usb.WriteText(
            global_tty[global_tty.index(self.tty_prefix) + len(self.tty_prefix) :]
        )
        self.left_vertical_pos = self.left_vertical_pos + self.vertical_pos_increment

        wx.StaticText(self.leftpanel, label="Config version", pos=(20, self.left_vertical_pos + 6))
        self.w_message_version = wx.TextCtrl(
            self.leftpanel, -1, size=(90, 30), pos=(240, self.left_vertical_pos)
        )
        self.w_message_version.SetMaxLength(1)
        self.w_message_version.WriteText(default_msg_version)
        self.left_vertical_pos += self.vertical_pos_increment

        wx.StaticText(self.leftpanel, label="Output param", pos=(20, self.left_vertical_pos + 6))
        self.w_output_parameter = wx.ComboBox(
            self.leftpanel,
            500,
            value=OUTPUT_PARAMETER_LIST[0],
            size=(200, 30),
            pos=(130, self.left_vertical_pos),
            choices=OUTPUT_PARAMETER_LIST,
            style=wx.TE_READONLY,
        )
        self.w_output_parameter.Bind(wx.EVT_TEXT, self.display_new_configuration)
        self.left_vertical_pos += self.vertical_pos_increment

        wx.StaticText(
            self.leftpanel, label="Enable Alert Mode", pos=(20, self.left_vertical_pos + 6)
        )
        self.w_alert_mode = wx.CheckBox(
            self.leftpanel, label="", pos=(315, self.left_vertical_pos + 6)
        )
        self.w_alert_mode.SetValue(default_alert_mode)
        self.left_vertical_pos += self.vertical_pos_increment + 10

        self.w_set_config_btn = wx.Button(
            self.leftpanel, label="Set Config", pos=(20, self.left_vertical_pos)
        )
        self.w_set_config_btn.Bind(wx.EVT_BUTTON, self.set_config)

        self.w_set_config_btn = wx.Button(
            self.leftpanel, label="Request Config", pos=(195, self.left_vertical_pos)
        )
        self.w_set_config_btn.Bind(wx.EVT_BUTTON, self.request_config)
        self.left_vertical_pos += self.vertical_pos_increment

        self.w_default_cfg_btn = wx.Button(
            self.leftpanel, label="Load default config", pos=(20, self.left_vertical_pos + 20)
        )
        self.w_default_cfg_btn.Bind(wx.EVT_BUTTON, self.load_config)
        self.left_vertical_pos += self.vertical_pos_increment + 50

        wx.StaticText(self.leftpanel, label="Remote Token", pos=(20, self.left_vertical_pos + 6))
        self.w_token = wx.TextCtrl(
            self.leftpanel, -1, size=(90, 30), pos=(240, self.left_vertical_pos)
        )
        self.w_token.SetMaxLength(3)
        self.w_token.WriteText("1")
        self.left_vertical_pos += self.vertical_pos_increment + 10

        self.w_set_remote_config_btn = wx.Button(
            self.leftpanel, label="Set Remote Config", pos=(20, self.left_vertical_pos)
        )
        self.w_set_remote_config_btn.Bind(wx.EVT_BUTTON, self.set_remote_config)
        self.left_vertical_pos += self.vertical_pos_increment + 25

        self.left_vertical_pos += self.vertical_pos_increment
        self.SetSize((370, self.left_vertical_pos))


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

    try:
        app = wx.App()
        frame = MyFrame(None, -1, "DynAlgorithmCfg.py")
        frame.Show()
        app.MainLoop()
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, traceback.format_exc())


if __name__ == "__main__":
    main()
