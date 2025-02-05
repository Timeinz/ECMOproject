import network
from time import sleep
import credentials
from printhandler import PrintHandler

# Initialize WLAN in station mode
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

ph = PrintHandler()
ph.set_enable(True)

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