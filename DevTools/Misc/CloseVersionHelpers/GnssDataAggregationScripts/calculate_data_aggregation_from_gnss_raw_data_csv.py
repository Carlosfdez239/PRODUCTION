#!/usr/bin/env python3

"""
This script reads a CSV file (gnss_raw_data.csv) containing GNSS raw data and calculates
the rolling medians for each axis (lat, lon, alt).
The output is saved to a new CSV file (calculated-readings.csv) in the same format as the gateway generates
so it can be easily compared with the gateway output.
There might be differences in the last decimal place due to precision issues between the node and Pandas.

To run the script, execute the following command:
./calculate_data_aggregation_from_gnss_raw_data_csv.py
"""

import csv
import sys
from io import StringIO

import numpy as np
import pandas as pd


def read_csv_to_df(file_path):
    return pd.read_csv(file_path)


def compute_rolling_medians(df):
    # Parse the time column into datetime format
    df["Time"] = pd.to_datetime(df["readTimestamp"])

    # Reshape the data to long format for raw data processing
    melted = pd.melt(
        df,
        id_vars=["Time"],
        var_name="Sensor",
        value_name="Value",
    )

    # Extract the axis (lat, lon, alt) and raw ID from the Sensor column
    melted[["RawID", "Axis"]] = melted["Sensor"].str.extract(r"raw(\d+)_(lat|lon|alt)")

    # Ensure the 'Value' column contains only numeric data
    melted["Value"] = pd.to_numeric(melted["Value"], errors="coerce")

    # Drop rows of readTimestamp since the 'Value' is NaN (non-numeric values)
    melted = melted[melted["Sensor"] != "readTimestamp"]

    # Sort by Time to ensure proper rolling
    melted = melted.sort_values(by="Time")

    # Calculate rolling medians for each axis (lat, lon, alt)
    results = []

    for axis in ["lat", "lon", "alt"]:
        axis_data = melted[melted["Axis"] == axis].copy()
        axis_data.set_index("Time", inplace=True)

        # Calculate rolling medians
        axis_data["Last6hMedian"] = axis_data["Value"].rolling("6H", closed="right").median()
        axis_data["Last24hMedian"] = axis_data["Value"].rolling("24H", closed="right").median()

        # Reset index and add results
        axis_data.reset_index(inplace=True)
        results.append(axis_data)

    # Concatenate results for all axes
    combined = pd.concat(results)

    # Group by Time and Axis to calculate sample medians and rolling medians
    final_output = (
        combined.groupby(["Time", "Axis"])
        .agg(
            SampleMedian=("Value", "median"),  # Median of raw values in the sample for each axis
            Last6hMedian=("Last6hMedian", "last"),  # Last calculated 6-hour median
            Last24hMedian=("Last24hMedian", "last"),  # Last calculated 24-hour median
            # Number of samples in the 1-hour window, skipping NaN values
            Samples1h=("Value", "count"),
        )
        .reset_index()
    )

    # Pivot the data so each timestamp has one row with axis-specific columns
    wide_format = final_output.pivot(
        index="Time", columns="Axis", values=["SampleMedian", "Last6hMedian", "Last24hMedian"]
    )

    # Flatten the multi-level column index
    wide_format.columns = ["_".join(col).strip() for col in wide_format.columns.values]

    # Reset the index to make 'Time' a column again
    wide_format.reset_index(inplace=True)

    wide_format["samples1H"] = wide_format["Time"].map(
        lambda t: final_output[final_output["Time"] == t].head(1)["Samples1h"].values[0]
    )
    wide_format["samples6H"] = wide_format["Time"].map(
        lambda t: wide_format[
            (wide_format["Time"] > t - pd.Timedelta(hours=6))
            & (wide_format["Time"] <= t)
            & (wide_format["SampleMedian_lat"].notnull())
        ].shape[0]
    )
    wide_format["samples24H"] = wide_format["Time"].map(
        lambda t: wide_format[
            (wide_format["Time"] > t - pd.Timedelta(hours=24))
            & (wide_format["Time"] <= t)
            & (wide_format["SampleMedian_lat"].notnull())
        ].shape[0]
    )

    wide_format["SampleMedian_alt"] = wide_format["SampleMedian_alt"].round(4).fillna(0)
    wide_format["SampleMedian_lat"] = wide_format["SampleMedian_lat"].round(9).fillna(0)
    wide_format["SampleMedian_lon"] = wide_format["SampleMedian_lon"].round(9).fillna(0)

    wide_format["Last6hMedian_alt"] = wide_format["Last6hMedian_alt"].round(4).fillna(0)
    wide_format["Last6hMedian_lat"] = wide_format["Last6hMedian_lat"].round(9).fillna(0)
    wide_format["Last6hMedian_lon"] = wide_format["Last6hMedian_lon"].round(9).fillna(0)

    wide_format["Last24hMedian_alt"] = wide_format["Last24hMedian_alt"].round(4).fillna(0)
    wide_format["Last24hMedian_lat"] = wide_format["Last24hMedian_lat"].round(9).fillna(0)
    wide_format["Last24hMedian_lon"] = wide_format["Last24hMedian_lon"].round(9).fillna(0)

    return wide_format


