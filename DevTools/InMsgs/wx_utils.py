from datetime import datetime

import wx
import wx.adv
from ls_message_parsing.utils.named_enum import NamedEnum


class ConfigType(NamedEnum):
    FIELD = 0
    DROPDOWN = 1
    BOOL = 2
    BITWISE = 3
    CHANNEL = 4
    DATE = 5


class LSPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent)
        self.parent = parent


class LabelInput(wx.Panel):
    def __init__(
        self,
        parent,
        label="Value",
        initial_value="",
        flag=wx.ALL,  # Default flag without alignment conflicts
        border=5,
    ):
        super(LabelInput, self).__init__(parent)

        self._flag = flag
        self._border = border

        # Create the sizer for this component
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the label (left-aligned by default)
        self.label = wx.StaticText(self, label=label)
        self.sizer.Add(
            self.label,
            proportion=0,
            flag=wx.ALIGN_CENTER_VERTICAL | self._flag,
            border=self._border,
        )

        # Add a spacer to push the text control to the right
        self.sizer.AddStretchSpacer()

        # Create the text control with right-aligned text (right-aligned inside the control)
        self.text_ctrl = wx.TextCtrl(self, value=initial_value, style=wx.TE_RIGHT)
        self.sizer.Add(
            self.text_ctrl,
            proportion=1,
            flag=wx.EXPAND | self._flag,
            border=self._border,
        )

        # Set the sizer for the panel
        self.SetSizer(self.sizer)

        # Bind events
        self.text_ctrl.Bind(wx.EVT_TEXT, self.on_text_change)

    def on_text_change(self, event):
        event.Skip()  # Ensure the event is propagated to other handlers, if necessary

    def get_value(self):
        value = self.text_ctrl.GetValue()
        try:
            # Attempt to convert the value to an integer
            return int(value)
        except ValueError:
            # If conversion fails, return the value as a string
            return value

    def set_value(self, value):
        self.text_ctrl.SetValue(str(value))

    def set_label(self, label):
        self.label.SetLabel(label)


class LabelComboBox(wx.Panel):
    def __init__(
        self,
        parent,
        label="Select Option",
        initial_value="",
        choices=None,
        flag=wx.ALL,
        border=5,
    ):
        super(LabelComboBox, self).__init__(parent)

        if choices is None:
            choices = []

        self._flag = flag
        self._border = border

        # Create the sizer for this component
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the label (left-aligned by default)
        self.label = wx.StaticText(self, label=label)
        self.sizer.Add(
            self.label,
            proportion=0,
            flag=wx.ALIGN_CENTER_VERTICAL | self._flag,
            border=self._border,
        )

        # Add a spacer to push the ComboBox to the right
        self.sizer.AddStretchSpacer()

        # Create the ComboBox (right-aligned by the spacer)
        self.combo_box = wx.ComboBox(
            self,
            value=initial_value,
            choices=choices,
            style=wx.CB_READONLY,
        )
        self.sizer.Add(
            self.combo_box,
            proportion=0,
            flag=wx.ALIGN_CENTER_VERTICAL | self._flag,
            border=self._border,
        )

        # Set the sizer for the panel
        self.SetSizer(self.sizer)

    def get_value(self):
        return self.combo_box.GetValue()

    def set_value(self, value):
        self.combo_box.SetValue(value)

    def set_label(self, label):
        self.label.SetLabel(label)


class LabelCheckBox(wx.Panel):
    def __init__(
        self,
        parent,
        label="Option",
        initial_value=False,
        flag=wx.ALL,
        border=5,
    ):
        super(LabelCheckBox, self).__init__(parent)

        self._flag = flag
        self._border = border

        # Create the sizer for this component
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the label (left-aligned by default)
        self.label = wx.StaticText(self, label=label)
        self.sizer.Add(
            self.label,
            proportion=0,
            flag=wx.ALIGN_CENTER_VERTICAL | self._flag,
            border=self._border,
        )

        # Add a spacer to push the checkbox to the right
        self.sizer.AddStretchSpacer()

        # Create the checkbox (right-aligned)
        self.check_box = wx.CheckBox(self)
        self.check_box.SetValue(initial_value)
        self.sizer.Add(
            self.check_box,
            proportion=0,
            flag=wx.ALIGN_CENTER_VERTICAL | self._flag,
            border=self._border,
        )

        # Set the sizer for the panel
        self.SetSizer(self.sizer)

    def get_value(self):
        return self.check_box.GetValue()

    def set_value(self, value):
        self.check_box.SetValue(value)

    def set_label(self, label):
        self.label.SetLabel(label)

    def enable(self, enable=True):
        """Enable or disable the checkbox."""
        self.check_box.Enable(enable)


