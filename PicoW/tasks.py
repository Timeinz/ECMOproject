from machine import Pin
from peripherals import Peripherals

p = Peripherals()

def toggleafe():
    p.PWR_AFE.value(not p.AFE_state)  # Toggle the AFE state (on/off)
    p.AFE_state = not p.AFE_state  # Update the AFE state

def toggle():
    p.led.value(not p.led_state)  # Toggle the LED state (on/off)
    p.led_state = not p.led_state  # Update the LED state

def mainstart():
    # set the DRDY interrupt
    p.DRDY.irq(trigger=Pin.IRQ_RISING, handler=p.DRDY_callback)

def mainstop():
    # disable the DRDY interrupt
    p.DRDY.irq(trigger=Pin.IRQ_RISING, handler=None)

def read_adc_callback():
    raw = ADC.ADS1256_cycle_read()     #fetch raw data from ADC
    read = [time.ticks_ms()]           #initate read. (also take the time in ms)
    #read = ""
    
    for i in range(0, 8):              #convert ADC reading to temp using calibrattion coefficients
        read.append(chan[i].convert(raw[i]))