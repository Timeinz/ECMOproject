import asyncio
from bleak import BleakScanner, BleakClient



NAME = "ECMOSensor"

msg = "toggle"

commander = ''
notifier = ''

# Docu:
# first scan for BLE advertisements
# then select the device that matches our intended name
# then ask for its services


async def scan_ble_devices():
    global NAME, device, msg, commander, notifier
    try:
        device = await BleakScanner.find_device_by_name(NAME, timeout=5.0)
    except Exception as e:
        print(e)
        return
    if not device:
        print("Device not found")
        return
    async with BleakClient(device) as client:
        print(f"Connected to {device.address}")
        services = client.services
        print("Services:")
        for service in services:
            print(f"  {service}")
            for char in service.characteristics:
                print(f"  Characteristic: {char.uuid}, Properties: {char.properties}, Handle: {char.handle}")
                if "read" in char.properties:
                    try:
                        value = await client.read_gatt_char(char)
                        print(f"    Value: {value}")
                    except Exception as e:
                        print(f"    Failed to read: {e}")
                if "write-without-response" in char.properties:
                    commander = char.uuid
                    try:
                        await client.write_gatt_char(char.uuid, f"{msg}".encode())
                        print(f"Sent '{msg}' to Pico")
                    except Exception as e:
                        print(e)
                if "notify" in char.properties:
                    notifier = char
        
        print(f'notifier: {notifier.handle}')
        await client.start_notify(notifier.uuid, receive_notifications)
        print("Listening for notifications...")

        await client.write_gatt_char(commander, f"mainstart".encode())
        
        await asyncio.sleep(7)  # Wait for data
        

        await client.write_gatt_char(commander, f"mainstop".encode())
        await client.write_gatt_char(commander, f"{msg}".encode())
        await asyncio.sleep(1)  # Wait for data
        await client.write_gatt_char(commander, f"{msg}".encode())
        await asyncio.sleep(1)  # Wait for data
        await client.write_gatt_char(commander, f"{msg}".encode())

        await client.stop_notify(notifier)
        

'''

        await asyncio.sleep(1)  # Wait for data
        await client.write_gatt_char(commander, f"{msg}".encode())
        await asyncio.sleep(1)  # Wait for data
        await client.write_gatt_char(commander, f"{msg}".encode())
        await asyncio.sleep(5)  # Wait for data
'''


async def receive_notifications(client, data):
    print(f"Received: {data.decode().strip()}")



if __name__ == "__main__":
    asyncio.run(scan_ble_devices())
