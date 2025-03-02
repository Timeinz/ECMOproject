# this is a urtc.py wrapper, for ds3231, to program it / use it how we need in our project (simplified)
# pulls out the main functions we will use from the urtc module, writes the settings, and also extends for milliseconds functionality

import urtc
import time

# control and status registers, as explained in documentation (see comment at bottom)
control = 0x00011100
status  = 0x00000000
address = 0x68

class DS3231:
    def __init__(self, i2c, address=address):
        self.rtc = urtc.DS3231(i2c, address)
        self.millis_baseline = 0
        self.last_datetime_no_ms = None

    def read_datetime(self):    # reading the datetime, and extending it for millisecond functionality
        datetime_now_no_ms = self.rtc.datetime()
        if datetime_now_no_ms != self.last_datetime_no_ms:
            self.last_datetime_no_ms = datetime_now_no_ms
            self.millis_baseline = time.ticks_ms()
            datetime_now = urtc.datetime_tuple(*datetime_now_no_ms,millisecond=0)
        else:
            millisecond = min(time.ticks_ms() - self.millis_baseline, 999)
            datetime_now = urtc.datetime_tuple(*datetime_now_no_ms,millisecond=millisecond)
        return datetime_now
    
    def write_datetime(self, datetime):
        self.rtc.datetime(datetime)

    def lost_power(self):       # This is used to check for errors
        return self.rtc.lost_power()
    
    def set_control(self):
        self.rtc._register(self.rtc._CONTROL_REGISTER, control)
    
    def reset_status(self):
        self.rtc._register(self.rtc._STATUS_REGISTER, status)


# Clock Documentation "https://www.analog.com/media/en/technical-documentation/data-sheets/DS3231.pdf"
# Control Register (0Eh)
# •	 Bit 7 Enable Oscillator, should always be on for us (0)
# •	 Bit 6 battery-backed square wave, we don’t need the square wave (0)
# •	 Bit 5 Convert Temperature, is done automatically every 64s, I don’t intend to user initiate this (0)
# •	 Bit 4 and 3 set the frequency of the square ware. I don’t plan to use the square wave (1, 1)
# •	 Bit 2 this bit controls the square wave, don’t need (1)
# •	 Bit 1 and 0 these control alarms, we don’t plan to use alarms (0, 0)
# Status Register (0Fh)
# •	 Bit 7 Oscillator Stop Flag, this is essentially our error flag, will be set if oscillator stopped, eg. Through power loss, or first time initializing. If 1, it’s error. Needs to be written back to 0
# •	 Bit 3 Enable 32kHz output. We don’t need this --> set to 0
# •	 Bit 2 Busy indicator. If 1 it’s busy (temp conversion), 0 if it’s idle. Probably don’t need this
# •	 Bit 1 and 0 Alarm flags. Probably don’t need them. (0)