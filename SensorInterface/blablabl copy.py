import asyncio
from bleak import BleakScanner, BleakClient



NAME = "ECMOSensor"

msg = "toggle"

# Docu:
# first scan for BLE advertisements
# then select the device that matches our intended name
# then ask for its services


async def scan_ble_devices():
    global NAME, device, msg
    device = await BleakScanner.find_device_by_name(NAME, timeout=5.0)
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
                    try:
                        await client.write_gatt_char(char.uuid, f"{msg}".encode())
                        print(f"Sent '{msg}' to Pico")
                    except Exception as e:
                        print(e)
        #await client.disconnect()
        #print("Disconnected")
        


if __name__ == "__main__":
    asyncio.run(scan_ble_devices())
