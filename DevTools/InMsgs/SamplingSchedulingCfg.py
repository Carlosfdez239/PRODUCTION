#!/usr/bin/env python3
import os
import sys
import time

import bitstring
import wx
from bitstring import BitArray
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
                w_message_version.SetValue("0")
                w_sch_mode.SetValue(scheduling_modes_list[0])
                w_sch_action.SetValue(scheduling_action_list[0])
                w_skips.SetValue("0")
                w_action_code.SetValue(unconventional_action_code_list[0])
                w_action_data1.SetValue("00")
                w_action_data2.SetValue("00")
                w_action_data3.SetValue("00")
                w_timezone_correction.SetValue("0")
                w_interval_state.SetValue(False)
                w_onetime_n_intervals.SetValue("0")
                for i in one_time_intervals:
                    i[0].SetValue("0")
                    i[1].SetValue("0")
                w_periodic_mode.SetValue(scheduled_mode_periodic_modes[0])
                w_daily_n_intervals.SetValue("0")
                for i in daily_intervals:
                    i[0].SetValue("0")
                    i[1].SetValue("0")
                for w in weekly_intervals:
                    w[0].SetValue("0")
                    for i in w[1]:
                        i[0].SetValue("0")
                        i[1].SetValue("0")

            w_load_config.SetStringSelection(config)

        # method to set the config
        def set_config(event):
            valid_config = True
            error_msg = ""
            try:
                configuration_array = BitArray()
                msg_version = int(w_message_version.GetValue())
                if msg_version != 0:
                    valid_config = False
                    error_msg = "Message version must be 0."
                configuration_array.append(bitstring.pack("uint:3", (msg_version)))

                scheduling_mode = w_sch_mode.GetValue()
                scheduling_mode_int = scheduling_modes_list.index(scheduling_mode)
                configuration_array.append(bitstring.pack("uint:2", scheduling_mode_int))

                sampling_action = w_sch_action.GetValue()
                sampling_action_int = scheduling_action_list.index(sampling_action)
                configuration_array.append(bitstring.pack("uint:1", sampling_action_int))
                if sampling_action == scheduling_action_list[1]:
                    skip = int(w_skips.GetValue())
                    if not 0 <= skip <= 255:
                        valid_config = False
                        error_msg = "Wrong value for the skipped samples."
                    else:
                        configuration_array.append(bitstring.pack("uint:8", skip))

                unconventional_action = w_action_code.GetValue()
                unconventional_action_int = unconventional_action_code_list.index(
                    unconventional_action
                )
                configuration_array.append(bitstring.pack("uint:4", unconventional_action_int))
                if unconventional_action in unconventional_action_code_with_payload_list:
                    for o in [w_action_data1, w_action_data2, w_action_data3]:
                        configuration_array.append(bitstring.pack("uint:8", int(o.GetValue(), 16)))

                timezone = int(w_timezone_correction.GetValue())
                if not -64 <= timezone <= 63:
                    valid_config = False
                    error_msg = "Timezone correction must be in [-64, 63]."
                else:
                    configuration_array.append(bitstring.pack("int:7", timezone))

                interval_state = w_interval_state.GetValue()
                if interval_state:
                    interval_state_int = 1
                else:
                    interval_state_int = 0
                configuration_array.append(bitstring.pack("uint:1", interval_state_int))

                if scheduling_mode == scheduling_modes_list[1]:
                    num_intervals = int(w_onetime_n_intervals.GetValue())
                    if not 0 <= num_intervals <= 14:
                        valid_config = False
                        error_msg = "The number of intervals in one time mode has to be in [0, 14]."
                        num_intervals = 0
                    else:
                        configuration_array.append(bitstring.pack("uint:4", num_intervals))
                    prev = 1
                    for i in range(num_intervals):
                        start = int(one_time_intervals[i][0].GetValue())
                        end = int(one_time_intervals[i][1].GetValue())
                        if i == 0:
                            if not 0 <= start <= (2 ** 23) - 1:
                                valid_config = False
                                error_msg = "The interval 1 start is out of range [0, 2^23-1]."
                                break
                            else:
                                configuration_array.append(bitstring.pack("uint:23", start))
                        else:
                            if not 0 <= start <= (2 ** 10) - 1:
                                valid_config = False
                                error_msg = "The interval %i start is out of range [0, 2^10-1]." % (
                                    i + 1
                                )
                                break
                            if prev > start:
                                valid_config = False
                                error_msg = "The interval %i start is not in order." % (i + 1)
                                break
                            prev = start + 1
                            if valid_config:
                                configuration_array.append(bitstring.pack("uint:10", start))
                        if not 0 <= end <= (2 ** 10) - 1:
                            valid_config = False
                            error_msg = "The interval %i end is out of range [0, 2^10-1]." % (i + 1)
                            break
                        if prev > end:
                            valid_config = False
                            error_msg = "The interval %i invalid duration." % (i + 1)
                            break
                        prev = end
                        if valid_config:
                            configuration_array.append(bitstring.pack("uint:10", end))
                elif scheduling_mode == scheduling_modes_list[2]:
                    period_sch = w_periodic_mode.GetValue()
                    period_sch_int = scheduled_mode_periodic_modes.index(period_sch)
                    configuration_array.append(bitstring.pack("uint:1", period_sch_int))
                    if period_sch == scheduled_mode_periodic_modes[0]:
                        num_intervals = int(w_daily_n_intervals.GetValue())
                        if not 0 <= num_intervals <= 14:
                            valid_config = False
                            error_msg = (
                                "The number of intervals in daily mode has to be in [0, 14]."
                            )
                            num_intervals = 0
                        else:
                            configuration_array.append(bitstring.pack("uint:4", num_intervals))
                        prev = 0
                        for i in range(num_intervals):
                            start = int(daily_intervals[i][0].GetValue())
                            end = int(daily_intervals[i][1].GetValue())
                            if not 0 <= start <= 95:
                                valid_config = False
                                error_msg = "The interval 1 start is out of range [0, 95]."
                                break
                            if prev > start:
                                valid_config = False
                                error_msg = "The interval %i start is not in order." % (i + 1)
                                break
                            prev = start + 1
                            if valid_config:
                                configuration_array.append(bitstring.pack("uint:7", start))
                            if not 0 <= end <= 96:
                                valid_config = False
                                error_msg = "The interval %i end is out of range [0, 96]." % (i + 1)
                                break
                            if prev > end:
                                valid_config = False
                                error_msg = "The interval %i invalid duration." % (i + 1)
                                break
                            prev = end
                            if valid_config:
                                configuration_array.append(bitstring.pack("uint:7", end))
                    else:
                        for w in range(len(scheduled_mode_periodic_weekdays)):
                            num_intervals = int(weekly_intervals[w][0].GetValue())
                            if not 0 <= num_intervals <= 3:
                                valid_config = False
                                error_msg = "The number of daily intervals in weekly mode has to be in [0, 3]."
                                num_intervals = 0
                            else:
                                configuration_array.append(bitstring.pack("uint:2", num_intervals))
                            prev = 0
                            for i in range(num_intervals):
                                start = int(weekly_intervals[w][1][i][0].GetValue())
                                end = int(weekly_intervals[w][1][i][1].GetValue())
                                if not 0 <= start <= 95:
                                    valid_config = False
                                    error_msg = "The inteval %i start is out of range [0, 95]." % (
                                        i + 1
                                    )
                                    break
                                if prev > start:
                                    valid_config = False
                                    error_msg = "The interval %i start is not in order." % (i + 1)
                                    break
                                prev = start + 1
                                if valid_config:
                                    configuration_array.append(bitstring.pack("uint:7", start))
                                if not 0 <= end <= 96:
                                    valid_config = False
                                    error_msg = "The interval %i end is out of range [0, 96]." % (
                                        i + 1
                                    )
                                    break
                                if prev > end:
                                    valid_config = False
                                    error_msg = "The interval %i end invalid duration." % (i + 1)
                                    break
                                prev = end
                                if valid_config:
                                    configuration_array.append(bitstring.pack("uint:7", end))

                if valid_config is False:
                    msgb = wx.MessageDialog(
                        self, "Invalid configuration. " + error_msg, "ERROR", wx.OK | wx.ICON_HAND
                    )
                    msgb.ShowModal()
                    return
            except:
                msgb = wx.MessageDialog(
                    self, "Some field is not an integer", "ERROR", wx.OK | wx.ICON_HAND
                )
                msgb.ShowModal()
                return

            output = "9D"
            output += "".join(["%0.2X" % ord(e) for e in configuration_array.tobytes()])
            output = "\\x" + "\\x".join(a + b for a, b in zip(output[::2], output[1::2]))
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart(output, tty_usb, self)

        # method to request the config
        def request_config(event):
            tty_usb = "/dev/ttyUSB" + w_tty_usb.GetValue()
            ls_send_message_uart("\\x00\\x9D", tty_usb, self)

        def set_custom_config(event):
            w_load_config.SetStringSelection("Custom")

        def set_skips(event):
            scheduling_action = w_sch_action.GetValue()
            if scheduling_action == scheduling_action_list[1]:
                w_skips.Enable()
            else:
                w_skips.Disable()
            w_load_config.SetStringSelection("Custom")

        def set_action_code(event):
            action_code = w_action_code.GetValue()
            if action_code in unconventional_action_code_with_payload_list:
                w_action_data1.Enable()
                w_action_data2.Enable()
                w_action_data3.Enable()
            else:
                w_action_data1.Disable()
                w_action_data2.Disable()
                w_action_data3.Disable()
            w_load_config.SetStringSelection("Custom")

        def set_one_time_num_intervals(event):
            try:
                n_intervals = int(float(w_onetime_n_intervals.GetValue()))
            except ValueError:
                n_intervals = 0

            if n_intervals > 14:
                n_intervals = 14
                w_onetime_n_intervals.SetValue(str(n_intervals))

            for i, o in enumerate(one_time_intervals):
                if i < n_intervals:
                    o[0].Enable()
                    o[1].Enable()
                else:
                    o[0].Disable()
                    o[1].Disable()
            w_load_config.SetStringSelection("Custom")

        def set_daily_num_intervals(event):
            try:
                n_intervals = int(float(w_daily_n_intervals.GetValue()))
            except ValueError:
                n_intervals = 0

            if n_intervals > 14:
                n_intervals = 14
                w_daily_n_intervals.SetValue(str(n_intervals))

            for i, o in enumerate(daily_intervals):
                if i < n_intervals:
                    o[0].Enable()
                    o[1].Enable()
                else:
                    o[0].Disable()
                    o[1].Disable()
            w_load_config.SetStringSelection("Custom")

        def set_weekly_num_intervals(event):
            for w, day in enumerate(scheduled_mode_periodic_weekdays):
                try:
                    n_intervals = int(float(weekly_intervals[w][0].GetValue()))
                except ValueError:
                    n_intervals = 0

                if n_intervals > 3:
                    n_intervals = 3
                    weekly_intervals[w][0].SetValue(str(n_intervals))

                for i, o in enumerate(weekly_intervals[w][1]):
                    if i < n_intervals:
                        o[0].Enable()
                        o[1].Enable()
                    else:
                        o[0].Disable()
                        o[1].Disable()
            w_load_config.SetStringSelection("Custom")

        def set_scheduling_mode(event):
            scheduling_mode = w_sch_mode.GetValue()
            if scheduling_mode == scheduling_modes_list[0]:
                for o in one_time_elements:
                    o.Hide()
                for o in periodic_elements:
                    o.Hide()
                for o in daily_elements:
                    o.Hide()
                for o in weekly_elements:
                    o.Hide()
            elif scheduling_mode == scheduling_modes_list[1]:
                for o in one_time_elements:
                    o.Show()
                for o in periodic_elements:
                    o.Hide()
                for o in daily_elements:
                    o.Hide()
                for o in weekly_elements:
                    o.Hide()
            else:
                for o in one_time_elements:
                    o.Hide()
                for o in periodic_elements:
                    o.Show()
                periodic_mode = w_periodic_mode.GetValue()
                if periodic_mode == scheduled_mode_periodic_modes[0]:
                    for o in daily_elements:
                        o.Show()
                    for o in weekly_elements:
                        o.Hide()
                else:
                    for o in daily_elements:
                        o.Hide()
                    for o in weekly_elements:
                        o.Show()
            w_load_config.SetStringSelection("Custom")

        def set_periodic_mode(event):
            scheduling_mode = w_sch_mode.GetValue()
            if scheduling_mode == scheduling_modes_list[2]:
                periodic_mode = w_periodic_mode.GetValue()
                if periodic_mode == scheduled_mode_periodic_modes[0]:
                    for o in daily_elements:
                        o.Show()
                    for o in weekly_elements:
                        o.Hide()
                else:
                    for o in daily_elements:
                        o.Hide()
                    for o in weekly_elements:
                        o.Show()
                w_load_config.SetStringSelection("Custom")

        def update_current_time(event):
            timer.Start(1000)
            current_time = int(time.time() / (15 * 60))
            w_current_time.SetValue(str(current_time))
            w_offset_time.SetValue(str(current_time + int(w_result.GetValue())))

        def get_time(event):
            fail = False
            try:
                hours = int(float(w_hours.GetValue()))
                mins = int(float(w_mins.GetValue()))
                if 0 > hours > 25:
                    fail = True
                if 0 > mins or mins % 15 != 0:
                    fail = True
            except:
                fail = True
            if fail:
                w_result.SetValue(str(0))
                msgb = wx.MessageDialog(
                    self,
                    "Error reading the time. The mins need to be in 15min intervals",
                    "ERROR",
                    wx.OK | wx.ICON_HAND,
                )
                msgb.ShowModal()
                return
            t = (hours * 4) + (mins / 15)
            w_result.SetValue(str(t))
            current_time = int(w_current_time.GetValue())
            w_offset_time.SetValue(str(t + current_time))

        def set_offset(event):
            one_time_intervals[0][0].SetValue(w_offset_time.GetValue())

        tty_prefix = "/dev/ttyUSB"
        vertical_pos = 20
        horizontal_pos = 20
        vertical_pos_increment = 35

        pnl = wx.Panel(self, -1)

        wx.StaticText(pnl, label="ttyUSB Number", pos=(115, vertical_pos + 6))
        w_tty_usb = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(20, vertical_pos))
        w_tty_usb.SetMaxLength(10)
        w_tty_usb.WriteText(global_tty[global_tty.index(tty_prefix) + len(tty_prefix) :])
        vertical_pos = vertical_pos + vertical_pos_increment

        scheduling_modes_list = ["Disabled", "One Time Mode", "Periodic Mode"]
        scheduling_action_list = ["Disable sampling", "Skip samples"]
        unconventional_action_code_list = [
            "Normal sample",
            "Common action 1",
            "Common action 2",
            "Common action 3",
            "Common action 4",
            "Common action 5",
            "Common action 6",
            "Common action 7",
            "Node action 1",
            "Node action 2",
            "Node action 3",
            "Node action 4",
            "Node action 5",
            "Node action 6",
            "Node action 7",
            "Extended action",
        ]
        unconventional_action_code_with_payload_list = [
            "Common action 4",
            "Common action 5",
            "Common action 6",
            "Common action 7",
            "Node action 4",
            "Node action 5",
            "Node action 6",
            "Node action 7",
            "Extended action",
        ]
        scheduled_mode_periodic_modes = ["Daily", "Weekly"]
        scheduled_mode_periodic_weekdays = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        wx.StaticText(pnl, label="Config version", pos=(20, vertical_pos + 6))
        w_message_version = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(180, vertical_pos))
        w_message_version.SetMaxLength(1)
        w_message_version.WriteText("0")
        w_message_version.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="Scheduling Mode", pos=(20, vertical_pos + 6))
        w_sch_mode = wx.ComboBox(
            pnl,
            500,
            value=scheduling_modes_list[0],
            size=(170, 30),
            pos=(180, vertical_pos),
            choices=scheduling_modes_list,
        )
        w_sch_mode.Bind(wx.EVT_TEXT, set_scheduling_mode)
        vertical_pos += vertical_pos_increment

        # Helper
        vertical_pos_h = vertical_pos + 20
        wx.StaticText(pnl, label="Helper", pos=(480, vertical_pos_h))
        vertical_pos_h += vertical_pos_increment - 10

        wx.StaticText(pnl, label="Current time (15min steps):", pos=(400, vertical_pos_h))
        vertical_pos_h += vertical_pos_increment // 2
        w_current_time = wx.TextCtrl(
            pnl, -1, size=(140, 30), pos=(460, vertical_pos_h), style=wx.TE_READONLY | wx.TE_RIGHT
        )
        w_current_time.WriteText(str(int(time.time() / (15 * 60))))
        vertical_pos_h += vertical_pos_increment

        timer_id = 100
        timer = wx.Timer(pnl, timer_id)
        timer.Start(1000)
        pnl.Bind(wx.EVT_TIMER, update_current_time)

        wx.StaticText(pnl, label="Hours:", pos=(400, vertical_pos_h))
        wx.StaticText(pnl, label="Mins:", pos=(455, vertical_pos_h))
        vertical_pos_h += vertical_pos_increment // 2
        w_hours = wx.TextCtrl(pnl, -1, size=(50, 30), pos=(400, vertical_pos_h))
        w_hours.SetMaxLength(2)
        w_hours.WriteText("00")
        w_mins = wx.TextCtrl(pnl, -1, size=(50, 30), pos=(455, vertical_pos_h))
        w_mins.SetMaxLength(4)
        w_mins.WriteText("00")
        w_get_time_btn = wx.Button(pnl, label="Get Time", pos=(510, vertical_pos_h))
        w_get_time_btn.Bind(wx.EVT_BUTTON, get_time)
        vertical_pos_h += vertical_pos_increment
        wx.StaticText(pnl, label="Result:", pos=(400, vertical_pos_h + 6))
        w_result = wx.TextCtrl(
            pnl, -1, size=(150, 30), pos=(450, vertical_pos_h), style=wx.TE_READONLY | wx.TE_RIGHT
        )
        w_result.WriteText("0")
        vertical_pos_h += vertical_pos_increment

        wx.StaticText(pnl, label="Current time + Result:", pos=(400, vertical_pos_h))
        vertical_pos_h += vertical_pos_increment // 2
        wx.StaticText(pnl, label="Offset:", pos=(400, vertical_pos_h + 6))
        w_offset_time = wx.TextCtrl(
            pnl, -1, size=(140, 30), pos=(460, vertical_pos_h), style=wx.TE_READONLY | wx.TE_RIGHT
        )
        w_offset_time.WriteText(str(int(time.time() / (15 * 60)) + int(w_result.GetValue())))
        # Helper done

        wx.StaticText(pnl, label="Scheduling Action", pos=(20, vertical_pos + 6))
        w_sch_action = wx.ComboBox(
            pnl,
            500,
            value=scheduling_action_list[0],
            size=(170, 30),
            pos=(180, vertical_pos),
            choices=scheduling_action_list,
        )
        w_sch_action.Bind(wx.EVT_TEXT, set_skips)
        vertical_pos += vertical_pos_increment
        wx.StaticText(pnl, label="N skipped", pos=(40, vertical_pos + 6))
        w_skips = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(190, vertical_pos))
        w_skips.SetMaxLength(3)
        w_skips.WriteText("000")
        w_skips.Bind(wx.EVT_TEXT, set_custom_config)
        w_skips.Disable()
        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="Unconventional Action", pos=(20, vertical_pos + 6))
        w_action_code = wx.ComboBox(
            pnl,
            500,
            value=unconventional_action_code_list[0],
            size=(170, 30),
            pos=(180, vertical_pos),
            choices=unconventional_action_code_list,
        )
        w_action_code.Bind(wx.EVT_TEXT, set_action_code)
        vertical_pos += vertical_pos_increment
        wx.StaticText(pnl, label="Action Data (hex)", pos=(40, vertical_pos + 6))
        w_action_data1 = wx.TextCtrl(pnl, -1, size=(50, 30), pos=(190, vertical_pos))
        w_action_data1.SetMaxLength(2)
        w_action_data1.WriteText("00")
        w_action_data1.Bind(wx.EVT_TEXT, set_custom_config)
        w_action_data1.Disable()
        w_action_data2 = wx.TextCtrl(pnl, -1, size=(50, 30), pos=(250, vertical_pos))
        w_action_data2.SetMaxLength(2)
        w_action_data2.WriteText("00")
        w_action_data2.Bind(wx.EVT_TEXT, set_custom_config)
        w_action_data2.Disable()
        w_action_data3 = wx.TextCtrl(pnl, -1, size=(50, 30), pos=(310, vertical_pos))
        w_action_data3.SetMaxLength(2)
        w_action_data3.WriteText("00")
        w_action_data3.Bind(wx.EVT_TEXT, set_custom_config)
        w_action_data3.Disable()
        vertical_pos += vertical_pos_increment

        wx.StaticText(pnl, label="Timezone correction", pos=(20, vertical_pos + 6))
        w_timezone_correction = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(180, vertical_pos))
        w_timezone_correction.SetMaxLength(3)
        w_timezone_correction.WriteText("0")
        w_timezone_correction.Bind(wx.EVT_TEXT, set_custom_config)
        vertical_pos += int(vertical_pos_increment * 0.75)

        wx.StaticText(pnl, label="Interval state", pos=(20, vertical_pos + 6))
        w_interval_state = wx.CheckBox(pnl, label="", pos=(180, vertical_pos + 6))
        w_interval_state.SetValue(False)
        w_interval_state.Bind(wx.EVT_CHECKBOX, set_custom_config)
        vertical_pos += vertical_pos_increment

        # --- Interval Data ---
        text = wx.StaticText(pnl, -1, label="Interval_data:        ", pos=(20, vertical_pos + 6))
        font = wx.Font(
            10,
            wx.DEFAULT,
            wx.NORMAL,
            wx.BOLD,
            underline=False,
            faceName="",
            encoding=wx.FONTENCODING_DEFAULT,
        )
        text.SetFont(font)

        # -- One Time mode --
        vertical_pos_i = vertical_pos
        vertical_pos_temp = vertical_pos
        one_time_elements = []

        one_time_elements.append(
            wx.StaticText(pnl, label="One Time Mode", pos=(160, vertical_pos_i))
        )
        vertical_pos_i += vertical_pos_increment

        one_time_elements.append(
            wx.StaticText(pnl, label="Num intervals", pos=(40, vertical_pos_i + 6))
        )
        w_onetime_n_intervals = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(180, vertical_pos_i))
        w_onetime_n_intervals.SetMaxLength(2)
        w_onetime_n_intervals.WriteText("0")
        w_onetime_n_intervals.Bind(wx.EVT_TEXT, set_one_time_num_intervals)
        one_time_elements.append(w_onetime_n_intervals)
        vertical_pos_i += vertical_pos_increment

        w_set_offset_btn = wx.Button(pnl, label="Set offset", pos=(510, vertical_pos_i))
        w_set_offset_btn.Bind(wx.EVT_BUTTON, set_offset)
        one_time_elements.append(w_set_offset_btn)

        one_time_intervals = []
        for i in range(1, 15):
            one_time_elements.append(
                wx.StaticText(pnl, label="Interval %u Init/End" % i, pos=(60, vertical_pos_i + 6))
            )
            w_onetime_interval_init = wx.TextCtrl(
                pnl, -1, size=(140, 30), pos=(200, vertical_pos_i)
            )
            w_onetime_interval_init.SetMaxLength(10)
            w_onetime_interval_init.WriteText("0")
            w_onetime_interval_init.Bind(wx.EVT_TEXT, set_custom_config)
            w_onetime_interval_init.Disable()
            one_time_elements.append(w_onetime_interval_init)
            w_onetime_interval_end = wx.TextCtrl(pnl, -1, size=(140, 30), pos=(350, vertical_pos_i))
            w_onetime_interval_end.SetMaxLength(10)
            w_onetime_interval_end.WriteText("0")
            w_onetime_interval_end.Bind(wx.EVT_TEXT, set_custom_config)
            w_onetime_interval_end.Disable()
            one_time_elements.append(w_onetime_interval_end)
            one_time_intervals.append([w_onetime_interval_init, w_onetime_interval_end])
            vertical_pos_i += vertical_pos_increment

        for o in one_time_elements:
            o.Hide()
        vertical_pos_temp = max(vertical_pos_temp, vertical_pos_i)

        # -- Periodic mode --
        vertical_pos_i = vertical_pos
        periodic_elements = []

        periodic_elements.append(
            wx.StaticText(pnl, label="Periodic Mode", pos=(160, vertical_pos_i + 6))
        )
        vertical_pos_i += vertical_pos_increment

        periodic_elements.append(
            wx.StaticText(pnl, label="Periodic Mode", pos=(40, vertical_pos_i + 6))
        )
        w_periodic_mode = wx.ComboBox(
            pnl,
            500,
            value=scheduled_mode_periodic_modes[0],
            size=(170, 30),
            pos=(180, vertical_pos_i),
            choices=scheduled_mode_periodic_modes,
        )
        w_periodic_mode.Bind(wx.EVT_TEXT, set_periodic_mode)
        periodic_elements.append(w_periodic_mode)
        vertical_pos_i += vertical_pos_increment
        for o in periodic_elements:
            o.Hide()

        # - Daily mode -
        vertical_pos_j = vertical_pos_i
        daily_elements = []

        daily_elements.append(
            wx.StaticText(pnl, label="num intervals", pos=(40, vertical_pos_j + 6))
        )
        w_daily_n_intervals = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(180, vertical_pos_j))
        w_daily_n_intervals.SetMaxLength(2)
        w_daily_n_intervals.WriteText("0")
        w_daily_n_intervals.Bind(wx.EVT_TEXT, set_daily_num_intervals)
        daily_elements.append(w_daily_n_intervals)
        vertical_pos_j += vertical_pos_increment

        daily_intervals = []
        for i in range(1, 15):
            daily_elements.append(
                wx.StaticText(pnl, label="Interval %u Init/End" % i, pos=(60, vertical_pos_j + 6))
            )
            w_daily_interval_init = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(200, vertical_pos_j))
            w_daily_interval_init.SetMaxLength(10)
            w_daily_interval_init.WriteText("0")
            w_daily_interval_init.Bind(wx.EVT_TEXT, set_custom_config)
            w_daily_interval_init.Disable()
            daily_elements.append(w_daily_interval_init)
            w_daily_interval_end = wx.TextCtrl(pnl, -1, size=(90, 30), pos=(300, vertical_pos_j))
            w_daily_interval_end.SetMaxLength(10)
            w_daily_interval_end.WriteText("0")
            w_daily_interval_end.Bind(wx.EVT_TEXT, set_custom_config)
            w_daily_interval_end.Disable()
            daily_elements.append(w_daily_interval_end)
            daily_intervals.append([w_daily_interval_init, w_daily_interval_end])
            vertical_pos_j += vertical_pos_increment
        for o in daily_elements:
            o.Hide()

        vertical_pos_temp = max(vertical_pos_temp, vertical_pos_j)

        # - Weekly mode -
        vertical_pos_j = vertical_pos_i
        weekly_elements = []

        i = 0
        weekly_intervals = []

        for w in scheduled_mode_periodic_weekdays:
            horizontal_pos = 20
            horizontal_pos_increment_1 = 60
            horizontal_pos_increment_2 = 75
            horizontal_pos_increment_3 = 90

            weekly_elements.append(
                wx.StaticText(pnl, label=w + ":", pos=(horizontal_pos, vertical_pos_j))
            )
            horizontal_pos += horizontal_pos_increment_3
            weekly_elements.append(
                wx.StaticText(pnl, label="N intervals", pos=(horizontal_pos, vertical_pos_j))
            )
            w_week_n_intervals = wx.TextCtrl(
                pnl,
                -1,
                size=(50, 30),
                pos=(horizontal_pos, vertical_pos_j + vertical_pos_increment // 2),
            )
            horizontal_pos += horizontal_pos_increment_3
            w_week_n_intervals.SetMaxLength(2)
            w_week_n_intervals.WriteText("0")
            w_week_n_intervals.Bind(wx.EVT_TEXT, set_weekly_num_intervals)
            weekly_elements.append(w_week_n_intervals)

            day_intervals = []
            for i in range(1, 4):
                weekly_elements.append(
                    wx.StaticText(
                        pnl,
                        label="Init %u        End %u" % (i, i),
                        pos=(horizontal_pos, vertical_pos_j),
                    )
                )
                w_week_interval_init = wx.TextCtrl(
                    pnl,
                    -1,
                    size=(50, 30),
                    pos=(horizontal_pos, vertical_pos_j + vertical_pos_increment // 2),
                )
                w_week_interval_init.SetMaxLength(10)
                w_week_interval_init.WriteText("0")
                w_week_interval_init.Bind(wx.EVT_TEXT, set_custom_config)
                w_week_interval_init.Disable()
                weekly_elements.append(w_week_interval_init)
                horizontal_pos += horizontal_pos_increment_1
                w_week_interval_end = wx.TextCtrl(
                    pnl,
                    -1,
                    size=(50, 30),
                    pos=(horizontal_pos, vertical_pos_j + vertical_pos_increment // 2),
                )
                w_week_interval_end.SetMaxLength(10)
                w_week_interval_end.WriteText("0")
                w_week_interval_end.Bind(wx.EVT_TEXT, set_custom_config)
                w_week_interval_end.Disable()
                weekly_elements.append(w_week_interval_end)
                horizontal_pos += horizontal_pos_increment_2
                day_intervals.append([w_week_interval_init, w_week_interval_end])
            weekly_intervals.append([w_week_n_intervals, day_intervals])
            vertical_pos_j += int(vertical_pos_increment * 1.7)
        for o in weekly_elements:
            o.Hide()

        vertical_pos_temp = max(vertical_pos_temp, vertical_pos_j)

        vertical_pos = vertical_pos_temp

        vertical_pos = vertical_pos + vertical_pos_increment // 2
        w_set_config_btn = wx.Button(pnl, label="Set Config", pos=(400, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, set_config)

        w_set_config_btn = wx.Button(pnl, label="Request Config", pos=(400 + 90, vertical_pos))
        w_set_config_btn.Bind(wx.EVT_BUTTON, request_config)

        configs_list = ["Custom", "Default"]
        wx.StaticText(pnl, label="Load preset configs", pos=(400, 20))
        w_load_config = wx.ComboBox(
            pnl,
            500,
            value="0",
            size=(200, 30),
            pos=(400, 20 + vertical_pos_increment // 2),
            choices=configs_list,
            style=wx.CB_READONLY,
        )
        w_load_config.Bind(wx.EVT_COMBOBOX, load_config)
        w_load_config.SetStringSelection("Default")
        load_config(0)

        vertical_pos = vertical_pos + vertical_pos_increment
        self.SetSize((620, vertical_pos))
        self.SetTitle("SamplingSchedulerCfg")
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
