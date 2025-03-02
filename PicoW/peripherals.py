from machine import Pin
import sdcard
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
            self.RTC            = DS3231(i2c, indicator=self.IND2)

# Idea here to have a peripheral initiator, that deals with more copmlex setting ups of the peripherals, and tracks there status,
# all centrally in one spot, and can then be called from boot.py.