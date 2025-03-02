# this is a urtc.py wrapper, for ds3231, to program it / use it how we need in our project (simplified)
# pulls out the main functions we will use from the urtc module, writes the settings, and also extends for milliseconds functionality

import urtc
import time

# control and status registers, as explained in documentation (see comment at bottom)
control     = 0x00011100
status      = 0x00000000
address     = 0x68
TEMP_MSB    = 0x11  # Temperature register addresses. Most significant byte
TEMP_LSB    = 0x12  # Least significant byte

class DS3231:
    def __init__(self, i2c, address=address, indicator=None):
        self.rtc                    = urtc.DS3231(i2c, address)
        self.millis_baseline        = 0
        self.last_datetime_no_ms    = None
        self.indicator              = indicator

    def initialize(self):
        self.set_control()
        if self.is_live() == False:
            return False
        else:
            self.reset_status()
        return True

    def read_datetime(self):    # reading the datetime, and extending it for millisecond functionality
        datetime_now_no_ms = self.rtc.datetime()
        if datetime_now_no_ms != self.last_datetime_no_ms:  # new datetime value
            self.last_datetime_no_ms = datetime_now_no_ms   # init lat datetime value
            self.millis_baseline = time.ticks_ms()          # init millis baseline
            datetime_now = urtc.datetime_tuple(*datetime_now_no_ms,millisecond=0)   # write the datetime tuple with millis = 0
        else:                                               # still the same second as previous datetime read
            millisecond = min(time.ticks_ms() - self.millis_baseline, 999)          # counted the milliseconds from first read of this second (capped at 999)
            datetime_now = urtc.datetime_tuple(*datetime_now_no_ms,millisecond=millisecond) # write the new datetime tuple with the milliseconds value
        return datetime_now
    
    def write_datetime(self, datetime):
        self.rtc.datetime(datetime)
        if self.read_datetime().year > 2020:
            self.reset_status()
            if self.indicator is not None:
                self.indicator.value(0)

    def is_live(self):
        if self.last_datetime_no_ms is None:
            self.read_datetime()
        flag = self.rtc.lost_power() or self.last_datetime_no_ms.year < 2020
        if flag and self.indicator is not None:
            self.indicator.value(1)
        return not flag
    
    def set_control(self):
        self.rtc._register(self.rtc._CONTROL_REGISTER, control)
    
    def reset_status(self):
        self.rtc._register(self.rtc._STATUS_REGISTER, status)
    
    def read_temperature(self):     # Reads the temperature from the DS3231 temperature registers. Returns the temperature in degrees Celsius.
        data = self.rtc.i2c.readfrom_mem(address, TEMP_MSB, 2)   # Read 2 bytes starting from TEMP_MSB (0x11)
        msb = data[0]  # Integer part (and sign)
        lsb = data[1]  # Fractional part in upper 2 bits
        # Check if temperature is negative (MSB bit 7 is set)
        if msb & 0x80:
            # Handle two's complement for negative temperatures
            temp = -((~msb & 0x7F) + 1) - (lsb >> 6) * 0.25
        else:
            # Positive temperature: integer part + fractional part (0.25°C steps)
            temp = msb + (lsb >> 6) * 0.25
        return temp


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