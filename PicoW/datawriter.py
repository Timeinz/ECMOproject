# basic structure for writing the files to the sd card is:
# write into: /sd/data/<day>/<hour/min>/one_file_per_minute.txt (or .bin ?)
# then if sd card is like 80% full or something start deleting the oldest 20% of data.

import uos

base_path = "/sd/data"
header = "timestamp,channel0,channel1,channel2,channel3,channel4,channel5,channel6,channel7\n"

class DataWriter():
    def __init__(self, base_path=base_path, header=header):
        self.base_path  = base_path
        self.header     = header
        self.message    = ""

    def get_current_path(self, datetime_int, use_bin=False):
        # Ensure datetime_int is our human-readable 17digit int.
        s = f"{datetime_int:017d}"
        day = s[0:8]  # YYYYMMDD
        hour_min = s[8:12]  # HHMM
        ext = ".bin" if use_bin else ".txt"
        return f"{self.base_path}/{day}/{hour_min}{ext}"  # /sd/data/YYYYMMDD/HHMM.txt or .bin

    def write_data(self, data):
        full_path = self.get_current_path(data[0])
        # Check if file exists
        try:
            uos.stat(full_path)
            header_written = True
        except OSError:
            header_written = False

        with open(full_path, "a") as file:  # Append mode
            if not header_written:
                file.write(header)
            for i in range(len(data)):
                if i == 0:
                    self.message = str(data[i])
                else:
                    self.message = self.message + "," + data[i]
            file.write(self.message)
        file.flush()