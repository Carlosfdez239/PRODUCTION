#!/usr/bin/env python3
import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

G_TO_M_PER_S2 = 9.80665
SAMPLING_FREQ = 1000
SIGNAL_LEN = 10000  # Default signal length
SIGNAL_MARGINS_PRE = 200  # Space before the signal starts
SIGNAL_MARGINS_POST = 50000  # Space after the signal,
#                              needs to be enough to ensure that the event is terminated.
SHOW = True
SHOW_EXPECTATION = True

PPV_FFT_SIZE = 2048
HANNING_SLOPE_LEN = 1024

TEST_INPUT_VELOCITY_FILE_NAME = "composed_ppv_tester_test1.zip"
TEST_INPUT_ACCELERATION_FILE_NAME = "composed_ppv_tester_test2.zip"
OUTPUT_FILE_NAME = "composed_ppv_test_file.csv"


def save_test_data(x, y, z):
    df = pd.DataFrame({"x": x, "y": y, "z": z})
    df.to_csv(OUTPUT_FILE_NAME, sep=",", index=False, encoding="utf-8")


def plot_data(x, y, z, title):
    fig, ax = plt.subplots(3)
    ax[0].plot(x)
    ax[0].set_ylabel("X")
    ax[1].plot(y)
    ax[1].set_ylabel("Y")
    ax[2].plot(z)
    ax[2].set_ylabel("Z")
    fig.suptitle(title)
    fig.tight_layout()


def compute_acceleration(v):
    """
    Gets a 1D velocity array in m/s and transforms it into acceleration in g.
    """
    t = np.arange(len(v)) / SAMPLING_FREQ
    a = np.gradient(v, t)
    a /= G_TO_M_PER_S2
    return a


def integrate_signal(a):
    """
    Calculate a velocity array in m/2 from a 1D acceleration array in g.
    """
    a = a * G_TO_M_PER_S2
    h = np.hanning(HANNING_SLOPE_LEN * 2)
    a[:HANNING_SLOPE_LEN] *= h[:HANNING_SLOPE_LEN]
    a[-HANNING_SLOPE_LEN:] *= h[-HANNING_SLOPE_LEN:]
    num_windows = int(len(a) / (2 * PPV_FFT_SIZE))
    velocity_signal = np.zeros(len(a))
    for w in range(num_windows):
        lo = w * 2 * PPV_FFT_SIZE
        hi = (w + 1) * 2 * PPV_FFT_SIZE
        aa = a[lo:hi]
        fft_acceleration = np.fft.fft(aa, len(aa))
        f = np.fft.fftfreq(len(aa), d=1 / SAMPLING_FREQ)
        h = np.zeros(len(f))
        h[1:] = 1 / (2 * np.pi * f[1:])
        h = -1j * h
        integrated_acceleration = fft_acceleration * h
        integrated_acceleration[0] = 0
        velocity_complex = np.fft.ifft(integrated_acceleration, len(aa))
        velocity_signal[lo:hi] = np.real(velocity_complex)
    return velocity_signal


def centered_frequency_val(v, i):
    i_min = i - int(PPV_FFT_SIZE / 2)
    i_max = i + int(PPV_FFT_SIZE / 2)
    v_centered = v[max(0, i_min) : min(i_max, len(v) - 1)]
    if i_min < 0:
        v_centered = np.concatenate([np.zeros(-1 * i_min), v_centered])
    if i_max >= len(v):
        v_centered = np.concatenate([v_centered, np.zeros(i_max - len(v) + 1)])

    freqs = np.fft.fft(v_centered, len(v_centered))[: int(len(v_centered) / 2)]
    return np.fft.fftfreq(len(v_centered), d=1 / SAMPLING_FREQ)[np.argmax(freqs)]


def get_ppv_from_vel(x, y, z):
    ppv_x_index = np.argmax(np.abs(x))
    ppv_x_value = np.abs(x[ppv_x_index])
    ppv_x_freq = centered_frequency_val(x, ppv_x_index)

    ppv_y_index = np.argmax(np.abs(y))
    ppv_y_value = np.abs(y[ppv_y_index])
    ppv_y_freq = centered_frequency_val(y, ppv_y_index)

    ppv_z_index = np.argmax(np.abs(z))
    ppv_z_value = np.abs(z[ppv_z_index])
    ppv_z_freq = centered_frequency_val(z, ppv_z_index)

    c = np.sqrt(np.power(x, 2) + np.power(y, 2) + np.power(z, 2))
    ppv_c_index = np.argmax(c)
    ppv_c_value = np.abs(c[ppv_c_index])

    print("------ Expected Results ------")
    print(f"  -) X: ppv_value = {ppv_x_value}, ppv_frequency = {ppv_x_freq}")
    print(f"  -) Y: ppv_value = {ppv_y_value}, ppv_frequency = {ppv_y_freq}")
    print(f"  -) Z: ppv_value = {ppv_z_value}, ppv_frequency = {ppv_z_freq}")
    print(f"  -) Combined: ppv_value = {ppv_c_value}")