class BitwiseCheckPanel(wx.Panel):
    def __init__(self, parent, label="Bitwise Config", bit_labels=None, initial_value=0):
        super(BitwiseCheckPanel, self).__init__(parent)

        self.num_bits = (
            len(bit_labels) if bit_labels else 5
        )  # Default to 5 bits if no labels provided
        self.check_buttons = []
        self.initial_value = initial_value

        if bit_labels is not None:
            self.bit_labels = bit_labels
        else:
            self.bit_labels = {}

        # Create the main sizer
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add main label
        main_label = wx.StaticText(self, label=label)
        main_sizer.Add(main_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)

        # Add check buttons with labels
        for i in range(self.num_bits):
            bit_sizer = wx.BoxSizer(wx.VERTICAL)

            chk = wx.CheckBox(self)
            bit_sizer.Add(chk, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=2)
            self.check_buttons.append(chk)

            if bit_labels and i < len(bit_labels):
                bit_label = wx.StaticText(self, label=bit_labels[i])
                bit_sizer.Add(bit_label, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=2)

            main_sizer.Add(bit_sizer, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)

        # Set the initial value
        self.set_value(self.initial_value)

        # Set the sizer
        self.SetSizer(main_sizer)

    def set_value(self, value):
        """Set the checkboxes according to the provided uint value."""
        for i in range(self.num_bits):
            bit_value = (value >> i) & 1
            self.check_buttons[i].SetValue(bool(bit_value))

    def get_value(self):
        """Return a dictionary with bit labels and their corresponding boolean values."""
        return {self.bit_labels[i]: self.check_buttons[i].GetValue() for i in range(self.num_bits)}


class Channel(wx.Panel):
    def __init__(
        self, parent, id, value_key="value", label="Channel", initial_value=(True, 0), enabled=True
    ):
        super(Channel, self).__init__(parent)

        self.channel_id = id
        self.value_key = value_key  # The key for the value in the returned dictionary
        self.initial_enabled, self.initial_value = initial_value
        # Create the main sizer
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the label (left-aligned by default)
        self.label = wx.StaticText(self, label=f"{label}")
        self.sizer.Add(
            self.label,
            proportion=0,
            flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL,
            border=5,
        )

        # Create the text control
        self.text_ctrl = wx.TextCtrl(self, value=str(self.initial_value))
        self.sizer.Add(
            self.text_ctrl,
            proportion=1,
            flag=wx.EXPAND | wx.ALL,
            border=5,
        )

        # Create the checkbox
        self.checkbox = wx.CheckBox(self)
        self.checkbox.SetValue(self.initial_enabled)
        self.sizer.Add(
            self.checkbox,
            proportion=0,
            flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL,
            border=5,
        )

        # Set the sizer for the panel
        self.SetSizer(self.sizer)

    def get_value(self):
        """Return the current value of the channel as a dictionary."""
        value = self.text_ctrl.GetValue()
        try:
            # Attempt to convert the value to an integer
            value = int(value)
        except ValueError:
            # If conversion fails, keep it as a string
            pass

        return {
            "channel": self.channel_id,
            self.value_key: value,  # Use the custom key for the value
            "enabled": self.checkbox.GetValue(),
        }

    def set_value(self, value):
        """Set the value of the text control."""
        self.text_ctrl.SetValue(str(value))

    def set_enabled(self, enabled):
        """Set the checkbox value."""
        self.checkbox.SetValue(enabled)

    def set_label(self, label):
        """Set the label text."""
        self.label.SetLabel(label)


