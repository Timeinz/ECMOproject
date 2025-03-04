import network, os
from time import sleep
import credentials
from printhandler import PrintHandler
from peripherals import Peripherals

ph  = PrintHandler()
p   = Peripherals()

# Initialize WLAN in station mode
#wlan = network.WLAN(network.STA_IF)
#wlan.active(True)

ph.repl_set_enable(True)
ph.bt_set_enable(True)

# Mount the SD card at /sd
try:
    os.mount(p.SD, '/sd')
    ph.print("SD card mounted successfully!")
    ph.print(os.listdir('/sd'))  # List files on SD card
except Exception as e:
    ph.print("Error mounting SD card:", e)

try:
    is_live = p.RTC.initialize()
    ph.print("RTC connected successfully!")
    ph.print("RTC live status: " + str(is_live))
except Exception as e:
    ph.print("Error connecting to RTC:", e)

try:
    AFE_state = p.PWR_AFE.value()
    p.PWR_AFE.value(not AFE_state)  # Toggle the AFE state (on/off)
    ph.print("AFE:"+str(AFE_state))
except Exception as e:
    ph.print("Error powering AFE:", e)

try:
    if (p.ADC.ADS1256_init(p) != 0): 
        raise Exception()
    ph.print("Successfully connected to ADC")
except Exception as e:
    ph.print("Failed to connect to ADC")



'''
attempts = 10
while attempts > 0:
    
    # Connect to Wi-Fi network
    wlan.connect(credentials.ssid, credentials.password)
    
    # Wait for connection
    max_wait = 100
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        attempts -= 1
        print('network connection failed')
        #sleep(1)
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])
        wlan.ifconfig(('192.168.1.100', '255.255.255.0', '192.168.1.1', '8.8.8.8'))
        attempts = 0


import webrepl
#import webrepl_setup
webrepl.start()
'''