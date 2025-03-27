#!/usr/bin/env python3

import numpy as np

"""
This program just calculates the parameters for the direct form 1 normalized biquad filter.

This is based on the following paper:
    Rimell, A.N. and Mansfield, N.J., 2007. Design of digital filters for frequency weightings
    required for risk assessments of workers exposed to vibration. Industrial Health, 45(4), pp.512-519.

The filter parameters depend on the sampling rate. This file helps to calculate the filter parameters
for the specified sampling frequency.
"""

SAMPLING_FREQUENCY = 1000  # Specify the sampling frequency.
POS_SHIFT = 0  # This is the scale factor that should be applied to the filtered coeficients.
SCALE_FACTOR = 2 ** POS_SHIFT


def float_to_q31(param):
    ret = []
    for val in param:
        ret.append(int(round(val * 2147483648)))

    return ret


# parameters for the Wn filter:
f1 = 0.7 * 10 ** -0.1
q1 = 0.5
f2 = 1.15 * 100
q2 = 0.65
f3 = 1 / (0.028 * 2 * np.pi)
f4 = 1 / (0.028 * 2 * np.pi)
q4 = 1 / 2
f5 = 0
q5 = 0
f6 = 0
q6 = 0

# normalized centre frequencies
w1_n = 2 * np.pi * (f1 / SAMPLING_FREQUENCY)
w2_n = 2 * np.pi * (f2 / SAMPLING_FREQUENCY)
w3_n = 2 * np.pi * (f3 / SAMPLING_FREQUENCY)
w4_n = 2 * np.pi * (f4 / SAMPLING_FREQUENCY)
w5_n = 2 * np.pi * (f5 / SAMPLING_FREQUENCY)
w6_n = 2 * np.pi * (f6 / SAMPLING_FREQUENCY)

# wrapped frequencies
w1 = 2 * np.tan(w1_n / 2)
w2 = 2 * np.tan(w2_n / 2)
w3 = 2 * np.tan(w3_n / 2)
w4 = 2 * np.tan(w4_n / 2)
w5 = 2 * np.tan(w5_n / 2)
w6 = 2 * np.tan(w6_n / 2)

# High-pass filter b0, b1, b2, a1, a2
a0 = 4 * q1 + 2 * w1 + w1 ** 2
a1 = 2 * (w1 ** 2) - 8 * q1
a2 = 4 * q1 - 2 * w1 + w1 ** 2
b0 = 4 * q1
b1 = -8 * q1
b2 = 4 * q1
print(f"High pass: num = {[b0, b1, b2]}   den = {[a0, a1, a2]}")
a0 = a0 * SCALE_FACTOR
float_h_h = [b0 / a0, b1 / a0, b2 / a0, -a1 / a0, -a2 / a0]
h_h = float_to_q31(float_h_h)

# Low-pass filter b0, b1, b2, a1, a2
a0 = 4 * q2 + 2 * w2 + (w2 ** 2) * q2
a1 = 2 * (w2 ** 2) * q2 - 8 * q2
a2 = 4 * q2 - 2 * w2 + (w2 ** 2) * q2
b0 = (w2 ** 2) * q2
b1 = 2 * (w2 ** 2) * q2
b2 = (w2 ** 2) * q2
print(f"low pass: num = {[b0, b1, b2]}   den = {[a0, a1, a2]}")
a0 = a0 * SCALE_FACTOR
float_h_l = [b0 / a0, b1 / a0, b2 / a0, -a1 / a0, -a2 / a0]
h_l = float_to_q31(float_h_l)

# Acceleration-velocity transform filter b0, b1, b2, a1, a2
a0 = 4 * q4 + 2 * w4 + (w4 ** 2) * q4
a1 = 2 * (w4 ** 2) * q4 - 8 * q4
a2 = 4 * q4 - 2 * w4 + (w4 ** 2) * q4
b0 = (w4 ** 2) * q4 + 2 * ((q4 * (w4 ** 2)) / w3)
b1 = 2 * (w4 ** 2) * q4
b2 = (w4 ** 2) * q4 - 2 * ((q4 * (w4 ** 2)) / w3)
print(f"acceleration velocity: num = {[b0, b1, b2]}   den = {[a0, a1, a2]}")
a0 = a0 * SCALE_FACTOR
float_h_t = [b0 / a0, b1 / a0, b2 / a0, -a1 / a0, -a2 / a0]
h_t = float_to_q31(float_h_t)

# Upward step filter b0, b1, b2, a1, a2
"""
a0 =
a1 =
a2 =
b0 =
b1 =
b2 =
"""
float_h_s = [1, 0, 0, 0, 0]
print(f"low pass: num = {[1, 0, 0]}   den = {[1, 0, 0]}")
for index in range(len(float_h_s)):
    float_h_s[index] = float_h_s[index] / SCALE_FACTOR
h_s = float_to_q31(float_h_s)

print("\n\n----- Float values -----")
print(f"High-pass filter: {float_h_h}")
print(f"Low-pass filter: {float_h_l}")
print(f"Acceleration-velocity transform: {float_h_t}")
print(f"Upward step filter: {float_h_s}")
print(f"post shift = {POS_SHIFT}")
print("\n\n----- Fixed point values -----")
print(f"High-pass filter: {h_h}")
print(f"Low-pass filter: {h_l}")
print(f"Acceleration-velocity transform: {h_t}")
print(f"Upward step filter: {h_s}")
print(f"post shift = {POS_SHIFT}")

