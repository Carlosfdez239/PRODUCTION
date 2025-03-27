import datetime
from datetime import timedelta, tzinfo


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
