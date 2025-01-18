from machine import Pin, SPI

adcspi = SPI(0, baudrate = 1000000)
cspin = Pin(17, Pin.OUT)