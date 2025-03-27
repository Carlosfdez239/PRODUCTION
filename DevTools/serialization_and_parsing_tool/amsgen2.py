import sys
import typing
from pprint import pprint

import bitstring
from utils import *

"""
auto : Either a specially formatted string, a list or tuple, a file object, integer, bytearray, array, bytes or
        another bitstring.
bytes : A bytes object, for example read from a binary file.
hex, oct, bin: Hexadecimal, octal or binary strings.
int, uint: Signed or unsigned bit-wise big-endian binary integers.
intle, uintle: Signed or unsigned byte-wise little-endian binary integers.
intbe, uintbe: Signed or unsigned byte-wise big-endian binary integers.
intne, uintne: Signed or unsigned byte-wise native-endian binary integers.
float / floatbe, floatle, floatne: Big, little and native endian floating point numbers.
bfloat / bfloatbe, bfloatle, bfloatne: Big, little and native endian 16 bit ‘bfloat’ numbers.
se, ue : Signed or unsigned exponential-Golomb coded integers.
sie, uie : Signed or unsigned interleaved exponential-Golomb coded integers.
bool : A boolean (i.e. True or False).
"""

C_functions_in = {
    "uint:1": "bits_offset += Stream_GetBitsUint32(&p_msg[byte_count], sizeof(p_msg) - byte_count, bits_offset, 1,"
    " &%s);",
    "uint:3": "",
    "uint:4": "",
    "uint:7": "",
    "uint:8": "byte_count += Stream_GetUint8(&p_msg[byte_count], &%s);",
    "uint:15": "bits_offset += Stream_GetBitsUint32(&p_msg[byte_count], sizeof(p_msg) - byte_count, bits_offset, 15,"
    " &%s);",
    "uint:16": "byte_count += Stream_GetUint16(&p_msg[byte_count], &%s);",
    "uint:32": "byte_count += Stream_GetUint32(&p_msg[byte_count], &%s);",
    "int:8": "byte_count += Stream_GetInt8(&p_msg[byte_count], &%s);",
    "int:16": "",
    "int:32": "",
}

C_functions_out = {
    "uint:1": "bits_offset += Stream_PutBits(&p_buf[byte_count], sizeof(p_buf) - byte_count, bits_offset, %s, 1);",
    "uint:3": "bits_offset += Stream_PutBits(&p_buf[byte_count], sizeof(p_buf) - byte_count, bits_offset, %s, 3);",
    "uint:4": "bits_offset += Stream_PutBits(&p_buf[byte_count], sizeof(p_buf) - byte_count, bits_offset, %s, 4);",
    "uint:7": "bits_offset += Stream_PutBits(&p_buf[byte_count], sizeof(p_buf) - byte_count, bits_offset, %s, 7);",
    "uint:8": "byte_count += Stream_PutUint8(&p_buf[byte_count], %s);",
    "uint:15": "bits_offset += Stream_PutBits(&p_buf[byte_count], sizeof(p_buf) - byte_count, bits_offset, %s, 15);",
    "uint:16": "byte_count += Stream_PutUint16(&p_buf[byte_count], %s);",
    "uint:32": "byte_count += Stream_PutUint32(&p_buf[byte_count], %s);",
    "int:8": "byte_count += Stream_PutInt8(&p_buf[byte_count], %s);",
    "int:16": "byte_count += Stream_PutInt16(&p_buf[byte_count], %s);",
    "int:32": "byte_count += Stream_PutInt32(&p_buf[byte_count], %s);",
}

C_types = {
    "uint:1": "uint32_t",
    "uint:3": "uint32_t",
    "uint:4": "uint32_t",
    "uint:7": "uint32_t",
    "uint:8": "uint8_t",
    "uint:15": "uint32_t",
    "uint:16": "uint16_t",
    "uint:32": "uint32_t",
    "int:8": "int8_t",
    "int:16": "int16_t",
    "int:32": "int32_t",
}


"""

- c_struct -> msg -> json
- json     -> msg -> c_struct

typedef struct health_info {
     uint32_t     Uptime;         /**< Uptime of node            */
     float32_t    Temperature;    /**< Temperature of the node   */
     float32_t    BatteryVoltage; /**< Battery of node in mV     */
 } HEALTH_INFO_T;
"""


