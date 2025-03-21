# /*****************************************************************************
# * | File        :	  EPD_1in54.py
# * | Author      :   Waveshare team
# * | Function    :   Hardware underlying interface
# * | Info        :
# *----------------
# * |	This version:   V1.0
# * | Date        :   2019-01-24
# * | Info        :   
# ******************************************************************************/
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


#import spidev
import RPi.GPIO as GPIO
import time
from machine import SPI, Pin, SoftI2C
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

# hardware PINs
IND0 = 1
IND1 = 2
IND2 = 3
I2C_SDA = 4
I2C_SCL = 5
Heater_PWR = 6
meas_24V = 7
meas_12V = 8
meas_AFEBAT = 10
PWR_AFE = 11
ADC = 28
SD_Detect = 22
SD_CS = 21

# ADC Pin definition
RST_PIN        = 0  #it's not connected
CS_PIN       = 17
DRDY_PIN        = 20
PDWN_PIN = 0
# LCD Definition
I2C_ADDR = 0x27
totalRows = 2
totalColumns = 16
# SPI Bus (ADC module)
SCK_PIN = 18
MISO_PIN = 16
MOSI_PIN = 19
SPI_HZ = 1920000
# I2C Bus (LCD module)
#SCL_PIN = 27
#SDA_PIN = 26
I2C_FREQ = 500000

# SPI device, bus = 0, device = 0
spi = SPI(0,
          sck=Pin(SCK_PIN),
          mosi=Pin(MOSI_PIN),
          miso=Pin(MISO_PIN),
          baudrate=SPI_HZ,
          phase=1,
          polarity=0
          )
'''
i2c = SoftI2C(scl=Pin(SCL_PIN),
              sda=Pin(SDA_PIN),
              freq=I2C_FREQ
              )

lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)
lcd.clear()
print(i2c)
'''
print(str(spi))

def digital_write(pin, value):
    if (pin == CS_PIN):    #This will keep the ADC constantly selected, since no other devices are on the SPI bus
        return
    GPIO.output(pin, value)

def digital_read(pin):
    return GPIO.input(pin)

def delay_ms(delaytime):
    time.sleep(delaytime // 1000.0)

def spi_writebyte(data):
    spi.write(bytearray(data))
    
def spi_readbytes(reg):
    return spi.read(reg)
    

def module_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    #GPIO.setup(RST_PIN, GPIO.OUT)
    Pin(CS_PIN, Pin.OUT)
    Pin(PDWN_PIN, Pin.OUT)
    #GPIO.setup(DRDY_PIN, GPIO.IN)
    Pin(DRDY_PIN, Pin.IN)
    #GPIO.output(CS_PIN, GPIO.LOW) # Initialize CS Pin low
    Pin(CS_PIN).value(0)
    #GPIO.output(PDWN_PIN, GPIO.HIGH) # Initialize PDWN pin High
    Pin(PDWN_PIN).value(1)
    #delay_ms(35)
    #GPIO.setup(DRDY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #spi.max_speed_hz = 20000
    #spi.mode = 0b01
    return 0

### END OF FILE ###

