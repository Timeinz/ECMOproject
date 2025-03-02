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
    AFE_state = p.PWR_AFE.value()
    p.PWR_AFE.value(not AFE_state)  # Toggle the AFE state (on/off)
    ph.print("AFE:"+str(AFE_state))

def toggle():
    p.led.value(not p.led.value())  # Toggle the LED state (on/off)

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

def togglephrepl():
    ph.repl_set_enable(not ph.repl_is_enabled())

def togglephbt():
    ph.bt_set_enable(not ph.bt_is_enabled())

def slowtask():
    time.sleep_ms(3000)

def indon():
    p.timer.init(period=100, mode=Timer.PERIODIC, callback=blink_callback)

def indoff():
    p.timer.deinit()
    for led in p.leds:
        led.off()
    
def blink_callback(timer):                          # Timer callback function
    for i in range(len(p.leds)):
        if p.leds[i].value() == True:               # Find current LED
            p.leds[i].value(False)                  # Turn off LED first
            p.leds[(i+1)%len(p.leds)].value(True)   # Turn on next LED, wrapping around if necessary
            return 0

def initadc():
    try:
        if (p.ADC.ADS1256_init() != 0): 
            raise Exception()
        ph.print("Successfully connected to ADC")
        return 0
    except Exception as e:
        pass
    ph.print("Failed to connect to ADC")
    return None

def reboot():
    reset()

def gccollect():
    gc.collect()  # Call garbage collection