def test_always_pass():
    pass


def _generate_csv_string_for_testing(data):
    # Generate header
    fieldnames = ["readTimestamp"] + [
        f"raw{i}_{dim}" for i in range(3) for dim in ["lat", "lon", "alt"]
    ]
    header = ",".join(fieldnames)

    # Generate rows
    rows = []
    for entry in data:
        row = [entry.get("readTimestamp", "")]
        for i in range(3):  # Loop through raw0, raw1, raw2
            for dim in ["lat", "lon", "alt"]:
                key = f"raw{i}_{dim}"
                value = entry.get(key, "")
                if isinstance(value, float):  # Format only if value is a float
                    if dim == "alt":
                        row.append(f"{value:.4f}")  # 4 decimals for altitude
                    else:  # lat or lon
                        row.append(f"{value:.9f}")  # 9 decimals for latitude/longitude
                elif value != "":
                    row.append(str(value))
                else:
                    row.append("")
        # Trim trailing empty values
        row = ",".join(row).rstrip(",")
        rows.append(row)

    # Combine header and rows
    return f"{header}\n" + "\n".join(rows)


def test_compute_rolling_medians():
    csv_data_hardcoded = (
        "readTimestamp,raw0_lat,raw0_lon,raw0_alt,raw1_lat,raw1_lon,raw1_alt,raw2_lat,raw2_lon,raw2_alt\n"
        "2024-12-05T00:00:00Z,41.371700001,2.130200001,100.1234,41.371800002,2.130300002,100.5678,"
        "41.371900003,2.130400003,101.0000\n"
        "2024-12-05T03:00:00Z,41.372000001,2.130500001,200.0000,41.372100002,2.130600002,200.5000,"
        "41.372200003,2.130700003,201.0000\n"
        "2024-12-05T03:01:00Z,41.372300001,2.130800001,250.0000\n"
        "2024-12-05T06:00:00Z,41.372600002,2.130900002,300.5000,41.372500001,2.130800001,300.0000,"
        "41.372700003,2.131000003,301.0000\n"
        "2024-12-05T06:01:00Z,41.372800001,2.131100001,350.0000\n"
        "2024-12-05T09:00:00Z,41.373000001,2.131100001,400.0000,41.373100002,2.131200002,400.5000,"
        "41.373200003,2.131300003,401.0000\n"
        "2024-12-05T12:00:00Z,41.373500001,2.131500001,500.0000,41.373600002,2.131600002,500.5000,"
        "41.373700003,2.131700003,501.0000\n"
        "2024-12-06T00:00:00Z,40.000000000,2.000000000,10.0000,35.000000000,1.000000000,9.0000,"
        "37.000000000,1.500000000,9.5000\n"
        "2024-12-06T01:00:00Z"
    )

    data = [
        {
            "readTimestamp": "2024-12-05T00:00:00Z",
            "raw0_lat": 41.371700001,
            "raw0_lon": 2.130200001,
            "raw0_alt": 100.1234,
            "raw1_lat": 41.371800002,
            "raw1_lon": 2.130300002,
            "raw1_alt": 100.5678,
            "raw2_lat": 41.371900003,
            "raw2_lon": 2.130400003,
            "raw2_alt": 101.0000,
        },
        {
            "readTimestamp": "2024-12-05T03:00:00Z",
            "raw0_lat": 41.372000001,
            "raw0_lon": 2.130500001,
            "raw0_alt": 200.0000,
            "raw1_lat": 41.372100002,
            "raw1_lon": 2.130600002,
            "raw1_alt": 200.5000,
            "raw2_lat": 41.372200003,
            "raw2_lon": 2.130700003,
            "raw2_alt": 201.0000,
        },
        {
            "readTimestamp": "2024-12-05T03:01:00Z",
            "raw0_lat": 41.372300001,
            "raw0_lon": 2.130800001,
            "raw0_alt": 250.0000,
        },
        {
            "readTimestamp": "2024-12-05T06:00:00Z",
            "raw0_lat": 41.372600002,
            "raw0_lon": 2.130900002,
            "raw0_alt": 300.5000,
            "raw1_lat": 41.372500001,
            "raw1_lon": 2.130800001,
            "raw1_alt": 300.0000,
            "raw2_lat": 41.372700003,
            "raw2_lon": 2.131000003,
            "raw2_alt": 301.0000,
        },
        {
            "readTimestamp": "2024-12-05T06:01:00Z",
            "raw0_lat": 41.372800001,
            "raw0_lon": 2.131100001,
            "raw0_alt": 350.0000,
        },
        {
            "readTimestamp": "2024-12-05T09:00:00Z",
            "raw0_lat": 41.373000001,
            "raw0_lon": 2.131100001,
            "raw0_alt": 400.0000,
            "raw1_lat": 41.373100002,
            "raw1_lon": 2.131200002,
            "raw1_alt": 400.5000,
            "raw2_lat": 41.373200003,
            "raw2_lon": 2.131300003,
            "raw2_alt": 401.0000,
        },
        {
            "readTimestamp": "2024-12-05T12:00:00Z",
            "raw0_lat": 41.373500001,
            "raw0_lon": 2.131500001,
            "raw0_alt": 500.0000,
            "raw1_lat": 41.373600002,
            "raw1_lon": 2.131600002,
            "raw1_alt": 500.5000,
            "raw2_lat": 41.373700003,
            "raw2_lon": 2.131700003,
            "raw2_alt": 501.0000,
        },
        {
            "readTimestamp": "2024-12-06T00:00:00Z",
            "raw0_lat": 40.000000000,
            "raw0_lon": 2.000000000,
            "raw0_alt": 10.0000,
            "raw1_lat": 35.000000000,
            "raw1_lon": 1.000000000,
            "raw1_alt": 9.0000,
            "raw2_lat": 37.000000000,
            "raw2_lon": 1.500000000,
            "raw2_alt": 9.5000,
        },
        {
            "readTimestamp": "2024-12-06T01:00:00Z",
        },
    ]

    csv_data_generated = _generate_csv_string_for_testing(data)

    # print(csv_data_hardcoded)
    # print(csv_data_generated)
    assert csv_data_generated == csv_data_hardcoded

    df = pd.read_csv(StringIO(csv_data_generated))
    # df.columns = df.columns.str.strip()
    wide_format = compute_rolling_medians(df)

    for i, row in enumerate(data):
        assert pd.to_datetime(data[0]["readTimestamp"]) == wide_format["Time"][0]

        if len(row.keys()) == 1:
            expected_median_alt = 0
            expected_median_lat = 0
            expected_median_lon = 0
            expected_raw_samples = 0
        else:
            # Extract raw data
            latitudes = [v for k, v in row.items() if "lat" in k]
            longitudes = [v for k, v in row.items() if "lon" in k]
            altitudes = [v for k, v in row.items() if "alt" in k]
            # Expected medians
            expected_median_lat = np.median(latitudes)
            expected_median_lon = np.median(longitudes)
            expected_median_alt = np.median(altitudes)
            expected_raw_samples = (len(row.keys()) - 1) / 3
        assert expected_raw_samples == wide_format["samples1H"][i]
        assert expected_median_lat == wide_format["SampleMedian_lat"][i]
        assert expected_median_lon == wide_format["SampleMedian_lon"][i]
        assert expected_median_alt == wide_format["SampleMedian_alt"][i]

        # Check rolling medians
        timestamp = pd.to_datetime(row["readTimestamp"])
        print(f"timestamp: {timestamp}")

        relevant_rows_6h = [
            d
            for d in data
            if timestamp - pd.Timedelta(hours=6) < pd.to_datetime(d["readTimestamp"]) <= timestamp
        ]
        lat_6h = [v for d in relevant_rows_6h for k, v in d.items() if "lat" in k]
        lon_6h = [v for d in relevant_rows_6h for k, v in d.items() if "lon" in k]
        alt_6h = [v for d in relevant_rows_6h for k, v in d.items() if "alt" in k]
        samples6h = [d for d in relevant_rows_6h if len(d.keys()) > 1]
        assert len(samples6h) == wide_format["samples6H"][i]
        assert round(np.median(lat_6h), 9) == wide_format["Last6hMedian_lat"][i]
        assert round(np.median(lon_6h), 9) == wide_format["Last6hMedian_lon"][i]
        print(f"i: {i}, alt_6h: {alt_6h}, wide_format: {wide_format['Last6hMedian_alt'][i]}")
        assert round(np.median(alt_6h), 4) == wide_format["Last6hMedian_alt"][i]

        relevant_rows_24h = [
            d
            for d in data
            if timestamp - pd.Timedelta(hours=24) < pd.to_datetime(d["readTimestamp"]) <= timestamp
        ]
        lat_24h = [v for d in relevant_rows_24h for k, v in d.items() if "lat" in k]
        lon_24h = [v for d in relevant_rows_24h for k, v in d.items() if "lon" in k]
        alt_24h = [v for d in relevant_rows_24h for k, v in d.items() if "alt" in k]
        samples24h = [d for d in relevant_rows_24h if len(d.keys()) > 1]
        assert len(samples24h) == wide_format["samples24H"][i]
        assert round(np.median(lat_24h), 9) == wide_format["Last24hMedian_lat"][i]
        assert round(np.median(lon_24h), 9) == wide_format["Last24hMedian_lon"][i]
        print(f"longitude: {lon_24h}")
        print(f"expected_median_lon: {round(np.median(lon_24h), 9)}")
        assert round(np.median(alt_24h), 4) == wide_format["Last24hMedian_alt"][i]

    print_in_parsing_library_style(wide_format)
    # assert False
    df_gw_calculated = write_to_csv_in_gw_format(wide_format, "", write_to_csv=False)

    # TODO: the 4th element in 24h lon should be 2.130650003 instead of 2.130650002.
    # This is a precision issue between google spreadsheet and pandas.
    gw_expected_dict = {
        "Date-and-time": [
            "2024-12-05T00:00:00Z",
            "2024-12-05T03:00:00Z",
            "2024-12-05T03:01:00Z",
            "2024-12-05T06:00:00Z",
            "2024-12-05T06:01:00Z",
            "2024-12-05T09:00:00Z",
            "2024-12-05T12:00:00Z",
            "2024-12-06T00:00:00Z",
            "2024-12-06T01:00:00Z",
        ],
        "Timezone": ["UTC+00:00"] * 9,
        "1Sample-altitude-meters-a:00:00:00": [
            100.5678,
            200.5,
            250,
            300.5,
            350,
            400.5,
            500.5,
            9.5,
            0,
        ],
        "1Sample-latitude-degrees-a:00:00:00": [
            41.371800002,
            41.372100002,
            41.372300001,
            41.372600002,
            41.372800001,
            41.373100002,
            41.373600002,
            37,
            0,
        ],
        "1Sample-longitude-degrees-a:00:00:00": [
            2.130300002,
            2.130600002,
            2.130800001,
            2.130900002,
            2.131100001,
            2.131200002,
            2.131600002,
            1.5,
            0,
        ],
        "1Sample-numSamples-count-a:00:00:00": [3, 3, 1, 3, 1, 3, 3, 3, 0],
        "6hAverage-altitude-meters-a:00:01:00": [
            100.5678,
            150.5,
            200,
            250,
            275,
            325.5,
            401,
            9.5,
            9.5,
        ],
        "6hAverage-latitude-degrees-a:00:01:00": [
            41.371800002,
            41.371950002,
            41.372000001,
            41.372300001,
            41.372400001,
            41.372750002,
            41.373200003,
            37,
            37,
        ],
        "6hAverage-longitude-degrees-a:00:01:00": [
            2.130300002,
            2.130450002,
            2.130500001,
            2.130800001,
            2.130800001,
            2.131050002,
            2.131300003,
            1.5,
            1.5,
        ],
        "6hAverage-numSamples-count-a:00:01:00": [1, 2, 3, 3, 4, 4, 3, 1, 1],
        "24hAverage-altitude-meters-a:00:02:00": [
            100.5678,
            150.5,
            200,
            200.75,
            201,
            275,
            300.5,
            300.5,
            300.5,
        ],
        "24hAverage-latitude-degrees-a:00:02:00": [
            41.371800002,
            41.371950002,
            41.372000001,
            41.372150003,
            41.372200003,
            41.372400001,
            41.372600002,
            41.372600002,
            41.372600002,
        ],
        "24hAverage-longitude-degrees-a:00:02:00": [
            2.130300002,
            2.130450002,
            2.130500001,
            2.130650002,
            2.130700003,
            2.130800001,
            2.130900002,
            2.130900002,
            2.130900002,
        ],
        "24hAverage-numSamples-count-a:00:02:00": [1, 2, 3, 4, 5, 6, 7, 7, 7],
    }

    # Create the DataFrame

    pd.set_option("display.max_columns", None)  # Show all columns
    pd.set_option("display.max_rows", None)  # Show all rows
    pd.set_option("display.width", 1000)  # Increase the width to prevent wrapping
    pd.set_option("display.float_format", "{:.9f}".format)

    df_gw_expected = pd.DataFrame(gw_expected_dict)
    df_gw_expected["Date-and-time"] = pd.to_datetime(df_gw_expected["Date-and-time"]).dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # comparison = df_gw_calculated.compare(df_gw_expected)
    # print(comparison)

    assert df_gw_expected.equals(df_gw_calculated)

    from pandas.testing import assert_frame_equal

    assert_frame_equal(df_gw_expected, df_gw_calculated, check_dtype=True, atol=0, rtol=0)