class LabelDateTimePicker(wx.Panel):
    def __init__(
        self,
        parent,
        label="Date and Time",
        initial_date=None,
        initial_time=None,
        flag=wx.ALL,
        border=5,
    ):
        super(LabelDateTimePicker, self).__init__(parent)

        self._flag = flag
        self._border = border

        if initial_date is None:
            initial_date = wx.DateTime.Now()
        if initial_time is None:
            initial_time = wx.DateTime.Now()

        # Create the sizer for this component
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the label (left-aligned by default)
        self.label = wx.StaticText(self, label=label)
        self.sizer.Add(
            self.label,
            proportion=0,
            flag=wx.ALIGN_CENTER_VERTICAL | self._flag,
            border=self._border,
        )

        # Add a spacer to push the date and time pickers to the right
        self.sizer.AddStretchSpacer()

        # Create the date picker (right-aligned)
        self.date_picker = wx.adv.DatePickerCtrl(
            self, dt=initial_date, style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY
        )
        self.sizer.Add(
            self.date_picker,
            proportion=0,
            flag=wx.ALIGN_CENTER_VERTICAL | self._flag,
            border=self._border,
        )

        # Create the time picker (right-aligned)
        self.time_picker = wx.adv.TimePickerCtrl(self, dt=initial_time)
        self.sizer.Add(
            self.time_picker,
            proportion=0,
            flag=wx.ALIGN_CENTER_VERTICAL | self._flag,
            border=self._border,
        )

        # Set the sizer for the panel
        self.SetSizer(self.sizer)

    def get_value(self):
        """Return the selected date and time as a `datetime` object."""
        date = self.date_picker.GetValue()
        time = self.time_picker.GetValue()
        return datetime(
            year=date.GetYear(),
            month=date.GetMonth() + 1,  # wx.DateTime months are 0-based
            day=date.GetDay(),
            hour=time.GetHour(),
            minute=time.GetMinute(),
            second=time.GetSecond(),
        )

    def set_value(self, date_time):
        """Set the date and time pickers based on a `datetime` object."""
        if date_time is not None:
            wx_date = wx.DateTime.FromDMY(date_time.day, date_time.month - 1, date_time.year)
            wx_time = wx.DateTime.FromHMS(date_time.hour, date_time.minute, date_time.second)
        else:
            wx_date = wx.DateTime.Now()
            wx_time = wx.DateTime.Now()

        self.date_picker.SetValue(wx_date)
        self.time_picker.SetValue(wx_time)

    def set_label(self, label):
        """Set the label text."""
        self.label.SetLabel(label)

    def enable(self, enable=True):
        """Enable or disable the date and time pickers."""
        self.date_picker.Enable(enable)
        self.time_picker.Enable(enable)


class LSConfigParam:
    def __init__(self, name, default, config_type, choices=None, id=None, value_key=None):
        self.name = name
        self.default = default
        self.config_type = config_type
        self.choices = choices
        self.id = id
        self.value_key = value_key


def create_from_config(panel, config):
    if config.config_type == ConfigType.FIELD:
        return LabelInput(panel, label=config.name, initial_value=str(config.default))
    if config.config_type == ConfigType.DROPDOWN:
        return LabelComboBox(
            panel,
            label=config.name,
            initial_value=str(config.default),
            choices=config.choices,
        )
    if config.config_type == ConfigType.BOOL:
        return LabelCheckBox(panel, label=config.name, initial_value=config.default)
    if config.config_type == ConfigType.BITWISE:
        return BitwiseCheckPanel(
            panel,
            label=config.name,
            bit_labels=config.choices,
            initial_value=config.default,
        )
    if config.config_type == ConfigType.CHANNEL:
        return Channel(
            panel,
            id=config.id,
            label=config.name,
            value_key=config.value_key,
            initial_value=config.default,
        )
    if config.config_type == ConfigType.DATE:
        return LabelDateTimePicker(panel, label=config.name)


