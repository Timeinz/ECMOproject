import json
import binascii


PSK = input('Enter PSK: ')


with open('psk.json', 'w') as f:
    json.dump({'key': binascii.hexlify(PSK).decode()}, f)

print('success')
