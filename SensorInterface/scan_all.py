import asyncio
from bleak import BleakScanner, BleakClient



NAME = "ECMOSensor"

msg = "toggle"

# Docu:
# first scan for BLE advertisements
# then select the device that matches our intended name
# then ask for its services


async def scan():
    global NAME, device, msg
    scanner = BleakScanner()
    await scanner.start()
    await asyncio.sleep(5.0)
    await scanner.stop()
    for device in scanner.discovered_devices:
        print(f"{device.address}, {device.name or 'Unknown'}")

if __name__ == "__main__":
    asyncio.run(scan())