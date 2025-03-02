from machine import Pin, SPI, I2C
import config
import bluetooth
from ble_simple_peripheral import BLESimplePeripheral

SPI_BAUDRATE    = 1920000
SPI_CONTROLLER  = 0
I2C_FREQ        = 400000
I2C_CONTROLLER  = 0

class Communication:
    _spi = None
    _i2c = None
    _ble = None

    @staticmethod
    def get_spi():
        if Communication._spi is None:
            Communication._spi = SPI(SPI_CONTROLLER,
                                  baudrate  = SPI_BAUDRATE,
                                  sck       = Pin(config.SCK_PIN),
                                  mosi      = Pin(config.MOSI_PIN),
                                  miso      = Pin(config.MISO_PIN))
        return Communication._spi
    
    @staticmethod
    def get_i2c():
        if Communication._i2c is None:
            Communication._i2c = I2C(I2C_CONTROLLER,
                                  scl   = Pin(config.I2C_SCL),
                                  sda   = Pin(config.I2C_SDA),
                                  freq  = I2C_FREQ)
        return Communication._i2c
    
    @staticmethod
    def get_ble():
        if Communication._ble is None:
            Communication._ble = BLESimplePeripheral(bluetooth.BLE())
        return Communication._ble