header_msg = [
    {"t": "uint:4", "n": "h_version"},
    {"t": "uint:4", "n": "h_id_high"},
    {"t": "uint:8", "n": "h_pr_code"},
    {"t": "uint:16", "n": "h_id_low"},
    {"t": "uint:8", "n": "h_seq_num"},
]
"""
#p_data: is the pointer to the struct
#j: is the json dict data
#m: is the msg data

# C struct definition
c_struct     Uptime         uint32_t
c_struct     Temperature    uint32_t
c_struct     BatteryVoltage uint32_t

# Decoders
c_struct_dec Uptime         p_data->Uptime = uptime
c_struct_dec Temperature    p_data->Temperature = (float32_t) temperature
c_struct_dec BatteryVoltage p_data->BatteryVoltage = (float32_t ) battery_voltage * 10.

# Message defintion (order is important here)
msg header          header
msg amtype          uint:8
msg timestamp       uint:32
msg uptime          uint:32
msg battery_voltage uint:16
msg temperature     int:8
msg serial_n        uint:16
msg firmw_msb       uint:8
msg firmw_lsb       uint:8
msg delta_units     uint:1
msg delta           uint:15

# Message encoders decoders
msg_c_enc amtype 70
msg_c_enc battery_voltage (uint16_t ) p_data->BatteryVoltage / 10.
msg_c_enc timestamp       RTCA_GetTimeSec()
msg_c_enc uptime          p_data->Uptime
msg_c_enc battery_voltage (uint16_t ) p_data->BatteryVoltage / 10.
msg_c_enc temperature     p_data->temperature
msg_c_val serial_n        2
msg_c_val firmw_msb       1
msg_c_val firmw_lsb       2
msg_c_val delta_units     0
msg_c_val delta           15000

msg_py_val amtype 70
msg_py_enc timestamp       encode_time_iso8601_to_seconds(j["readTimestamp"])
msg_py_enc uptime          j["uptimeSeconds"]
msg_py_enc battery_voltage int(j["inputPowerVolts"] * 1000)
msg_py_enc temperature     j["temperatureDegrees"]
msg_py_enc serial_n        j["serialNumber"]
msg_py_enc firmw_msb       j["firmwareVersion"].split(".")[0]
msg_py_enc firmw_lsb       j["firmwareVersion"].split(".")[1]
msg_py_enc delta_units     j["timeDeltaUnits"]
msg_py_enc delta           j["timeDelta"]

# JSON definition
json type                   string
json nodeModel              string
json nodeId                 string
json inputPowerVolts        number
json readTimestamp          string
json uptimeSeconds          number
json temperatureDegrees     number
json firmwareVersion        string
json serialNumber           number
json timeDeltaUnits         string
json timeDelta              number

# JSON decoders
json_py_val type               healthV2
json_py_val nodeModel          LS-G6-VW-5-SA
json_py_val nodeId             m["h_id_high"] << 16 | m["h_id_low"]
json_py_dec inputPowerVolts    m["battery_voltage"] / 1000
json_py_dec readTimestamp      second_to_time_iso8601(m["timestamp"])
json_py_dec uptimeSeconds      m["uptime"]
json_py_dec temperatureDegrees m["temperature"]
json_py_dec firmwareVersion    "%d.%d" % (m["firmw_msb"], m["firmw_lsb"])
json_py_dec serialNumber       m["serial_n"],
json_py_dec timeDeltaUnits     ["minutes", "seconds"][m["delta_units"]]
json_py_dec timeDelta          m["delta"]

"""

