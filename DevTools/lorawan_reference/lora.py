#!/usr/bin/env python3

import math
from enum import Enum

import bitstring
from Crypto.Cipher import AES  # uses pycryptodome

from .AES_CMAC import AesCmac


class KeyType(Enum):
    FWD_NETKEY = 1  # Forward Network Session Integrity Key (v1.1)
    SES_APPKEY = 2  # Application Session Encryption Key
    SVC_NETKEY = 3  # Serving Network Session Integrity Key (v1.1)
    SES_NETKEY = 4  # Network Session Encryption Key
    ENC_JSKEY = 5  # Join Encryption Key (v1.1)
    INT_JSKEY = 6  # Join Integrity Key (v1.1)


class FrameType(Enum):
    JOIN_REQ = 0
    JOIN_ACCEPT = 1
    UNCONFIRMED_DATA_UP = 2
    UNCONFIRMED_DATA_DOWN = 3
    CONFIRMED_DATA_UP = 4
    CONFIRMED_DATA_DOWN = 5


def frame2str(frame):
    return ", ".join(["0x{:02X}".format(e) for e in frame])


def build_uplink_frame(akey, nkey, dev_addr, seqno, port, data):
    frame_ctrl = 0
    fbuffer = bitstring.pack(
        "uint:3, pad:5, uintle:32, uintle:8, uintle:16",
        FrameType.UNCONFIRMED_DATA_UP.value,
        dev_addr,
        frame_ctrl,
        (seqno & 0xFFFF),
    ).unpack("8*uint:8")
    fbuffer += [port]
    fbuffer += encrypt_data_payload(akey if port > 0 else nkey, dev_addr, seqno, data)
    fbuffer += compute_data_mic(nkey, dev_addr, seqno, fbuffer)
    return fbuffer


def build_downlink_frame(akey, nkey, dev_addr, seqno, fopts, port, data):
    frame_ctrl = 0 + len(fopts)
    fbuffer = bitstring.pack(
        "uint:3, pad:5, uintle:32, uintle:8, uintle:16",
        FrameType.UNCONFIRMED_DATA_DOWN.value,
        dev_addr,
        frame_ctrl,
        (seqno & 0xFFFF),
    ).unpack("8*uint:8")

    fbuffer += fopts
    if data:
        fbuffer += [port]
        fbuffer += encrypt_data_payload(akey if port > 0 else nkey, dev_addr, seqno, data)

    fbuffer += compute_data_mic(nkey, dev_addr, seqno, fbuffer, uplink=False)
    return fbuffer


def encrypt_data_payload(key, dev_addr, seqno, data, uplink=True):
    k = int(math.ceil(len(data) / 16.0))
    direction = 0 if uplink else 1
    a = []
    for i in range(k):
        a += [0x01]
        a += [0x00] * 4
        a += [direction]
        a += bitstring.pack("uintle:32", dev_addr).unpack("4*uint:8")
        a += bitstring.pack("uintle:32", seqno).unpack("4*uint:8")
        a += [0x00]
        a += [i + 1]
    cipher = AES.new(bytes(key), AES.MODE_ECB)
    s = cipher.encrypt(bytes(a))
    padded_payload = []
    for i in range(k):
        idx = (i + 1) * 16
        padded_payload += (data[idx - 16 : idx] + ([0x00] * 16))[:16]
    payload = []
    for i in range(len(data)):
        payload += [s[i] ^ padded_payload[i]]
    return list(map(int, payload))


def compute_data_mic(key, dev_addr, seqno, data, uplink=True):
    direction = 0 if uplink else 1
    mic = [0x49]
    mic += [0x00] * 4
    mic += [direction]
    mic += bitstring.pack("uintle:32", dev_addr).unpack("4*uint:8")
    mic += bitstring.pack("uintle:32", seqno).unpack("4*uint:8")
    mic += [0x00]
    mic += [len(data)]
    mic += data
    return compute_mic(key, mic)


def build_join_response(
    key, join_nonce, net_id, dev_addr, rx1d_offset, rx2_dr, rx_delay, cf_list=None
):
    # MHDR : 001 | 000 | 00
    fbuffer = bitstring.pack(
        "uint:3, pad:5, uintle:24, uintle:24, uintle:32, pad:1, uint:3, uint:4, uint:8",
        FrameType.JOIN_ACCEPT.value,
        join_nonce,
        net_id,
        dev_addr,
        rx1d_offset,
        rx2_dr,
        rx_delay,
    ).unpack("13*uint:8")
    # CFList
    if (isinstance(cf_list, dict)) and ("type" in cf_list):
        if 0 == cf_list["type"]:
            fbuffer += bitstring.pack(
                "5*uintle:24, uint:8", *[int(e / 100) for e in cf_list["ch"]], cf_list["type"]
            ).unpack("16*uint:8")
        elif 1 == cf_list["type"]:
            fbuffer += bitstring.pack(
                "5*uintle:16, pad:16, pad:24, uint:8",
                *[int(e) for e in cf_list["mask"]],
                cf_list["type"]
            ).unpack("16*uint:8")
    # MIC
    fbuffer += compute_mic(key, fbuffer)
    return fbuffer[:1] + encrypt_join_payload(key, fbuffer[1:])


def build_join_request(key, join_eui, dev_eui, dev_nonce):
    if isinstance(join_eui, list):
        join_eui = bitstring.pack("8*uint:8", *join_eui).unpack("uintle:64")[0]
    if isinstance(dev_eui, list):
        dev_eui = bitstring.pack("8*uint:8", *dev_eui).unpack("uintle:64")[0]
    fbuffer = bitstring.pack(
        "uint:3, pad:5, uintle:64, uintle:64, uintle:16",
        FrameType.JOIN_REQ.value,
        join_eui,
        dev_eui,
        dev_nonce,
    ).unpack("19*uint:8")
    # MIC
    fbuffer += compute_mic(key, fbuffer)
    return fbuffer


def compute_mic(key, payload):
    cmac = AesCmac()
    computed_mic = cmac.encode(bytes(key), bytes(payload))[:4]
    return list(map(int, computed_mic))


def encrypt_join_payload(key, payload):
    cipher = AES.new(bytes(key), AES.MODE_ECB)
    return list(map(int, cipher.decrypt(bytes(payload))))


def derive_nwskey(key, devnonce, appnonce, netid):
    return derive_key(KeyType.FWD_NETKEY, key, devnonce, appnonce, netid)


def derive_appskey(key, devnonce, appnonce, netid):
    return derive_key(KeyType.SES_APPKEY, key, devnonce, appnonce, netid)


def derive_key(key_id, key, devnonce, appnonce, netid):
    a = [key_id.value]
    a += bitstring.pack("uintle:24", appnonce).unpack("3*uint:8")
    a += bitstring.pack("uintle:24", netid).unpack("3*uint:8")
    a += bitstring.pack("uintle:16", devnonce).unpack("2*uint:8")
    a += [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    cipher = AES.new(bytes(key), AES.MODE_ECB)
    return list(map(int, cipher.encrypt(bytes(a))))