print("-------------------")
print("-------------------")
print("-------------------")
print("-------------------")

# parameters for the Wn filter:
f1 = 10 ** -0.1
q1 = 1 / np.sqrt(2, dtype=np.float16)
f2 = 100
q2 = 1 / np.sqrt(2, dtype=np.float16)
f3 = 1 / (0.028 * 2 * np.pi)
f4 = 1 / (0.028 * 2 * np.pi)
q4 = 1 / 2
f5 = 0
q5 = 0
f6 = 0
q6 = 0

# normalized centre frequencies
w1_n = np.array([2 * np.pi * (f1 / SAMPLING_FREQUENCY)], dtype=np.float16)[0]
w2_n = np.array([2 * np.pi * (f2 / SAMPLING_FREQUENCY)], dtype=np.float16)[0]
w3_n = np.array([2 * np.pi * (f3 / SAMPLING_FREQUENCY)], dtype=np.float16)[0]
w4_n = np.array([2 * np.pi * (f4 / SAMPLING_FREQUENCY)], dtype=np.float16)[0]
w5_n = np.array([2 * np.pi * (f5 / SAMPLING_FREQUENCY)], dtype=np.float16)[0]
w6_n = np.array([2 * np.pi * (f6 / SAMPLING_FREQUENCY)], dtype=np.float16)[0]

# wrapped frequencies
w1 = 2 * np.tan(w1_n / 2, dtype=np.float16)
w2 = 2 * np.tan(w2_n / 2, dtype=np.float16)
w3 = 2 * np.tan(w3_n / 2, dtype=np.float16)
w4 = 2 * np.tan(w4_n / 2, dtype=np.float16)
w5 = 2 * np.tan(w5_n / 2, dtype=np.float16)
w6 = 2 * np.tan(w6_n / 2, dtype=np.float16)

# High-pass filter b0, b1, b2, a1, a2
a0 = np.array([4 * q1 + 2 * w1 + w1 ** 2], dtype=np.float16)[0]
a1 = np.array([2 * (w1 ** 2) - 8 * q1], dtype=np.float16)[0]
a2 = np.array([4 * q1 - 2 * w1 + w1 ** 2], dtype=np.float16)[0]
b0 = np.array([4 * q1], dtype=np.float16)[0]
b1 = np.array([-8 * q1], dtype=np.float16)[0]
b2 = np.array([4 * q1], dtype=np.float16)[0]
print(f"High pass: num = {[b0, b1, b2]}   den = {[a0, a1, a2]}")
a0 = a0 * SCALE_FACTOR
float_h_h = [b0 / a0, b1 / a0, b2 / a0, -a1 / a0, -a2 / a0]
h_h = float_to_q31(float_h_h)

# Low-pass filter b0, b1, b2, a1, a2
a0 = np.array([4 * q2 + 2 * w2 + (w2 ** 2) * q2], dtype=np.float16)[0]
a1 = np.array([2 * (w2 ** 2) * q2 - 8 * q2], dtype=np.float16)[0]
a2 = np.array([4 * q2 - 2 * w2 + (w2 ** 2) * q2], dtype=np.float16)[0]
b0 = np.array([(w2 ** 2) * q2], dtype=np.float16)[0]
b1 = np.array([2 * (w2 ** 2) * q2], dtype=np.float16)[0]
b2 = np.array([(w2 ** 2) * q2], dtype=np.float16)[0]
print(f"low pass: num = {[b0, b1, b2]}   den = {[a0, a1, a2]}")
a0 = a0 * SCALE_FACTOR
float_h_l = [b0 / a0, b1 / a0, b2 / a0, -a1 / a0, -a2 / a0]
h_l = float_to_q31(float_h_l)

# Acceleration-velocity transform filter b0, b1, b2, a1, a2
a0 = np.array([4 * q4 + 2 * w4 + (w4 ** 2) * q4], dtype=np.float16)[0]
a1 = np.array([2 * (w4 ** 2) * q4 - 8 * q4], dtype=np.float16)[0]
a2 = np.array([4 * q4 - 2 * w4 + (w4 ** 2) * q4], dtype=np.float16)[0]
b0 = np.array([(w4 ** 2) * q4 + 2 * ((q4 * (w4 ** 2)) / w3)], dtype=np.float16)[0]
b1 = np.array([2 * (w4 ** 2) * q4], dtype=np.float16)[0]
b2 = np.array([(w4 ** 2) * q4 - 2 * ((q4 * (w4 ** 2)) / w3)], dtype=np.float16)[0]
print(f"acceleration velocity: num = {[b0, b1, b2]}   den = {[a0, a1, a2]}")
a0 = a0 * SCALE_FACTOR
float_h_t = [b0 / a0, b1 / a0, b2 / a0, -a1 / a0, -a2 / a0]
h_t = float_to_q31(float_h_t)

# Upward step filter b0, b1, b2, a1, a2
"""
a0 =
a1 =
a2 =
b0 =
b1 =
b2 =
"""
float_h_s = [1, 0, 0, 0, 0]
print(f"low pass: num = {[1, 0, 0]}   den = {[1, 0, 0]}")
for index in range(len(float_h_s)):
    float_h_s[index] = float_h_s[index] / SCALE_FACTOR
h_s = float_to_q31(float_h_s)
