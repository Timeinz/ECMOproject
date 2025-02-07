from machine import Pin, Timer
import bluetooth
from ble_simple_peripheral import BLESimplePeripheral
import config
import ADS1256
from printhandler import PrintHandler as ph

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
            self.led = Pin("LED", Pin.OUT)
            self.led_state = False
            self.BLEs = BLESimplePeripheral(bluetooth.BLE())
            self.PWR_AFE = Pin(config.PWR_AFE, Pin.OUT)
            self.AFE_state = False
            self.DRDY = Pin(config.DRDY_PIN, Pin.IN, Pin.PULL_DOWN)
            self.ADC = ADS1256.ADS1256()
            self.IND0 = Pin(config.IND0, Pin.OUT)
            self.IND1 = Pin(config.IND1, Pin.OUT)
            self.IND2 = Pin(config.IND2, Pin.OUT)
            self.leds = [self.led, self.IND0, self.IND1, self.IND2] # Define the LED pins. The Pico has four on-board LEDs on GPIO pins 25, 22, 21, and 20.
            self.current_led = 0 # Keep track of which LED we're currently lighting up
            self.timer = Timer() # Setup the timer

    def led_on(self):
        self.led.on()

    def led_off(self):
        self.led.off()

    def send_bt_message(self, message):
        self.BLEs.send(message)

    def on_write(self, callback):
        self._write_callback = callback
    
    def DRDY_callback(self):
        self.ADC.flag = True
    
    def _init_ADC(self):
        try:
            #Initiate the digital pins; Initiate the ADS1256 module.
            if (config.module_init() != 0):
                raise Exception()
            if (self.ADC.ADS1256_init() != 0): 
                raise Exception()
            ph.print("Successfully connected to ADC")
            return 0
        except Exception as e:
            pass
        ph.print("Failed to connect to ADC")
        return None  # If all retries fail, return None or handle as needed
    
    # Timer callback function
    def blink_callback(self, timer):
        
        # Turn off LEDs first
        self.leds[self.current_led].off()
        
        # Move to the next LED, wrapping around to 0 if we've reached the end
        self.current_led = (self.current_led + 1) % len(self.leds)

        # Turn on the current LED
        self.leds[self.current_led].on()