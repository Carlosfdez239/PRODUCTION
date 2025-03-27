import datetime
import random
import sys
from datetime import timedelta, tzinfo
from pprint import pprint

import bitstring

"""
26:uint32_t Stream_PutBits(uint8_t *p_buf, uint16_t  buf_size, uint16_t bit_offset, uint32_t v, uint8_t  num_bits);
27:uint32_t Stream_PutBits64(uint8_t *p_buf, uint16_t  buf_size, uint16_t bit_offset, uint64_t v, uint8_t  num_bits);
31:uint32_t Stream_PutBitsFromBuffer(uint8_t *p_buf_out, WS_UNUSED uint16_t buf_out_size, uint16_t bit_offset_out,
42:WS_STATIC_INLINE uint32_t Stream_PutFloat(uint8_t *p_buf, float v) {
61:WS_STATIC_INLINE uint32_t Stream_PutUint32(uint8_t *p_buf, uint32_t v) {
77:WS_STATIC_INLINE uint32_t Stream_PutInt32(uint8_t *p_buf, int32_t v) {
93:WS_STATIC_INLINE uint32_t Stream_PutUint24(uint8_t *p_buf, uint32_t v) {
108:WS_STATIC_INLINE uint32_t Stream_PutInt24(uint8_t *p_buf, int32_t v) {
123:WS_STATIC_INLINE uint32_t Stream_PutUint16(uint8_t *p_buf, uint16_t v) {
138:WS_STATIC_INLINE uint32_t Stream_PutInt16(uint8_t *p_buf, int16_t v) {
152:WS_STATIC_INLINE uint32_t Stream_PutUint8(uint8_t *p_buf, uint8_t v) {
165:WS_STATIC_INLINE uint32_t Stream_PutInt8(uint8_t *p_buf, int8_t v) {
179:WS_STATIC_INLINE uint32_t Stream_PutFloatLE(uint8_t *p_buf, float v) {
197:WS_STATIC_INLINE uint32_t Stream_PutUint32LE(uint8_t *p_buf, uint32_t v) {
213:WS_STATIC_INLINE uint32_t Stream_PutInt32LE(uint8_t *p_buf, int32_t v) {
229:WS_STATIC_INLINE uint32_t Stream_PutUint24LE(uint8_t *p_buf, uint32_t v) {
244:WS_STATIC_INLINE uint32_t Stream_PutInt24LE(uint8_t *p_buf, int32_t v) {
259:WS_STATIC_INLINE uint32_t Stream_PutUint16LE(uint8_t *p_buf, uint16_t v) {
274:WS_STATIC_INLINE uint32_t Stream_PutInt16LE(uint8_t *p_buf, int16_t v) {
426:WS_STATIC_INLINE uint32_t Stream_PutNBytes(uint8_t *p_buf, const uint8_t *p_inbuf, uint32_t n) {


auto : Either a specially formatted string, a list or tuple, a file object, integer, bytearray, array, bytes
    or another bitstring.
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
filename : Directly from a file, without reading into memory if using Bits or ConstBitStream.

"""


C_functions = {
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
    "uint:1": "uint8_t",
    "uint:3": "uint8_t",
    "uint:4": "uint8_t",
    "uint:7": "uint8_t",
    "uint:8": "uint8_t",
    "uint:15": "uint16_t",
    "uint:16": "uint16_t",
    "uint:32": "uint32_t",
    "int:8": "int8_t",
    "int:16": "int16_t",
    "int:32": "int32_t",
}

C_random = {
    "uint:1": random.randint(0, 1),
    "uint:3": random.randint(0, 7),
    "uint:4": random.randint(0, 15),
    "uint:7": random.randint(0, 127),
    "uint:8": random.randint(0, 255),
    "uint:15": random.randint(0, 32767),
    "uint:16": random.randint(0, 65535),
    "uint:32": random.randint(0, 4294967295),
    "int:8": random.randint(-127, 128),
    "int:16": random.randint(-32767, 32767),
    "int:32": random.randint(-2147483647, 2147483647),
}

