import network
from time import sleep
import credentials
import webrepl

# Initialize WLAN in station mode
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Connect to Wi-Fi network
wlan.connect(credentials.ssid, credentials.password)

# Wait for connection
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    sleep(1)

# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])

import webrepl_setup
webrepl.start()