def test_0():
    c = input("Input combined val >>")
    x = input("Input X val >>")
    y = input("Input Y val >>")
    z = input("Input Z val >>")
    fx = input("Input X freq >>")
    fy = input("Input Y freq >>")
    fz = input("Input Z freq >>")

    c = int(c) / 1e6
    x = int(x) / 1e6
    y = int(y) / 1e6
    z = int(z) / 1e6
    fx = int(fx) / 1e6
    fy = int(fy) / 1e6
    fz = int(fz) / 1e6

    print("\n\n------ Obtained Results ------")
    print(f"  -) X: ppv_value = {x}, ppv_frequency = {fx}")
    print(f"  -) Y: ppv_value = {y}, ppv_frequency = {fy}")
    print(f"  -) Z: ppv_value = {z}, ppv_frequency = {fz}")
    print(f"  -) Combined: ppv_value = {c}")


def test_1():
    """
    Test 1 is a calibration test to test the gain of the injection tool.
    """

    # --- Generate acceleromter inputs ---
    ax = np.concatenate([np.ones(SIGNAL_LEN), np.zeros(SIGNAL_MARGINS_POST)])
    ay = np.concatenate([np.ones(SIGNAL_LEN), np.zeros(SIGNAL_MARGINS_POST)])
    az = np.concatenate([np.ones(SIGNAL_LEN), np.zeros(SIGNAL_MARGINS_POST)])
    plot_data(ax, ay, az, "test 1 - Acceleration")
    save_test_data(ax, ay, az)

    plt.show()


def test_velocity_input(x_gain, y_gain, z_gain, x_shift, y_shift, z_shift, test_name):
    """
    Generic test function when the input is a velocity signal.
    """
    max_shift = max(x_shift, y_shift, z_shift)

    # --- load signal ---
    df = pd.read_csv(TEST_INPUT_VELOCITY_FILE_NAME, compression="zip", sep=",", encoding="utf-8")
    vx = (
        np.concatenate(
            [
                np.zeros(SIGNAL_MARGINS_PRE + x_shift),
                df["data"].to_numpy(),
                np.zeros(max_shift - x_shift + SIGNAL_MARGINS_POST),
            ]
        )
        * x_gain
    )
    vy = (
        np.concatenate(
            [
                np.zeros(SIGNAL_MARGINS_PRE + y_shift),
                df["data"].to_numpy(),
                np.zeros(max_shift - y_shift + SIGNAL_MARGINS_POST),
            ]
        )
        * y_gain
    )
    vz = (
        np.concatenate(
            [
                np.zeros(SIGNAL_MARGINS_PRE + z_shift),
                df["data"].to_numpy(),
                np.zeros(max_shift - z_shift + SIGNAL_MARGINS_POST),
            ]
        )
        * z_gain
    )
    plot_data(vx, vy, vz, f"{test_name} - Velocity (m/s)")

    # --- Generate acceleromter inputs ---
    ax = compute_acceleration(vx)
    ay = compute_acceleration(vy)
    az = compute_acceleration(vz)
    plot_data(ax, ay, az, f"{test_name} - Acceleration (g)")
    save_test_data(ax, ay, az)

    # --- Expected results ---
    get_ppv_from_vel(vx, vy, vz)

    plt.show()


def test_acceleration_input(names, test_name):
    """
    Generic test function when the input is an acceleration signal.
    """

    # --- load signal ---
    df = pd.read_csv(
        TEST_INPUT_ACCELERATION_FILE_NAME, compression="zip", sep=",", encoding="utf-8"
    )
    ax = (
        np.concatenate(
            [np.zeros(HANNING_SLOPE_LEN), df[names[0]].to_numpy(), np.zeros(SIGNAL_MARGINS_POST)]
        )
        / G_TO_M_PER_S2
    )
    ay = (
        np.concatenate(
            [np.zeros(HANNING_SLOPE_LEN), df[names[1]].to_numpy(), np.zeros(SIGNAL_MARGINS_POST)]
        )
        / G_TO_M_PER_S2
    )
    az = (
        np.concatenate(
            [np.zeros(HANNING_SLOPE_LEN), df[names[2]].to_numpy(), np.zeros(SIGNAL_MARGINS_POST)]
        )
        / G_TO_M_PER_S2
    )
    plot_data(ax, ay, az, f"{test_name} - Acceleration (g)")
    save_test_data(ax, ay, az)

    # --- Generate velocity signals ---
    vx = integrate_signal(ax)
    vy = integrate_signal(ay)
    vz = integrate_signal(az)
    plot_data(vx, vy, vz, f"{test_name} - Velocity (m/s)")

    # --- Expected results ---
    get_ppv_from_vel(vx, vy, vz)

    plt.show()