"""
 "h_version": {"pos": 1, "value": h_version, "bits": 4, "type": "uint"},
 "h_id_high": {"pos": 2, "value": h_id_high, "bits": 4, "type": "uint"},
 "h_pr_code": {"pos": 3, "value": h_pr_code, "bits": 8, "type": "uint"},
 "h_id_low": {"pos": 4, "value": h_id_low, "bits": 16, "type": "uint"},
         "h_seq_num": {
             "pos": 5,
             "value": h_seq_num,
             "bits": 8,
             "type": "uint",
         },
         "am_type": {"pos": 6, "value": am_type, "bits": 8, "type": "uint"},
         "timestamp": {"pos": 7, "value": timestamp, "bits": 32, "type": "uint"},
         "uptime": {"pos": 8, "value": uptime, "bits": 32, "type": "uint"},
         "battery_voltage": {
             "pos": 9,
             "value": battery_voltage,
             "bits": 16,
             "type": "uint",
         },
         "temperature": {"pos": 10, "value": temperature, "bits": 8, "type": "int"},
         "serial_n": {"pos": 11, "value": serial_n, "bits": 16, "type": "uint"},
         "firmw_msb": {"pos": 12, "value": fw_msb, "bits": 8, "type": "uint"},
         "firmw_lsb": {"pos": 13, "value": fw_lsb, "bits": 8, "type": "uint"},
         "delta_units": {"pos": 14, "value": delta_units, "bits": 1, "type": "uint"},
         "delta": {"pos": 15, "value": delta, "bits": 15, "type": "uint"},
"""


class SimpleUTC(tzinfo):
    def tzname(self, **kwargs):
        return "UTC"

    def utcoffset(self, dt):
        return timedelta(0)

    def dst(self, dt):
        return timedelta(0)


def second_to_time_iso8601(timestamp):
    d = datetime.datetime.fromtimestamp(0, SimpleUTC()) + datetime.timedelta(seconds=timestamp)
    isof = d.isoformat()
    return isof[:-6] + "Z"


def encode_time_iso8601_to_seconds(time_iso8601):
    utc_dt = datetime.datetime.strptime(time_iso8601, "%Y-%m-%dT%H:%M:%SZ")
    timestamp = (utc_dt - datetime.datetime(1970, 1, 1)).total_seconds()
    return int(timestamp)


def encode_firmware_version(decoded_firmware_version):
    # type: (str) -> tuple[int, int]
    firmware_version_split = decoded_firmware_version.split(".")

    return int(firmware_version_split[0]), int(firmware_version_split[1])


header = [
    {"t": "uint:4", "n": "h_version"},
    {"t": "uint:4", "n": "h_id_high"},
    {"t": "uint:8", "n": "h_pr_code"},
    {"t": "uint:16", "n": "h_id_low"},
    {"t": "uint:8", "n": "h_seq_num"},
]
health = [
    *header,
    {"t": "uint:8", "n": "am_type"},
    {
        "t": "uint:32",
        "n": "timestamp",
        "dec": lambda v: second_to_time_iso8601(v),
        "enc": lambda v: encode_time_iso8601_to_seconds(v),
        "alias": "readTimestamp",
    },
    {"t": "uint:32", "n": "uptime", "alias": "uptimeSeconds"},
    {
        "t": "uint:16",
        "n": "battery_voltage",
        "dec": lambda v: v / 1000,
        "enc": lambda v: v * 1000,
        "alias": "inputPowerVolts",
    },
    {"t": "int:8", "n": "temperature", "alias": "temperatureDegrees"},
    {"t": "uint:16", "n": "serial_n"},
    {"t": "uint:8", "n": "firmw_msb"},
    {"t": "uint:8", "n": "firmw_lsb"},
    {"t": "uint:1", "n": "delta_units"},
    {"t": "uint:15", "n": "delta"},
]


def enc_node_id(n, d):
    d.update({"h_id_high": (d[n] >> 16) & 0xF, "h_id_low": d[n] & 0xFF})
    del d[n]


def dec_node_id(n, d):
    d.update({n: d["h_id_high"] << 16 | d["h_id_low"]})
    del d["h_id_high"]
    del d["h_id_low"]


def enc_firmware_version(n, d):
    d.update({"firmw_msb": d[n].split(".")[0], "firmw_lsb": d[n].split(".")[1]})
    del d[n]


def dec_firmware_version(n, d):
    d.update({n: "%d.%d" % (d["firmw_msb"], d["firmw_lsb"])}),
    del d["firmw_lsb"]
    del d["firmw_msb"]


