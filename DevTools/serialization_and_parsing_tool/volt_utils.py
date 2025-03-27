def get_converted_volt_input_type(input_type, counts):
    """
    See formulas applied in the doc
    https://docs.google.com/document/d/1sDL9869HDK6o8254ZadrQfklMbS1GZYLa_T09M0AJOE/edit#heading=h.qswy9q5dul9s
    """
    if "Voltage" == input_type:
        v_ref = 4.5
        at = -5.0
        volts = at * (((v_ref / 2.0 ** 24) * counts) - (v_ref / 2))
        msg = "%.7f" % volts
    elif "Gauge" == input_type:
        adc_gain = 128.0
        gauges = 1000.0 / adc_gain * ((counts / 2.0 ** 23) - 1.0)
        msg = "%.7f" % gauges
    elif "Thermistor" == input_type:
        r_offset = 2020.0
        r_f = 1000.0
        r_b = 10000.0
        r_a = r_f + r_b
        ohms = ((counts * r_a) / (2.0 ** 24 - counts)) - r_offset
        msg = "%.7f" % ohms
    elif "Current" == input_type:
        v_ref = 4.5
        r = 200.0
        v_uni = v_ref * (counts / 2.0 ** 24)
        ampers = v_uni / r * 1000.0
        msg = "%.7f" % ampers
    elif "PTC" == input_type:
        v_ref = 4.5
        gain = 16.0
        i = 195.6521739 / 1000000.0
        ptcs = ((v_ref * (counts / 2.0 ** 24)) / i) / gain
        msg = "%.7f" % ptcs
    elif "Potentiometer" == input_type:
        potentiometer = 1000.0 * (counts / 2.0 ** 24)
        msg = "%.7f" % potentiometer
    else:
        msg = "Unknown (%s)" % input_type
    return msg


def get_counts_from_converted_value(input_type, value):
    """
    These formulas were calculated basing on the formulas from get_converted_volt_input_type
    Source formulas were to find the value basing on counts, these are opposite,
    to find counts basing on the value
    """
    value = float(value)
    if "Voltage" == input_type:
        v_ref = 4.5
        at = -5.0
        counts = (value / at + (v_ref / 2)) / (v_ref / 2.0 ** 24)
    elif "Gauge" == input_type:
        adc_gain = 128.0
        counts = (value / 1000.0 * adc_gain + 1.0) * (2.0 ** 23)
    elif "Thermistor" == input_type:
        r_offset = 2020.0
        r_f = 1000.0
        r_b = 10000.0
        r_a = r_f + r_b
        counts = ((2.0 ** 24) * (value + r_offset)) / (r_a + value + r_offset)
    elif "Current" == input_type:
        v_ref = 4.5
        r = 200.0
        counts = ((value / 1000.0 * r) / v_ref) * (2.0 ** 24)
    elif "PTC" == input_type:
        v_ref = 4.5
        gain = 16.0
        i = 195.6521739 / 1000000.0
        counts = ((value * gain * i) / v_ref) * (2.0 ** 24)
    elif "Potentiometer" == input_type:
        counts = value / 1000.0 * (2.0 ** 24)
    else:
        counts = 0
    return int(round(counts))  # round and int to find the closest integer


input_type_definition = {
    0: "Voltage",
    1: "Gauge",
    2: "Thermistor",
    3: "Current",
    4: "PTC",
    5: "Potentiometer",
}


def get_volt_input_type_str(input_type):
    return input_type_definition.get(input_type) or "Unknown (%u)" % input_type


def get_volt_input_type_number(input_type):
    return next(
        (
            type_num
            for type_num, type_str in input_type_definition.items()
            if type_str == input_type
        ),
        None,
    )
