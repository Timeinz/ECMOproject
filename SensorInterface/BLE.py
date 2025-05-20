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
    notification_print = pyqtSignal(str, bool) # message to print, bool coming from pico?

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
        self.loop.create_task(self.loop_connect())
        self.loop.run_forever()

    async def loop_connect(self):
        while True:
            await self.ble_connection()
            await asyncio.sleep(1)

    async def ble_connection(self):
        global NAME, device, msg, commander, notifier
        try:
            device = await BleakScanner.find_device_by_name(NAME, timeout=5.0)
        except Exception as e:
            self.notification_printer(e)
            return
        if not device:
            self.notification_printer("Device not found")
            return
        async with BleakClient(device) as client:
            self.client = client
            self.notification_printer(f"Connected to {device.address}")
            services = client.services
            self.notification_printer("Services:")
            for service in services:
                self.notification_printer(f"  {service}")
                for char in service.characteristics:
                    self.notification_printer(f"  Characteristic: {char.uuid}, Properties: {char.properties}, Handle: {char.handle}")
                    if "read" in char.properties:
                        try:
                            value = await client.read_gatt_char(char)
                            self.notification_printer(f"    Value: {value}")
                        except Exception as e:
                            self.notification_printer(f"    Failed to read: {e}")
                    if "write-without-response" in char.properties:
                        commander = char.uuid
                    if "notify" in char.properties:
                        notifier = char
            
            self.notification_printer(f'notifier: {notifier.handle}')
            await client.start_notify(notifier.uuid, self.receive_notifications)
            self.notification_printer("Listening for notifications...")
            
            # Keep connection alive with non-blocking sleep
            while self.client.is_connected:
                await asyncio.sleep(0.01)  # Short sleep to yield control


    async def receive_notifications(self, x, data, throwaway=None):
        global data_list
        try:
            raw = ast.literal_eval(data.decode().strip())
            trim = min( len(data_list[0]) - self.window_length, 0)
            for i in range(len(data_list)):
                data_list[i].append(raw[i])
                del data_list[i][:trim]
            #self.notification_printer(f"Received: {raw}")
            self.data_received.emit(data_list)
        except Exception as e:
            self.notification_printer(e)
    
    def send_message(self, msg):
        if self.client and self.loop:
            # Schedule write task in asyncio loop
            asyncio.run_coroutine_threadsafe(self.write_message(msg), self.loop)
        else:
            self.notification_printer("BLE not connected")

    async def write_message(self, msg):
        """Write data to BLE characteristic."""
        try:
            if self.client:
                await self.client.write_gatt_char(commander, f"{msg}".encode())
                self.notification_printer(f"Sent to BLE: {msg}")
        except Exception as e:
            self.notification_printer(f"Write error: {e}")

    def notification_printer(self, message, remote=False):
        self.notification_print.emit(message, remote)