health_transfroms = [
    {
        "n": "nodeId",
        "dec": dec_node_id,
        "enc": enc_node_id,
    },
    {
        "n": "firmwareVersion",
        "dec": dec_firmware_version,
        "enc": enc_firmware_version,
    },
]


def generate_c_code(code):
    print(code)


def ammsg_to_c_code(msg_def):
    print("---------------- c code -----------------")
    bits_offset = 0
    total_bits = 0
    byte_count = 0
    # Generate variables to fill
    h = {
        "am_type": 70,
        "battery_voltage": 4500,
        "delta": 32767,
        "delta_units": 0,
        "firmw_lsb": 2,
        "firmw_msb": 1,
        "h_pr_code": 2,
        "h_seq_num": 1,
        "h_version": 4,
        "h_id_low": 5,
        "h_id_high": 0,
        "serial_n": 2,
        "temperature": 25,
        "timestamp": 540475440,
        "uptime": 5000,
    }

    for f in msg_def:
        generate_c_code("%s %s = %s;" % (C_types[f["t"]], f["n"], h[f["n"]]))
    generate_c_code("\n")
    for f in msg_def:
        generate_c_code(C_functions[f["t"]] % f["n"])

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
    print("---------------- end c code -----------------")
    bits_counted = byte_count * 8
    if bits_counted != total_bits:
        print(
            "ERROR message bits are not aligned correctly total_bits = %d bits_counted %d !!!!"
            % (total_bits, bits_counted)
        )
        sys.exit(1)


def ammsg_to_dict(msg_def, msg_transforms, data):
    stream = bitstring.ConstBitStream(bytes=data)
    d = {}
    for f in msg_def:
        v = stream.read(f["t"])
        if "dec" in f:
            v = f["dec"](v)
        n = f["n"]
        if "alias" in f:
            n = f["alias"]
        d.update({n: v})
    for f in msg_transforms:
        if "dec" in f:
            f["dec"](f["n"], d)
    return d


def ammsg_to_stream(msg_def, msg_transforms, d):
    for f in msg_transforms:
        if "enc" in f:
            f["enc"](f["n"], d)
    stream = bitstring.BitStream()
    for f in msg_def:
        n = f["n"]
        if "alias" in f:
            n = f["alias"]
        v = d[n]
        if "enc" in f:
            v = f["enc"](v)
        stream.append(bitstring.pack(f["t"], v))
    return stream


# ammsg_to_c_code(health)
# Version | product code = 2 | node id = 5 | seq number = 1
h_msg = b"\x40\x02\x00\x05\x01"
# timestamp = 540475440, uptime = 5000, battery = 4.5, temperature = 25, fw = 1.2,
# serial = 2
health_data = h_msg + b"\x46\x20\x37\x00\x30\x00\x00\x13\x88\x11\x94\x19\x00\x02\x01\x02\x7F\xFF"


current_health = {
    "type": "healthV2",
    "nodeModel": "LS-G6-VW-5-SA",
    "nodeId": 5,
    "inputPowerVolts": 4.5,
    "readTimestamp": "1987-02-16T12:04:00Z",
    "uptimeSeconds": 5000,
    "temperatureDegrees": 25,
    "firmwareVersion": "1.2",
    "serialNumber": 2,
    "timeDeltaUnits": "seconds",
    "timeDelta": 32767,
}

# health_data = b"\x77\xa7\xcb\x1b\xa7\xa7\x55\x05\xf0\x91\x55\x05\xf0\x91\xcb\x1b\x28\xcb\x1b\xa7\xa7\xe2\x4d"
# health_data = b"\xab\xcd\xef\x12\x00\x06\xaa\xbb\xcc\xdd\x12\x34\x57\x90\x88\x99\x34\x67\x89\x99\x33\xf7\x31"
health_data = (
    b"\x40\x02\x00\x05\x01\x46\x20\x37\x00\x30\x00\x00\x13\x88\x11\x94\x19\x00\x02\x01\x02\x7f\xff"
)
d = ammsg_to_dict(health, health_transfroms, health_data)
pprint(d)
print()
pprint(current_health)
print(bitstring.BitStream(bytes=health_data))
s = ammsg_to_stream(health, health_transfroms, d)
print(s)