msgdef = {
    "c_struct": {
        "Uptime": {"t": "uint32_t", "c_dec": "p_data->Uptime = uptime;"},
        "Temperature": {
            "t": "float32_t",
            "c_dec": "p_data->Temperature = (float32_t ) temperature;",
        },
        "BatteryVoltage": {
            "t": "float32_t",
            "c_dec": "p_data->BatteryVoltage = (float32_t ) battery_voltage * 10.;",
        },
    },
    "msg": [
        *header_msg,
        {
            "t": "uint:8",
            "n": "am_type",
            "c_enc": 70,
            "py_enc": 70,
        },
        {
            "t": "uint:32",
            "n": "timestamp",
            "val": {
                "max": 0,
                "min": 10,
                "c_val": "timestamp >= 0 && timestamp <= 10",
                "py_val": lambda m: m["timestamp"] >= 0 and m["timestamp"] <= 10,
            },
            "c_enc": "RTCA_GetTimeSec()",
            "py_enc": lambda j: encode_time_iso8601_to_seconds(j["readTimestamp"]),
        },
        {
            "t": "uint:32",
            "n": "uptime",
            "c_enc": "p_data->Uptime",
            "py_enc": lambda j: j["uptimeSeconds"],
        },
        {
            "t": "uint:16",
            "n": "battery_voltage",
            "c_enc": "(uint16_t ) p_data->BatteryVoltage / 10.",
            "py_enc": lambda j: int(j["inputPowerVolts"] * 1000),
        },
        {
            "t": "int:8",
            "n": "temperature",
            "c_enc": " (uint8_t) p_data->Temperature",
            "py_enc": lambda j: j["temperatureDegrees"],
        },
        {
            "t": "uint:16",
            "n": "serial_n",
            "c_enc": "2",
            "py_enc": lambda j: j["serialNumber"],
        },
        {
            "t": "uint:8",
            "n": "firmw_msb",
            "c_enc": "1",
            "py_enc": lambda j: j["firmwareVersion"].split(".")[0],
        },
        {
            "t": "uint:8",
            "n": "firmw_lsb",
            "py_enc": lambda j: j["firmwareVersion"].split(".")[1],
            "c_enc": "2",
        },
        {
            "t": "uint:1",
            "n": "delta_units",
            "c_enc": "20",
            "py_enc": lambda j: 0 if j["timeDeltaUnits"] == "seconds" else 1,
        },
        {
            "t": "uint:15",
            "n": "delta",
            "c_enc": "50",
            "py_enc": lambda j: j["timeDelta"],
            "bitmask": "serial_n:0x01",
        },
    ],
    "json": {
        "type": {
            "py_dec": "healthV2",
        },
        "nodeModel": {
            "py_dec": "LS-G6-VW-5-SA",
        },
        "nodeId": {
            "py_dec": lambda m: m["h_id_high"] << 16 | m["h_id_low"],
        },
        "inputPowerVolts": {
            "py_dec": lambda m: m["battery_voltage"] / 1000,
        },
        "readTimestamp": {
            "py_dec": lambda m: second_to_time_iso8601(m["timestamp"]),
        },
        "uptimeSeconds": {
            "py_dec": lambda m: m["uptime"],
        },
        "temperatureDegrees": {
            "py_dec": lambda m: m["temperature"],
        },
        "firmwareVersion": {
            "py_dec": lambda m: "%d.%d" % (m["firmw_msb"], m["firmw_lsb"]),
        },
        "serialNumber": {
            "py_dec": lambda m: m["serial_n"],
        },
        "timeDeltaUnits": {
            "py_dec": lambda m: "seconds" if m["delta_units"] == 0 else "minutes",
        },
        "timeDelta": {
            "py_dec": lambda m: m["delta"],
        },
    },
}


def generate_c_code(code):
    print(code)


def amsg_c_struct(msg_def):
    generate_c_code("typedef struct msg_data {")
    for k, d in msg_def["c_struct"].items():
        generate_c_code("    %s %s;" % (d["t"], k))
    generate_c_code("} MSG_DATA_T;")


def ammsg_to_c_code_in(msg_def):
    generate_c_code(
        "int Msg_Decode(const uint8_t *p_msg, uint16_t msg_size, WS_DATA_UNION_T *p_decoded_msg,"
        " uint16_t *p_decoded_size) {"
    )
    generate_c_code(
        """
uint32_t byte_count = 0;
uint16_t bits_offset = 0;
MSG_DATA_T *p_data = malloc(sizeof(MSG_DATA_T));
    """
    )
    bits_offset = 0
    total_bits = 0
    byte_count = 0
    for f in msg_def["msg"][len(header_msg) :]:
        generate_c_code("%s %s;" % (C_types[f["t"]], f["n"]))
    for f in msg_def["msg"][len(header_msg) :]:
        generate_c_code(C_functions_in[f["t"]] % f["n"])
        # Increment byte count and reset bits offset
        bits = int(f["t"].split(":")[1])
        total_bits += bits
        bits_offset += bits
        _bytes = bits_offset / 8
        if bits_offset % 8 == 0 and bits % 8 != 0:
            generate_c_code("bits_offset = 0;")
            generate_c_code("byte_count += %d;" % _bytes)
            bits_offset = 0
            byte_count += _bytes
        elif bits_offset % 8 == 0:
            bits_offset = 0
            byte_count += _bytes

    generate_c_code("WS_ASSERT(%d == byte_count)" % byte_count)
    bits_counted = byte_count * 8
    if bits_counted != total_bits:
        print(
            "ERROR message bits are not aligned correctly total_bits = %d bits_counted %d !!!!"
            % (total_bits, bits_counted)
        )
        sys.exit(1)

    for k, d in msg_def["c_struct"].items():
        generate_c_code(d["c_dec"])
    generate_c_code("p_decoded_msg->Data_Ptr = (void *)p_data;")
    generate_c_code("return 0;")
    generate_c_code("}")


