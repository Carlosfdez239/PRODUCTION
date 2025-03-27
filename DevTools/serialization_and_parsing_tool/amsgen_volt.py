import sys
import typing
from pprint import pprint

import bitstring
import volt_utils

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
    "uint:24": "byte_count += Stream_GetUint24(&p_msg[byte_count], &%s);",
    "uint:32": "byte_count += Stream_GetUint32(&p_msg[byte_count], &%s);",
    "int:8": "byte_count += Stream_GetInt8(&p_msg[byte_count], &%s);",
    "int:16": "",
    "int:24": "byte_count += Stream_GetInt24(&p_msg[byte_count], &%s);",
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
    "uint:24": "byte_count += Stream_PutUint24(&p_buf[byte_count], %s);",
    "uint:32": "byte_count += Stream_PutUint32(&p_buf[byte_count], %s);",
    "int:8": "byte_count += Stream_PutInt8(&p_buf[byte_count], %s);",
    "int:16": "byte_count += Stream_PutInt16(&p_buf[byte_count], %s);",
    "int:24": "byte_count += Stream_PutInt24(&p_buf[byte_count], %s);",
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
    "uint:24": "uint32_t",
    "uint:32": "uint32_t",
    "int:8": "int8_t",
    "int:16": "int16_t",
    "int:24": "int32_t",
    "int:32": "int32_t",
}


header_msg = [
    {"t": "uint:4", "n": "h_version"},
    {"t": "uint:4", "n": "h_id_high"},
    {"t": "uint:8", "n": "h_pr_code"},
    {"t": "uint:16", "n": "h_id_low"},
    {"t": "uint:8", "n": "h_seq_num"},
]

"""
- c_struct -> msg -> json
- json     -> msg -> c_struct
 VINT_NUM_CHANNELS = 4

 typedef struct {
     uint8_t              InputType;
     VADC_SAMPLE_COUNTS_T Reading;              /* All readings stored in counts. Conversions performed outside (SW) */
 } VOLT_CHANNEL_READING_T;

 typedef struct {
     uint8_t                ChEnBitmap;
     VOLT_CHANNEL_READING_T Channels[VINT_NUM_CHANNELS];
 } VOLT_DATA_T;
 new struct
 typedef struct {
     uint8_t                ChEnBitmap;
     uint8_t                InputType1;
     uint32_t               Reading1;
     uint8_t                InputType2;
     uint32_t               Reading2;
     uint8_t                InputType3;
     uint32_t               Reading3;
     uint8_t                InputType4;
     uint32_t               Reading4;
 } VOLT_DATA_T;

"""

