import utime
from urtc import DateTimeTuple

def to_iso8601(dt: DateTimeTuple) -> str:
    return f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}T{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}.{dt.millisecond:03d}Z"

def to_unix_ms(dt: DateTimeTuple) -> int:
    # Convert to Unix timestamp (seconds) using utime.mktime, then add milliseconds
    time_tuple = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.weekday, 1)  # yearday=1 (ignored)
    seconds = utime.mktime(time_tuple)
    return seconds * 1000 + dt.millisecond

def to_human_int(dt: DateTimeTuple) -> int:
    return int(f"{dt.year:04d}{dt.month:02d}{dt.day:02d}{dt.hour:02d}{dt.minute:02d}{dt.second:02d}{dt.millisecond:03d}")

def from_human_int(human_int: int) -> DateTimeTuple:
    s = f"{human_int:017d}"  # Ensure 17 digits
    year = int(s[0:4])
    month = int(s[4:6])
    day = int(s[6:8])
    hour = int(s[8:10])
    minute = int(s[10:12])
    second = int(s[12:14])
    millisecond = int(s[14:17])
    weekday = utime.localtime(utime.mktime((year, month, day, hour, minute, second, 0, 1)))[6]  # Calculate weekday
    return DateTimeTuple(year, month, day, weekday, hour, minute, second, millisecond)

def human_int_to_iso8601(human_int: int) -> str:
    dt = from_human_int(human_int)
    return f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}T{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}.{dt.millisecond:03d}Z"

def human_int_to_unix_ms(human_int: int) -> int:
    dt = from_human_int(human_int)
    time_tuple = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.weekday, 1)
    seconds = utime.mktime(time_tuple)
    return seconds * 1000 + dt.millisecond