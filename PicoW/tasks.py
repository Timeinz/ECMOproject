from machine import Pin, Timer, reset
from peripherals import Peripherals
from printhandler import PrintHandler as ph
import time
import gc

p = Peripherals()

# Defining the task class which will be used to queue them
class Task:
    def __init__(self, func, priority, *args, **kwargs):
        self.func = func
        self.priority = priority
        self.args = args
        self.kwargs = kwargs
        self.last_run_time = 0  # For starvation prevention

def toggleafe():
    p.PWR_AFE.value(not p.AFE_state)  # Toggle the AFE state (on/off)
    p.AFE_state = not p.AFE_state  # Update the AFE state
    ph.print("AFE:"+str(p.AFE_state))

def toggle():
    p.led.value(not p.led_state)  # Toggle the LED state (on/off)
    p.led_state = not p.led_state  # Update the LED state

def mainstart():
    # set the DRDY interrupt
    p.ADC.DRDY.irq(trigger=Pin.IRQ_FALLING, handler=p.ADC.DRDY_callback)

def mainstop():
    # disable the DRDY interrupt
    p.ADC.DRDY.irq(handler=None)
    p.IND0.off()

def read_adc_callback():
    p.ADC.ADS1256_cycle_read()     #fetch raw data from ADC
    
    if p.ADC.read_flag:
        #read = [time.ticks_ms()]           #initate read. (also take the time in ms)
        #for i in range(0, p.ADC.num_of_chans):              #convert ADC reading to temp using calibrattion coefficients
            #read.append(p.ADC.chan[i].convert(p.ADC.raw[i]))
            #ph.print(p.ADC.raw)
            #read.append(p.ADC.raw[i])
        #ph.print(read)
        ph.print(p.ADC.raw)

def toggleph():
    ph.set_console_enable(not ph.is_enabled())

def togglebtph():
    ph.set_bt_enable(not ph.bt_is_enabled())

def slowtask():
    time.sleep_ms(3000)

def indon():
    p.timer.init(period=100, mode=Timer.PERIODIC, callback=p.blink_callback)

def indoff():
    p.timer.deinit()
    for led in p.leds:
        led.off()

def initadc():
    p._init_ADC()

def reboot():
    reset()

def gccollect():
    gc.collect()  # Call garbage collection