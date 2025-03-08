import asyncio
from bleak import BleakClient

CUSTOM_SERVICE_UUID = "12345678-1234-5678-1234-567812345678"
CUSTOM_CHAR_UUID = "87654321-4321-8765-4321-876543210987"

async def run_client():
    # Replace with your device's address
    address = "XX:XX:XX:XX:XX:XX"
    async with BleakClient(address) as client:
        print("Connected!")
        # Read from custom characteristic
        data = await client.read_gatt_char(CUSTOM_CHAR_UUID)
        print(f"Received: {data.hex()}")
        # Write to custom characteristic
        await client.write_gatt_char(CUSTOM_CHAR_UUID, b"\xCA\xFE\xBA\xBE")
        print("Wrote custom data")

asyncio.run(run_client())