def test_2():
    """
    Test 2 uses a random signal with the maximum on the Y axis.
    """
    x_gain = 0.8 / 1e6
    y_gain = 1.1 / 1e6
    z_gain = 0.75 / 1e6
    x_shift = 0
    y_shift = 1000
    z_shift = 300
    test_velocity_input(x_gain, y_gain, z_gain, x_shift, y_shift, z_shift, "test 2")


def test_3():
    """
    Test 3 uses a random signal with the maximum on the X axis and the X and Y axis aligned.
    """
    x_gain = 2.0 / 1e6
    y_gain = 1.1 / 1e6
    z_gain = 0.75 / 1e6
    x_shift = 1000
    y_shift = 1000
    z_shift = 300
    test_velocity_input(x_gain, y_gain, z_gain, x_shift, y_shift, z_shift, "test 3")


def test_4():
    """
    Test 4 uses a random signal with the maximum on the Z axis and the X and Z axis aligned.
    """
    x_gain = 1.0 / 1e6
    y_gain = 0.8 / 1e6
    z_gain = 1.1 / 1e6
    x_shift = 1000
    y_shift = 300
    z_shift = 1000
    test_velocity_input(x_gain, y_gain, z_gain, x_shift, y_shift, z_shift, "test 4")


def test_5():
    """
    Test 5 uses a random signal with the maximum on the Z axis and the Y and Z axis aligned.
    """
    x_gain = 1.0 / 1e6
    y_gain = 0.8 / 1e6
    z_gain = 1.1 / 1e6
    x_shift = 300
    y_shift = 1000
    z_shift = 1000
    test_velocity_input(x_gain, y_gain, z_gain, x_shift, y_shift, z_shift, "test 5")


def test_6():
    """
    Test 6 uses a train acceleration signal with the maximum on the X axis and none of the axis aligned.
    """
    test_acceleration_input(["y", "x", "z"], "test 6")


def test_7():
    """
    Test 7 uses a train acceleration signal with the maximum on the Y axis and none of the axis aligned.
    """
    test_acceleration_input(["x", "y", "z"], "test 7")


def test_8():
    """
    Test 8 uses a train acceleration signal with the maximum on the Z axis and none of the axis aligned.
    """
    test_acceleration_input(["z", "x", "y"], "test 8")


tests = [test_0, test_1, test_2, test_3, test_4, test_5, test_6, test_7, test_8]


def print_help():
    print("---- Help msg ---")
    print("Input -t or --test followed by the test number to select test:")
    print("   0 - Test used to translate node debug prints to correct units.")
    print("   1 - Test used to calibrate the injection gain.")
    print("   2 - Test uses a random signal with the maximum on the Y axis.")
    print(
        "   3 - Test uses a random signal with the maximum on the X axis and the X and Y axis aligned."
    )
    print(
        "   4 - Test uses a random signal with the maximum on the Z axis and the X and Z axis aligned."
    )
    print(
        "   5 - Test uses a random signal with the maximum on the Z axis and the Y and Z axis aligned."
    )
    print(
        "   6 - Test uses a train acceleration signal with the maximum on the X axis and none of the axis aligned."
    )
    print(
        "   7 - Test uses a train acceleration signal with the maximum on the Y axis and none of the axis aligned."
    )
    print(
        "   8 - Test uses a train acceleration signal with the maximum on the Z axis and none of the axis aligned."
    )


def main():
    parser = argparse.ArgumentParser(
        prog="PPV tester tool",
        fromfile_prefix_chars="@",
        description="Generates the CSV file required to test the composed PPV vector.",
        epilog="Developed by Worldsensing",
    )

    parser.add_argument(
        "-t",
        "--test",
        help="test number to run",
        type=int,
        default=None,
        choices=[0, 1, 2, 3, 4, 5, 6, 7, 8],
    )
    parser.add_argument("-s", "--show", help="Get help msg", action="store_true")

    config = parser.parse_args()

    if config.show:
        print_help()

    print(f"Test number:  {config.test}")
    if config.test is None:
        print("No test selected")
        print_help()
    elif 0 <= config.test < len(tests):
        tests[config.test]()
    else:
        print("invalid test")


if __name__ == "__main__":
    main()
