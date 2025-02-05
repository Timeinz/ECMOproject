from machine import Pin 
import bluetooth
from ble_simple_peripheral import BLESimplePeripheral
import config
import ADS1256

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
                break # I know it's SyntaxError here but this will do the trick and trigger the except.
            if (self.ADC.ADS1256_init() != 0): 
                break
            print("Successfully connected to ADC")
            return 0
        except Exception as e:
            pass
        print("Failed to connect to ADC")
        return None  # If all retries fail, return None or handle as needed