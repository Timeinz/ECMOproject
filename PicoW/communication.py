from machine import Pin, SPI, I2C
import bluetooth
from ble_peripheral import BLEPeripheral
import config


class Communication:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Communication, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._spi = None
            self._i2c = None
            self._ble = None
            self._spi_baudrate = 100000 # dummy values will be overwritten by the peripherals
            self._spi_phase = 0
            self._spi_polarity = 0
            self._status = {}
            self._log_text = ""
            self._initialize()
            self._initialized = True

    def _initialize(self):
        try:
            self._spi = SPI(config.SPI_CONTROLLER,
                            baudrate=self._spi_baudrate,
                            sck=Pin(config.SCK_PIN),
                            mosi=Pin(config.MOSI_PIN),
                            miso=Pin(config.MISO_PIN),
                            phase=self._spi_phase,
                            polarity=self._spi_polarity)
            self._status["SPI"] = "OK"
            self._log_text += "SPI OK\n"
        except Exception as e:
            self._status["SPI"] = f"ERROR: {e}"
            self._log_text += f"SPI failed: {e}\n"

        try:
            self._i2c = I2C(config.I2C_CONTROLLER,
                            scl=Pin(config.I2C_SCL),
                            sda=Pin(config.I2C_SDA),
                            freq=config.I2C_FREQ)
            self._status["I2C"] = "OK"
            self._log_text += "I2C OK\n"
        except Exception as e:
            self._status["I2C"] = f"ERROR: {e}"
            self._log_text += f"I2C failed: {e}\n"

        try:
            ble = bluetooth.BLE()
            ble.active(True)
            self._ble = BLEPeripheral(ble)
            self._status["BLE"] = "OK"
            self._log_text += "BLE OK\n"
        except Exception as e:
            self._status["BLE"] = f"ERROR: {e}"
            self._log_text += f"BLE failed: {e}\n"

    @property
    def spi(self):
        if self._spi is None:
            raise RuntimeError("SPI not initialized")
        return self._spi

    @property
    def spi_config(self): # Get the current SPI configuration parameters.
        return {
            "baudrate": self._spi_baudrate,  # Default from config
            "phase": self._spi_phase,  # Default used in initialization
            "polarity": self._spi_polarity  # Default used in initialization
        }
    
    @spi_config.setter
    def spi_config(self, params):
        """
        Set SPI configuration parameters without reinitializing.
        
        Args:
            params: dict with baudrate, phase, and/or polarity
        """
        # Simply store the configuration values for reference
        # This doesn't change the actual SPI configuration
        if "baudrate" in params:
            self._spi_baudrate = params["baudrate"]
        if "phase" in params:
            self._spi_phase = params["phase"]
        if "polarity" in params:
            self._spi_polarity = params["polarity"]

    @property
    def i2c(self):
        if self._i2c is None:
            raise RuntimeError("I2C not initialized")
        return self._i2c

    @property
    def ble(self):
        if self._ble is None:
            raise RuntimeError("BLE not initialized")
        return self._ble

    def get_status(self):
        return self._status

    def get_log(self):
        return self._log_text