def ammsg_to_c_code_out(msg_def):
    generate_c_code(
        "uint8_t Msg_PayloadSerializeToStream(const void *p, WS_UNUSED uint16_t size, uint8_t *p_buf,"
        " WS_UNUSED uint16_t buf_size) {"
    )
    generate_c_code(
        """
uint32_t byte_count = 0;
uint16_t bits_offset = 0;
MSG_DATA_T *p_data = (MSG_DATA_T *) p;
    """
    )
    bits_offset = 0
    total_bits = 0
    byte_count = 0
    for f in msg_def["msg"][len(header_msg) :]:
        generate_c_code(C_functions_out[f["t"]] % f["c_enc"])
        # Increment byte count and reset bits offset
        bits = int(f["t"].split(":")[1])
        total_bits += bits
        bits_offset += bits
        _bytes = bits_offset / 8
        if bits_offset % 8 == 0 and bits % 8 != 0:
            generate_c_code("bits_offset = 0;")
            generate_c_code("byte_count += %d;" % _bytes)
            bits_offset = 0
            byte_count += _bytes
        elif bits_offset % 8 == 0:
            bits_offset = 0
            byte_count += _bytes

    generate_c_code("WS_ASSERT(%d == byte_count)" % byte_count)
    generate_c_code("return byte_count;")
    generate_c_code("}")
    bits_counted = byte_count * 8
    if bits_counted != total_bits:
        print(
            "ERROR message bits are not aligned correctly total_bits = %d bits_counted %d !!!!"
            % (total_bits, bits_counted)
        )
        sys.exit(1)


def ammsg_to_json(msg_def, data):
    stream = bitstring.ConstBitStream(bytes=data)
    m = {}
    for f in msg_def["msg"]:
        if "bitmask" in f:
            print("--------> has bitmask", f["bitmask"])
            field, mask = f["bitmask"].split(":")
            mask = int(mask, 16)
            print(m[field], mask)
            if m[field] & mask != mask:
                m.update({f["n"]: None})
                continue
        v = stream.read(f["t"])
        m.update({f["n"]: v})
    j = {}
    for k, d in msg_def["json"].items():
        v = d["py_dec"]
        if isinstance(v, typing.Callable):
            v = v(m)
        if v is not None:
            j.update({k: v})
    return j


def ammsg_to_stream(msg_def, j):
    stream = bitstring.BitStream()
    for f in msg_def["msg"][len(header_msg) :]:
        v = f["py_enc"]
        if isinstance(v, typing.Callable):
            v = v(j)
        stream.append(bitstring.pack(f["t"], v))
    return stream


# health_data = b"\x77\xa7\xcb\x1b\xa7\xa7\x55\x05\xf0\x91\x55\x05\xf0\x91\xcb\x1b\x28\xcb\x1b\xa7\xa7\xe2\x4d"
# health_data = b"\xab\xcd\xef\x12\x00\x06\xaa\xbb\xcc\xdd\x12\x34\x57\x90\x88\x99\x34\x67\x89\x99\x33\xf7\x31"
health_data = (
    b"\x40\x02\x00\x05\x01\x46\x20\x37\x00\x30\x00\x00\x13\x88\x11\x94\x19\x00\x02\x01\x02\x7f\xff"
)
health_data = (
    b"\x40\x02\x00\x05\x01\x46\x3b\x9a\xca\x00\x00\x00\x00\x0f\x11\x94\x19\x00\x02\x01\x02\x00\x32"
)
print(
    """
#include <stdio.h>
#include <stdlib.h>
#include "stream.h"
#include "ws_assert.h"

#define N_BUFF 64
uint32_t RTCA_GetTimeSec() {
    return 1000000000;
}
"""
)
amsg_c_struct(msgdef)
print("\n\n")
ammsg_to_c_code_in(msgdef)
print("\n\n")
ammsg_to_c_code_out(msgdef)


print(
    """

int main() {
    uint8_t p_buf[N_BUFF];
    uint8_t byte_count;
    uint16_t decoded_size;
    WS_DATA_UNION_T decoded_msg;
    memset(p_buf, 0, sizeof(p_buf));

    MSG_DATA_T    data;
    MSG_DATA_T *p_data = &data;

    p_data->BatteryVoltage = 45600;
    p_data->Temperature = 25.0;
    p_data->Uptime = 15;

    byte_count = Msg_PayloadSerializeToStream(p_data, sizeof(MSG_DATA_T), p_buf, N_BUFF);

    memset(p_data, 0, sizeof(data));

    for (int i=0; i< byte_count;i++) {
        printf("\\\\x%02x", p_buf[i]);
    }
    printf("\\n");

    Msg_Decode(p_buf, byte_count, &decoded_msg, &decoded_size);

    p_data = (MSG_DATA_T *) decoded_msg.Data_Ptr;

    printf("%d %f %f", p_data->Uptime, p_data->Temperature, p_data->BatteryVoltage);

    return 0;
}
"""
)
j = ammsg_to_json(msgdef, health_data)
pprint(j)
# s = ammsg_to_stream(msgdef, j)
# print(bitstring.BitStream(bytes=health_data))
# print("         ", s)
