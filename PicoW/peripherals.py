from machine import Pin, Timer
import sdcard, os
import config
from ads1256 import ADS1256
from ds3231 import DS3231
from printhandler import PrintHandler
from communication import Communication

ph  = PrintHandler()
spi = Communication.get_spi()
i2c = Communication.get_i2c()

class Peripherals:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Peripherals, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def __init__(self):
        # Check if initialization has already been done to prevent reinitialization
        if not hasattr(self, 'led'):
            self.led            = Pin("LED", Pin.OUT)
            self.IND0           = Pin(config.IND0, Pin.OUT)
            self.IND1           = Pin(config.IND1, Pin.OUT)
            self.IND2           = Pin(config.IND2, Pin.OUT)
            self.leds           = [self.led, self.IND0, self.IND1, self.IND2] # Define the LED pins. The Pico has four on-board LEDs on GPIO pins 25, 22, 21, and 20.
            self.PWR_AFE        = Pin(config.PWR_AFE, Pin.OUT)
            self.ADC            = ADS1256(spi)
            self.SD             = sdcard.SDCard(spi, config.SD_CS)
            self.RTC            = DS3231(i2c)
            self.timer          = Timer() # Setup the timer 
    
    def _init_ADC(self):
        try:
            if (self.ADC.ADS1256_init() != 0): 
                raise Exception()
            ph.print("Successfully connected to ADC")
            return 0
        except Exception as e:
            pass
        ph.print("Failed to connect to ADC")
        return None  # If all retries fail, return None or handle as needed
    
    def blink_callback(self, timer):                            # Timer callback function
        for i in range(len(self.leds)):
            if self.leds[i].value() == True:                    # Find current LED
                self.leds[i].value(False)                       # Turn off LED first
                self.leds[(i+1)%len(self.leds)].value(True)     # Turn on next LED, wrapping around if necessary
                return 0