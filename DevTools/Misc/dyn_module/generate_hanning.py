#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@brief: This python script is used to generate the lookup tables containing the hanning heights for
    different window sizes.

This file generates a header file named dyn_process_din_hanning.h.
The created header file contains multiple static const float32_t arrays with the hanning weights for the
specified window length.
Since the hanning windows are symmetrical from the center point, only the first half of the window is stored.

For each window length the following data is generated:

    #define DYNPROCESSDINHANNING_HANNING_4096_LENGTH       4096U  // Define with the window length
    // Define with the number of elements in the lookup table.
    #define DYNPROCESSDINHANNING_HANNING_4096_ARRAY_LENGTH 2048U

    static const float32_t DynProcessDinHanning_Hanning4096[DYNPROCESSDINHANNING_HANNING_4096_ARRAY_LENGTH] =
        {  // Array with the first half of the hanning weights for the specified window lengths.

@Note: Adding or removing support for different window sizes:
    This script generates a support for the window sizes in the list: HANNING_SIZES. To add or remove support
    for a given window size add/remove the window size to/from the list.

"""

import matplotlib.pyplot as plt
import numpy as np

MAX_WINDOW_LEN = 4096
MAX_FLOATS_PER_LINE = 1

HANNING_SIZES = [4096, 2048, 1024, 512, 256, 128]


PLOT_HANNING = True

str_header = (
    "/**",
    "  * \\file    dyn_process_din_hanning.h",
    "  *",
    "  * \\brief   Header file containing the definition of the Hanning window.",
    "  * \\author  Worldsensing",
    "  *",
    "  * \\section License",
    "  *          (C) Copyright 2023 Worldsensing, http://www.worldsensing.com",
    "  * \\note    This files has been generated using file in ./DevTools/Misc/dyn_module/generate_hanning.py",
    "  */",
    "#ifndef __DYN_PROCESS_DIN_HANNING_H__",
    "#define __DYN_PROCESS_DIN_HANNING_H__",
    "",
    '#include "ws_types.h"',
    "",
    "",
    "/************************************ Defines *************************************************/",
    "",
)

str_tail = ("#endif /* __DYN_PROCESS_DIN_H__ */",)


def write_hanning(size, f):
    str_mid_start = (
        f"#define DYNPROCESSDINHANNING_HANNING_{size}_LENGTH       {size}U",
        f"#define DYNPROCESSDINHANNING_HANNING_{size}_ARRAY_LENGTH {int(size/2)}U",
        "",
        f"static const float32_t"
        + f"DynProcessDinHanning_Hanning{size}[DYNPROCESSDINHANNING_HANNING_{size}_ARRAY_LENGTH] = "
        + "{",
    )

    str_mid_end = (
        "};",
        "",
        "",
    )

    data = np.hanning(size)

    if PLOT_HANNING:
        plt.figure()
        plt.title(f"Hanning {size}")
        plt.plot(data)
        print(data)
        plt.show()

    f.writelines(s + "\n" for s in str_mid_start)
    for i in range(int(size / (2 * MAX_FLOATS_PER_LINE))):
        j = i * MAX_FLOATS_PER_LINE
        s = "    "
        for c in range(MAX_FLOATS_PER_LINE):
            if c != 0:
                s += ", "
            s += "{:.10e}f".format(data[j + c])
        if i + 1 < int(size / MAX_FLOATS_PER_LINE):
            s += ","
        f.write(s + "\n")
    f.writelines(s + "\n" for s in str_mid_end)


with open("dyn_process_din_hanning.h", "w") as f:
    f.writelines(s + "\n" for s in str_header)

    for h in HANNING_SIZES:
        write_hanning(h, f)

    f.writelines(s + "\n" for s in str_tail)
