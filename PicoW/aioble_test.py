import bluetooth
import aioble
import asyncio

# UUIDs
SERVICE_UUID = bluetooth.UUID("12345678-0000-1000-8000-00805f9b34fb")
CHAR1_UUID = bluetooth.UUID("11111111-0000-1000-8000-00805f9b34fb")
CHAR2_UUID = bluetooth.UUID("22222222-0000-1000-8000-00805f9b34fb")

# Define service and notify characteristics
service = aioble.Service(SERVICE_UUID)
notify_char1 = aioble.Characteristic(service, CHAR1_UUID, notify=True)
notify_char2 = aioble.Characteristic(service, CHAR2_UUID, notify=True)
aioble.register_services(service)

async def send_notifications():
    print("Advertising...")
    async with await aioble.advertise(self, name="DualNotify", services=[service]) as conn:
        print("Connected!")
        while True:
            await notify_char1.notify(conn, b"Hello from CHAR 1")
            await asyncio.sleep(1)
            await notify_char2.notify(conn, b"Hello from CHAR 2")
            await asyncio.sleep(1)

asyncio.run(send_notifications())