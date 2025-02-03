#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
import ADS1256
import sys
import config
import csv
import temp_conv
import coefficients
import machine
from machine import Pin

PWR_AFE = Pin(config.PWR_AFE, Pin.OUT)
PWR_AFE.value(1)

led = Pin("LED", Pin.OUT)

#Initiate the digital pins; Initiate the ADS1256 module.
ADC = ADS1256.ADS1256()
if (config.module_init() != 0):
    sys.exit()
if(ADC.ADS1256_init() != 0):
    sys.exit()


# Initiate the csv and give the name
#file_name = 'test.csv'
#csv.init_file(file_name)


#setup calibration coefficients for each ADC channel
chan = []
for i in range(0, 8):
    chan.append(temp_conv.channel_cal(coefficients.channel[i][0], coefficients.channel[i][1]))

led_state = 0
AFE_state = 0

def toggle_led():
    pass

# Define the interrupt handler function
def handle_interrupt(pin):
    print("Interrupt occurred on pin", pin)

# Set up the GPIO pin as input with pull-down resistor
DRDY = Pin(config.DRDY_PIN, Pin.IN, Pin.PULL_DOWN)

# Set up the interrupt
# Here, we're detecting a rising edge (when the button is pressed)
DRDY.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt)

# Main loop - this will keep the script running to detect interrupts
while True:
    time.sleep_ms(100)  # Small delay to reduce CPU usage

while(1):
    raw = ADC.ADS1256_cycle_read()     #fetch raw data from ADC
    read = [time.ticks_ms()]           #initate read. (also take the time in ms)
    #read = ""
    
    for i in range(0, 8):              #convert ADC reading to temp using calibrattion coefficients
        read.append(chan[i].convert(raw[i]))
    
    #read.extend(raw)                  #add raw data to read
    #csv.write_line(file_name, read)    #write the data (read) to the csv
    print(read) 

