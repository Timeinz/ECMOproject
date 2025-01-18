#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
import ADS1256
import RPi.GPIO as GPIO
import sys
import config
from machine import Pin


ADC = ADS1256.ADS1256()
for i in range(0, 10):
    if (ADC.ADS1256_init() != 0):
        GPIO.output(config.PDWN_PIN, GPIO.LOW) # Initialize PDWN pin High
        time.sleep(1)
        GPIO.output(config.PDWN_PIN, GPIO.HIGH) # Initialize PDWN pin High
        ADC.ADS1256_reset()
    else:
        break
    #sys.exit()

while (1):
    read = []
    read.append(time.ticks_us())
    read.append(ADC.ADS1256_cycle_read())
    print(read)

while(1):
    for i in range(0, 20):
        read = []
        read.append(time.ticks_us())
        read.append(ADC.ADS1256_cycle_read())
        print(read)
    config.lcd.move_to(0,1)
    config.lcd.putstr(str(read[0]))
    config.lcd.move_to(9,1)
    config.lcd.putstr(str(read[1][1]))


pos_chan = [[0, 0], [8, 0], [0, 1], [8, 1]]

#config.lcd.move_to(pos_chan[chan][0], pos_chan[chan][1])
#config.lcd.putstr(str(read[chan]))


'''

interrupt = Pin(20)
interrupt_flag = 0
stop = 0

def callback(interrupt):
    global interrupt_flag
    interrupt_flag = 1

interrupt.irq(trigger=Pin.IRQ_FALLING, handler=callback)
config.spi_writebyte([0x03])


try:
    while(1):
        if(interrupt_flag == 1):
            ADC.interrupt_routine()
            interrupt_flag = 0
    
except:
        
    
    GPIO.output(config.PDWN_PIN, GPIO.LOW) # Pull RST Pin low for Power off
    #interrupt.irq(handler=None)
    print (print("stopping data read.\nGoodbye!"))



while(1):
    ADC_Value = ADC.ADS1256_GetAll()
    #print(ADC_Value)
    print ("0 ADC = %f"%(ADC_Value[0]*5.0/0x7fffff))
    print ("1 ADC = %f"%(ADC_Value[1]*5.0/0x7fffff))
    print ("2 ADC = %f"%(ADC_Value[2]*5.0/0x7fffff))
    print ("3 ADC = %f"%(ADC_Value[3]*5.0/0x7fffff))
    print ("4 ADC = %f"%(ADC_Value[4]*5.0/0x7fffff))
    print ("5 ADC = %f"%(ADC_Value[5]*5.0/0x7fffff))
    print ("6 ADC = %f"%(ADC_Value[6]*5.0/0x7fffff))
    print ("7 ADC = %f"%(ADC_Value[7]*5.0/0x7fffff))
    print ("\33[9A")
    config.delay_ms(1500)
    '''
