from machine import Pin
import sdcard
import config
from ads1256 import ADS1256
from ds3231 import DS3231
from printhandler import PrintHandler
from communication import Communication

ph  = PrintHandler()
spi = Communication().spi
i2c = Communication().i2c


class Peripherals:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Peripherals, cls).__new__(cls)
        return cls._instance

    def __init__(self, debug=False):
        # Check if initialization has already been done to prevent reinitialization
        if not hasattr(self, 'log_text'):
            self.log_text = ""
            self.status = {}  # Dictionary to track peripheral status
            self.debug = debug
            
            # Initialize basic pins first
            try:
                self.led = Pin("LED", Pin.OUT)
                self.IND0 = Pin(config.IND0, Pin.OUT)
                self.IND1 = Pin(config.IND1, Pin.OUT)
                self.IND2 = Pin(config.IND2, Pin.OUT)
                self.leds = [self.led, self.IND0, self.IND1, self.IND2]
                self.PWR_AFE = Pin(config.PWR_AFE, Pin.OUT)
                self.PWR_AFE.value(1) # Powering the AFE
                self.SD_CS = Pin(config.SD_CS, Pin.OUT)
                self.SD_CS.value(1) # CS pin high = communication off
                self.ADC_CS = Pin(config.ADC_CS, Pin.OUT)
                self.ADC_CS.value(1) # CS pin high = communication off
                self.status["pins"] = "OK"
                self.log_text += "Pins OK\n"
                ph.print(self.log_text.splitlines()[-1])
            except Exception as e:
                self.status["pins"] = f"ERROR: {str(e)}"
                self.log_text += f"Pins failed: {str(e)}\n"
                ph.print(self.log_text.splitlines()[-1])
            
            # Initialize ADC
            try:
                self.ADC = ADS1256(spi, self.ADC_CS, baudrate=config.ADC_SPI_BAUDRATE, debug=self.debug)
                init_result = self.ADC.ADS1256_init()
                
                if init_result == 0:
                    self.status["ADC"] = "OK"
                    self.log_text += "ADC OK\n"
                elif init_result == -1:
                    self.status["ADC"] = "ERROR: ID Read failed"
                    self.log_text += "ADC failed: Chip ID verification failed\n"
                elif init_result == 1:
                    self.status["ADC"] = "ERROR: DRDY timeout"
                    self.log_text += "ADC failed: DRDY timeout\n"
                else:
                    self.status["ADC"] = f"ERROR: Unknown error code {init_result}"
                    self.log_text += f"ADC failed: Unknown error code {init_result}\n"
                ph.print(self.log_text.splitlines()[-1])
            except Exception as e:
                self.ADC = None
                self.status["ADC"] = f"ERROR: {str(e)}"
                self.log_text += f"ADC failed: {str(e)}\n"
                ph.print(self.log_text.splitlines()[-1])
            
            # Initialize SD card
            try:
                self.SD = sdcard.SDCard(spi, self.SD_CS, baudrate=config.SD_SPI_BAUDRATE, debug=self.debug)
                self.status["SD"] = "OK"
                self.log_text += "SD card OK\n"
                ph.print(self.log_text.splitlines()[-1])
            except OSError as e:
                self.SD = None
                error_msg = str(e)
                
                if "no SD card" in error_msg:
                    self.status["SD"] = "ERROR: No SD card detected"
                    self.log_text += "SD card failed: No SD card detected\n"
                elif "timeout waiting for v1 card" in error_msg:
                    self.status["SD"] = "ERROR: Timeout waiting for v1 card"
                    self.log_text += "SD card failed: Timeout waiting for v1 card\n"
                elif "timeout waiting for v2 card" in error_msg:
                    self.status["SD"] = "ERROR: Timeout waiting for v2 card"
                    self.log_text += "SD card failed: Timeout waiting for v2 card\n"
                elif "couldn't determine SD card version" in error_msg:
                    self.status["SD"] = "ERROR: Unknown SD card version"
                    self.log_text += "SD card failed: Couldn't determine SD card version\n"
                elif "SD card CSD format not supported" in error_msg:
                    self.status["SD"] = "ERROR: Unsupported CSD format"
                    self.log_text += "SD card failed: SD card CSD format not supported\n"
                elif "can't set 512 block size" in error_msg:
                    self.status["SD"] = "ERROR: Can't set block size"
                    self.log_text += "SD card failed: Can't set 512 block size\n"
                elif "timeout waiting for response" in error_msg:
                    self.status["SD"] = "ERROR: Card not responding"
                    self.log_text += "SD card failed: Timeout waiting for response\n"
                else:
                    self.status["SD"] = f"ERROR: {error_msg}"
                    self.log_text += f"SD card failed: {error_msg}\n"
                ph.print(self.log_text.splitlines()[-1])
            except Exception as e:
                self.SD = None
                self.status["SD"] = f"ERROR: {str(e)}"
                self.log_text += f"SD card failed: {str(e)}\n"
                ph.print(self.log_text.splitlines()[-1])
            
            # Initialize RTC
            try:
                self.RTC = DS3231(i2c, indicator=self.IND2)
                init_result = self.RTC.initialize()
                
                if init_result:
                    self.status["RTC"] = "OK"
                    self.log_text += "RTC OK\n"
                else:
                    if not self.RTC.is_live():
                        self.status["RTC"] = "ERROR: RTC not tracking time"
                        self.log_text += "RTC failed: RTC needs time synchronization (lost power or date not set)\n"
                    else:
                        self.status["RTC"] = "ERROR: RTC initialization failed"
                        self.log_text += "RTC failed: Unknown error\n"
                
                ph.print(self.log_text.splitlines()[-1])
            except OSError as e:
                self.RTC = None
                error_msg = str(e)
                self.status["RTC"] = f"ERROR: {error_msg}"
                self.log_text += f"RTC failed: {error_msg}\n"
                
                ph.print(self.log_text.splitlines()[-1])
            except Exception as e:
                self.RTC = None
                self.status["RTC"] = f"ERROR: {str(e)}"
                self.log_text += f"RTC failed: {str(e)}\n"
                ph.print(self.log_text.splitlines()[-1])
                
    def get_status(self):
        """Return the current status of all peripherals"""
        return self.status
    
    def get_log(self):
        """Return the initialization log"""
        return self.log_text

# Idea here to have a peripheral initiator, that deals with more complex setting ups of the peripherals, and tracks there status,
# all centrally in one spot, and can then be called from boot.py.