class BaseConfigPanel(wx.Panel):
    def __init__(
        self, parent, usb_label="ttyUSB", get_label="Request config", set_label="Set config"
    ):
        super(BaseConfigPanel, self).__init__(parent)

        # Store the labels
        self.usb_label = usb_label
        self.get_label = get_label
        self.set_label = set_label

        # Initialize the main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Top Section: USB component on the left, with a line underneath
        self.usb_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.usb = LabelInput(self, label=self.usb_label, initial_value="0")
        self.usb_sizer.Add(self.usb, flag=wx.ALL, border=5)

        self.main_sizer.Add(self.usb_sizer, flag=wx.EXPAND | wx.ALL, border=5)

        # Add a line underneath the USB component, spanning the full width
        self.line1 = wx.StaticLine(self)
        self.main_sizer.Add(self.line1, flag=wx.EXPAND | wx.ALL, border=5)

        # Set the sizer
        self.SetSizer(self.main_sizer)

    def add_line(self):
        """Add a horizontal line to separate sections."""
        line = wx.StaticLine(self)
        self.main_sizer.Add(line, flag=wx.EXPAND | wx.ALL, border=5)
        return line

    def add_buttons(self):
        """Add the Get and Set buttons to the bottom of the layout."""
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.w_get_config_btn = wx.Button(self, label=self.get_label)
        self.button_sizer.AddStretchSpacer()
        self.button_sizer.Add(self.w_get_config_btn, flag=wx.ALL, border=5)
        self.w_set_config_btn = wx.Button(self, label=self.set_label)
        self.button_sizer.Add(self.w_set_config_btn, flag=wx.ALL, border=5)
        self.main_sizer.Add(self.button_sizer, flag=wx.EXPAND | wx.ALL, border=5)

    def update_min_size(self):
        # Calculate the minimum width and height required for the layout
        min_width = self.main_sizer.GetMinSize().GetWidth() + 20
        min_height = self.main_sizer.GetMinSize().GetHeight() + 20  # Extra padding

        # Set the minimum size of the panel based on the calculated dimensions
        self.SetMinSize((min_width, min_height))
        self.SetSize((min_width, min_height))


class ConfigPanel(BaseConfigPanel):
    def __init__(self, parent, config, usb_label="ttyUSB", get_label="Get", set_label="Set"):
        super(ConfigPanel, self).__init__(parent, usb_label, get_label, set_label)

        # Middle Section: A vertical sizer for the parameters
        param_sizer = wx.BoxSizer(wx.VERTICAL)

        # Add parameters to the vertical sizer
        self.config_inputs = {}
        for ci in config:
            comp = create_from_config(self, ci)
            self.config_inputs[ci.name] = comp
            param_sizer.Add(comp, flag=wx.EXPAND | wx.ALL, border=5)

        # Add the param sizer to the main sizer
        self.main_sizer.Insert(2, param_sizer, flag=wx.EXPAND | wx.ALL, border=5)

        # Add another line underneath the parameters section
        self.add_line()

        # Finalize layout
        self.Layout()
        self.update_min_size(self.usb_sizer, param_sizer, self.button_sizer)


class DualConfigPanel(BaseConfigPanel):
    def __init__(
        self,
        frame,
        parent,
        left_config,
        right_config,
        usb_label="ttyUSB",
        get_label="Request config",
        set_label="Set config",
        load_defaults_label="Load Defaults",  # Add a label for the "Load Defaults" button
    ):
        super(DualConfigPanel, self).__init__(parent, usb_label, get_label, set_label)

        self.frame = frame
        self.default_config = {
            "left": left_config,
            "right": right_config,
        }  # Store default configurations
        self.horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.left_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)

        self.config_inputs = {}
        for ci in left_config:
            comp = create_from_config(self, ci)
            self.config_inputs[ci.name] = comp
            self.left_sizer.Add(comp, flag=wx.EXPAND | wx.ALL, border=5)

        for ci in right_config:
            comp = create_from_config(self, ci)
            self.config_inputs[ci.name] = comp
            self.right_sizer.Add(comp, flag=wx.EXPAND | wx.ALL, border=5)

        self.horizontal_sizer.Add(self.left_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        self.horizontal_sizer.Add(self.right_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        self.main_sizer.Add(self.horizontal_sizer, flag=wx.EXPAND | wx.ALL, border=5)

        self.add_line()

        self.add_buttons()

        # Add the Load Defaults button
        self.w_load_defaults_btn = wx.Button(self, label=load_defaults_label)
        self.button_sizer.Add(self.w_load_defaults_btn, flag=wx.ALL, border=5)
        self.w_load_defaults_btn.Bind(
            wx.EVT_BUTTON, self.frame.load_default
        )  # Bind the button to load_default

        self.Layout()
        self.update_min_size()

    def update_min_size(self):
        usb_size = self.usb_sizer.GetMinSize()
        horizontal_size = self.horizontal_sizer.GetMinSize()
        button_size = self.button_sizer.GetMinSize()

        min_width = (
            max(usb_size.GetWidth(), horizontal_size.GetWidth(), button_size.GetWidth()) + 40
        )
        min_height = (
            usb_size.GetHeight() + horizontal_size.GetHeight() + button_size.GetHeight() + 110
        )

        self.frame.SetMinSize((min_width, min_height))
        self.frame.SetSize((min_width, min_height))