msgdef = {
    "c_struct": {
        "timestamp": {"t": "uint32_t", "c_dec": "p_data->timestamp = timestamp;"},
        "ChEnBitmap": {"t": "uint8_t", "c_dec": "p_data->ChEnBitmap = ch_en_bitmap;"},
        "InputType1": {"t": "uint8_t", "c_dec": "p_data->InputType1 = ch1_input_type;"},
        "Reading1": {"t": "uint32_t", "c_dec": "p_data->Reading1 = ch1_reading;"},
        "InputType2": {"t": "uint8_t", "c_dec": "p_data->InputType2 = ch2_input_type;"},
        "Reading2": {"t": "uint32_t", "c_dec": "p_data->Reading2 = ch2_reading;"},
        "InputType3": {"t": "uint8_t", "c_dec": "p_data->InputType3 = ch3_input_type;"},
        "Reading3": {"t": "uint32_t", "c_dec": "p_data->Reading3 = ch3_reading;"},
        "InputType4": {"t": "uint8_t", "c_dec": "p_data->InputType4 = ch4_input_type;"},
        "Reading4": {"t": "uint32_t", "c_dec": "p_data->Reading4 = ch4_reading;"},
    },
    "msg": [
        *header_msg,
        {
            "t": "uint:8",
            "n": "am_type",
            "c_enc": 0x43,
            "py_enc": 0x43,
        },
        {
            "t": "uint:32",
            "n": "timestamp",
            "c_enc": "p_data->timestamp",
            "py_enc": lambda j: j["timestamp"],
        },
        {
            "t": "uint:8",
            "n": "ch_en_bitmap",
            "c_enc": "p_data->ChEnBitmap",
            "py_enc": lambda j: j["readings"],
        },
        {
            "t": "uint:8",
            "n": "ch1_input_type",
            "c_enc": "p_data->InputType1",
            "bitmask": "ch_en_bitmap:0x01",
        },
        {
            "t": "uint:24",
            "n": "ch1_reading",
            "c_enc": "p_data->Reading1",
            "bitmask": "ch_en_bitmap:0x01",
        },
        {
            "t": "uint:8",
            "n": "ch2_input_type",
            "c_enc": "p_data->InputType2",
            "bitmask": "ch_en_bitmap:0x02",
        },
        {
            "t": "uint:24",
            "n": "ch2_reading",
            "c_enc": "p_data->Reading2",
            "bitmask": "ch_en_bitmap:0x02",
        },
        {
            "t": "uint:8",
            "n": "ch3_input_type",
            "c_enc": "p_data->InputType3",
            "bitmask": "ch_en_bitmap:0x04",
        },
        {
            "t": "uint:24",
            "n": "ch3_reading",
            "c_enc": "p_data->Reading3",
            "bitmask": "ch_en_bitmap:0x04",
        },
        {
            "t": "uint:8",
            "n": "ch4_input_type",
            "c_enc": "p_data->InputType4",
            "bitmask": "ch_en_bitmap:0x08",
        },
        {
            "t": "uint:24",
            "n": "ch4_reading",
            "c_enc": "p_data->Reading4",
            "bitmask": "ch_en_bitmap:0x08",
        },
    ],
    "json": {
        "type": {
            "py_dec": "voltageReadingsV1",
        },
        "nodeModel": {
            "py_dec": "LS-G6-VOLT-4-FCC",
        },
        "nodeId": {
            "py_dec": lambda m: m["h_id_high"] << 16 | m["h_id_low"],
        },
        "ch1_input_type": {
            "py_dec": lambda m: m["ch1_input_type"]
            and volt_utils.get_volt_input_type_str(m["ch1_input_type"])
        },
        "ch1_reading": {
            "py_dec": lambda m: m["ch1_input_type"]
            and volt_utils.get_converted_volt_input_type(
                volt_utils.get_volt_input_type_str(m["ch1_input_type"]), m["ch1_reading"]
            )
        },
        "ch2_input_type": {
            "py_dec": lambda m: m["ch2_input_type"]
            and volt_utils.get_volt_input_type_str(m["ch2_input_type"])
        },
        "ch2_reading": {
            "py_dec": lambda m: m["ch2_input_type"]
            and volt_utils.get_converted_volt_input_type(
                volt_utils.get_volt_input_type_str(m["ch2_input_type"]), m["ch2_reading"]
            )
        },
        "ch3_input_type": {
            "py_dec": lambda m: m["ch3_input_type"]
            and volt_utils.get_volt_input_type_str(m["ch3_input_type"])
        },
        "ch3_reading": {
            "py_dec": lambda m: m["ch3_input_type"]
            and volt_utils.get_converted_volt_input_type(
                volt_utils.get_volt_input_type_str(m["ch3_input_type"]), m["ch3_reading"]
            )
        },
        "ch4_input_type": {
            "py_dec": lambda m: m["ch4_input_type"]
            and volt_utils.get_volt_input_type_str(m["ch4_input_type"])
        },
        "ch4_reading": {
            "py_dec": lambda m: m["ch4_input_type"]
            and volt_utils.get_converted_volt_input_type(
                volt_utils.get_volt_input_type_str(m["ch4_input_type"]), m["ch4_reading"]
            )
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
        bitmask = True if "bitmask" in f else False
        if bitmask:
            field, mask = f["bitmask"].split(":")
            generate_c_code("if ( %s & %s) {" % (field, mask))
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
        if bitmask:
            generate_c_code("}")

    # TODO based onbitmask generate_c_code("WS_ASSERT(%d == byte_count)" % byte_count)
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
    bitmasks = {}
    for f in msg_def["msg"][len(header_msg) :]:
        bitmask = True if "bitmask" in f else False
        if bitmask:
            field, mask = f["bitmask"].split(":")
            bitmasks.update({field: True})

    for f in msg_def["msg"][len(header_msg) :]:
        if f["n"] in bitmasks:
            generate_c_code("%s %s = %s;" % (C_types[f["t"]], f["n"], f["c_enc"]))
    for f in msg_def["msg"][len(header_msg) :]:
        bitmask = True if "bitmask" in f else False
        if bitmask:
            field, mask = f["bitmask"].split(":")
            generate_c_code("if ( %s & %s) {" % (field, mask))
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
        if bitmask:
            generate_c_code("}")

    # TODO based on bitmask generate_c_code("WS_ASSERT(%d == byte_count)" % byte_count)
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
            field, mask = f["bitmask"].split(":")
            mask = int(mask, 16)
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

    p_data->ChEnBitmap = 0xF;
    p_data->InputType1 = 1;
    p_data->Reading1 = 2;
    p_data->InputType2 = 3;
    p_data->Reading2 = 4;
    p_data->InputType3 = 5;
    p_data->Reading3 = 6;
    p_data->InputType4 = 7;
    p_data->Reading4 = 8;

    byte_count = Msg_PayloadSerializeToStream(p_data, sizeof(MSG_DATA_T), p_buf, N_BUFF);

    memset(p_data, 0, sizeof(data));

    for (int i=0; i< byte_count;i++) {
        printf("\\\\x%02x", p_buf[i]);
    }
    printf("\\n");

    Msg_Decode(p_buf, byte_count, &decoded_msg, &decoded_size);

    p_data = (MSG_DATA_T *) decoded_msg.Data_Ptr;

    printf("%d %d %d %d %d %d %d %d %d",
     p_data->ChEnBitmap,
     p_data->InputType1,
     p_data->Reading1,
     p_data->InputType2,
     p_data->Reading2,
     p_data->InputType3,
     p_data->Reading3,
     p_data->InputType4,
     p_data->Reading4);


    return 0;
}
"""
)
# timestamp = 540475440, channels = 4
#   ch0 counts        0 -> -7.8125 mV/V
#   ch1 counts     4095 -> -7.80868623406 mV/V
#   ch2 counts   262143 -> -7.56836030632 mV/V
#   ch3 counts 16777215 -> 7.81249906868  mV/V

msg = b"\x40\x48\x00\xab\x00\x43\x20\x37\x00\x30\x0F\x01\x00\x00\x00\x01\x00\x0F\xFF\x01\x03\xFF\xFF\x01\xFF\xFF\xFF"
# msg = b"\x40\x48\x00\xab\x00\x43\x20\x37\x00\x30\x07\x01\x00\x00\x00\x01\x00\x0F\xFF\x01\x03\xFF\xFF"
# msg = b"\x40\x48\x00\xab\x00\x43\x20\x37\x00\x30\x03\x01\x00\x00\x00\x01\x00\x0F\xFF"
# msg = b"\x40\x48\x00\xab\x00\x43\x20\x37\x00\x30\x0e\x01\x00\x0F\xFF\x01\x03\xFF\xFF\x01\xFF\xFF\xFF"

j = ammsg_to_json(msgdef, msg)
pprint(j)
# s = ammsg_to_stream(msgdef, j)
# print(bitstring.BitStream(bytes=health_data))
# print("         ", s)
