import bitstring
from bitstring import BitArray

MULTIPART_SET_CONFIG_AMTYPE = 194
MSG_VERSION = 0
PART_NUMBER = 0
TOTAL_PARTS = 0
NUMBER_OF_CONFIGS = 0
RFU = 0


def convert_to_remote_config(output, token):
    configuration_array = BitArray()
    configuration_array.append(bitstring.pack("uint:8", (MULTIPART_SET_CONFIG_AMTYPE)))
    configuration_array.append(bitstring.pack("uint:3", (MSG_VERSION)))
    configuration_array.append(bitstring.pack("uint:4", (PART_NUMBER)))
    configuration_array.append(bitstring.pack("uint:4", (TOTAL_PARTS)))
    configuration_array.append(bitstring.pack("uint:3", (NUMBER_OF_CONFIGS)))
    configuration_array.append(bitstring.pack("uint:8", (token)))
    configuration_array.append(bitstring.pack("uint:2", (RFU)))
    configuration_array.append(bitstring.pack("uint:16", (len(output) / 4)))

    remote_output = "".join(["%0.2X" % ord(e) for e in configuration_array.tobytes()])
    remote_output = "\\x" + "\\x".join(
        a + b for a, b in zip(remote_output[::2], remote_output[1::2])
    )
    remote_output += output

    return remote_output


def convert_to_remote_config_python3(output, token):
    configuration_array = BitArray()
    configuration_array.append(bitstring.pack("uint:8", (MULTIPART_SET_CONFIG_AMTYPE)))
    configuration_array.append(bitstring.pack("uint:3", (MSG_VERSION)))
    configuration_array.append(bitstring.pack("uint:4", (PART_NUMBER)))
    configuration_array.append(bitstring.pack("uint:4", (TOTAL_PARTS)))
    configuration_array.append(bitstring.pack("uint:3", (NUMBER_OF_CONFIGS)))
    configuration_array.append(bitstring.pack("uint:8", (token)))
    configuration_array.append(bitstring.pack("uint:2", (RFU)))
    configuration_array.append(bitstring.pack("uint:16", (len(output) / 2)))

    remote_output = bytes.hex(configuration_array.tobytes())
    remote_output += output

    return remote_output
