import asyncio
from bleak import BleakScanner, BleakClient

import numpy as np
import sys
from PyQt6.QtCore import pyqtSignal, QObject, QThread

import ast

from threading import Thread


NAME = "ECMOSensor"

commander = ''
notifier = ''

data_list = [[],[],[],[],[],[],[],[],[]]

# Docu:
# first scan for BLE advertisements
# then select the device that matches our intended name
# then ask for its services

class BLE_module(QObject):
    data_received = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.client = None
        self.loop = None

        self.window_length = 500

        self.thread = QThread()
        self.asyncio_thread = Thread(target=self.run_asyncio, daemon=True)

        self.moveToThread(self.thread)
        self.thread.started.connect(self.start_asyncio)
        self.thread.start()

    def start_asyncio(self):
        self.asyncio_thread.start()

    def run_asyncio(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.scan_ble_devices())

    async def scan_ble_devices(self):
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
            self.client = client
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
                    if "notify" in char.properties:
                        notifier = char
            
            print(f'notifier: {notifier.handle}')
            await client.start_notify(notifier.uuid, self.receive_notifications)
            print("Listening for notifications...")
            
            # Keep connection alive with non-blocking sleep
            while self.client.is_connected:
                await asyncio.sleep(0.1)  # Short sleep to yield control


    async def receive_notifications(self, x, data, throwaway=None):
        global data_list
        try:
            raw = ast.literal_eval(data.decode().strip())
            trim = min( len(data_list[0]) - self.window_length, 0)
            for i in range(len(data_list)):
                data_list[i].append(raw[i])
                del data_list[i][:trim]
            print(f"Received: {raw}")
            self.data_received.emit(data_list)
        except Exception as e:
            print(e)
    
    def send_message(self, msg):
        if self.client and self.loop:
            # Schedule write task in asyncio loop
            asyncio.run_coroutine_threadsafe(self.write_message(msg), self.loop)
        else:
            print("BLE not connected")

    async def write_message(self, msg):
        """Write data to BLE characteristic."""
        try:
            if self.client:
                await self.client.write_gatt_char(commander, f"{msg}".encode())
                print(f"Sent to BLE: {msg}")
        except Exception as e:
            print(f"Write error: {e}")

