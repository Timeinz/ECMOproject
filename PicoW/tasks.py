from machine import Pin, Timer, reset
from communication import Communication
from peripherals import Peripherals
from printhandler import PrintHandler
from datawriter import DataWriter
import datetime_conversion as dtc
import time
import gc


comm = Communication()
p = Peripherals()
ph = PrintHandler()
dw = DataWriter()
timer = Timer()

# Defining the task class which will be used to queue them
class Task:
    def __init__(self, func, priority=3, *args, **kwargs):
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
    p.ADC.trigger_set(True)

def mainstop():
    p.ADC.trigger_set(False)
    p.ADC.ditch1meas = True

def read_adc_callback():
    p.ADC.ADS1256_cycle_read()     # fetch raw data from ADC
    
    if p.ADC.read_flag:
        if p.ADC.ditch1meas:
            p.ADC.ditch1meas = False
        else:
            read = [dtc.to_human_int(p.RTC.read_datetime())]        # initate read. also take the time in ms, convert to human-readable int.
            read.extend(p.ADC.raw)
            
            #for i in range(p.ADC.num_of_chans):                  # convert ADC reading to temp using calibrattion coefficients
                #read.append(p.ADC.chan[i].convert(p.ADC.raw[i]))
                
            #dw.write_data(read)
            #ph.print(read)
            ph.send_data(read)

def togglephrepl():
    ph.repl_set_enable(not ph.repl_is_enabled())

def togglephbt():
    ph.bt_set_enable(not ph.bt_is_enabled())

def slowtask():
    time.sleep_ms(10)

def indon():
    timer.init(period=100, mode=Timer.PERIODIC, callback=blink_callback)

def indoff():
    timer.deinit()
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
        if (p.ADC.ADS1256_init(ph) != 0):
            raise Exception()
        ph.print("Successfully connected to ADC")
        return 0
    except Exception as e:
        pass
    ph.print("Failed to connect to ADC")
    return None

def reboot():
    reset()

def status_log():
    log = comm.get_log()
    return log

def gccollect():
    gc.collect()  # Call garbage collection

def send_status_log():
    ph.print(p.log_text)