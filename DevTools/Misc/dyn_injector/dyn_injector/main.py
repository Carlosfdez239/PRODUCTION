#!/usr/bin/env python3
import argparse
import csv
import decimal
import logging
from decimal import Decimal
from enum import Enum, auto

import dyn_injector.node_manager


class Adxl35xModelT(Enum):
    ADXL355 = auto()
    ADXL357 = auto()


ADXL35X_MODEL = Adxl35xModelT.ADXL355
ADXL35X_MAX_MEASUREMENT_VAL = 524288
ADXL35X_BASE_LO_SCALE = 1
ADXL35X_BASE_HI_SCALE = 5

logger = logging.getLogger(__name__)


def transform_float_to_raw(f_value):
    if ADXL35X_MODEL == Adxl35xModelT.ADXL355:
        scale = ADXL35X_BASE_LO_SCALE
    else:
        scale = ADXL35X_BASE_HI_SCALE

    scale *= 2
    return int((f_value * ADXL35X_MAX_MEASUREMENT_VAL) / scale)


def main():
    parser = argparse.ArgumentParser(
        prog="DYN injector",
        fromfile_prefix_chars="@",
        description="Inject data to a test DYN node from a csv file.",
        epilog="Developed by Worldsensing",
    )

    parser.add_argument(
        "-l",
        "--log-level",
        help="debug level",
        type=str,
        default="info",
        choices=["error", "warn", "info", "debug"],
    )
    parser.add_argument("-i", "--input", help="Input DB file path", type=str, required=True)
    parser.add_argument("-c", "--com", help="Serial device path", type=str, default="/dev/ttyUSB0")

    config = parser.parse_args()
    print(config)

    logging.basicConfig(level=config.log_level.upper())

    data = []

    with open(config.input) as csvfile:
        dyn_data_reader = csv.reader(csvfile, delimiter=",")
        for row in dyn_data_reader:
            try:
                data.extend([transform_float_to_raw(Decimal(e)) for e in row])
            except decimal.InvalidOperation:
                pass

    logger.info(f"Read {len(data)} elements")

    if 0 != len(data) % 3:
        logger.error(
            "The number of elements in the CSV file is not multiple of 3."
            "The CSV must contain 3 columns, one for each exis (x, y, z)."
        )
        return 1

    dyn_injector.node_manager.init(config.com, logger_name=__name__)
    ok = dyn_injector.node_manager.inject_data(data)

    if ok:
        logger.info("Data injected successfully.")
    else:
        logger.error("Data injection failed.")

    return 0


if __name__ == "__main__":
    exit(main())