def print_in_parsing_library_style(wide_format):
    # Create the desired format
    formatted_output = wide_format.apply(
        lambda row: f"readTimestamp: {row['Time']}; "
        f"lat1H: {row['SampleMedian_lat']}; lon1H: {row['SampleMedian_lon']}; "
        f"alt1H: {row['SampleMedian_alt']}; samples1H: {row['samples1H']}; "
        f"lat6H: {row['Last6hMedian_lat']}; lon6H: {row['Last6hMedian_lon']}; "
        f"alt6H: {row['Last6hMedian_alt']}; samples6H: {row['samples6H']}; "
        f"lat24H: {row['Last24hMedian_lat']}; lon24H: {row['Last24hMedian_lon']}; "
        f"alt24H: {row['Last24hMedian_alt']}; samples24H: {row['samples24H']}",
        axis=1,
    )
    print("\n".join(formatted_output))


def write_to_csv_in_gw_format(wide_format, output_file_name, write_to_csv=True):
    # Create the desired header and columns
    output_data = pd.DataFrame()

    output_data["Date-and-time"] = wide_format["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    output_data["Timezone"] = "UTC+00:00"  # Fixed timezone for all rows
    output_data["1Sample-altitude-meters-a:00:00:00"] = wide_format["SampleMedian_alt"]
    output_data["1Sample-latitude-degrees-a:00:00:00"] = wide_format["SampleMedian_lat"]
    output_data["1Sample-longitude-degrees-a:00:00:00"] = wide_format["SampleMedian_lon"]
    output_data["1Sample-numSamples-count-a:00:00:00"] = wide_format["samples1H"]

    output_data["6hAverage-altitude-meters-a:00:01:00"] = wide_format["Last6hMedian_alt"]
    output_data["6hAverage-latitude-degrees-a:00:01:00"] = wide_format["Last6hMedian_lat"]
    output_data["6hAverage-longitude-degrees-a:00:01:00"] = wide_format["Last6hMedian_lon"]
    output_data["6hAverage-numSamples-count-a:00:01:00"] = wide_format["samples6H"]

    output_data["24hAverage-altitude-meters-a:00:02:00"] = wide_format["Last24hMedian_alt"]
    output_data["24hAverage-latitude-degrees-a:00:02:00"] = wide_format["Last24hMedian_lat"]
    output_data["24hAverage-longitude-degrees-a:00:02:00"] = wide_format["Last24hMedian_lon"]
    output_data["24hAverage-numSamples-count-a:00:02:00"] = wide_format["samples24H"]

    if write_to_csv:
        # Write CSV manually with custom formatting (0.0 has to be 0)
        with open(output_file_name, mode="w", newline="") as file:
            writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC, quotechar='"')

            # Write header
            writer.writerow(output_data.columns)

            # Write rows with custom formatting
            for row in output_data.itertuples(index=False):
                formatted_row = [int(value) if value == 0 else value for value in row]
                writer.writerow(formatted_row)
        print(f"Data saved to {output_file_name}")
    return output_data


def main():
    # Load CSV file
    df = read_csv_to_df("gnss_raw_data.csv")

    # Compute rolling medians and sample counts
    wide_format = compute_rolling_medians(df)

    print_in_parsing_library_style(wide_format)

    write_to_csv_in_gw_format(
        wide_format,
        "calculated-readings.csv",
    )


if __name__ == "__main__":
    sys.exit(main())
