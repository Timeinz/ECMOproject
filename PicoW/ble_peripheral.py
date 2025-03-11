import bluetooth
import struct
from micropython import const
from machine import Pin
import time
from ble_constants import UUID_map, NAME

# Constants   
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_FLAG_READ = const(0x0002)
_FLAG_WRITE = const(0x0004)
_FLAG_NOTIFY = const(0x0010)

# Custom UUIDs
_SERVICE_UUID = bluetooth.UUID(UUID_map["Service"])
_CHAR_UUID = (bluetooth.UUID(UUID_map["Send_data"]), _FLAG_NOTIFY)
_CHAR_UUID = (bluetooth.UUID(UUID_map["Receive_CMD"]), _FLAG_WRITE)

# BLE Service
_BLE_SERVICE = (_SERVICE_UUID, (_CHAR_UUID,))

class BLEPeripheral:
    def __init__(self, ble, name=NAME):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle,),) = self._ble.gatts_register_services((_BLE_SERVICE,))
        self._connections = set()
        self._max_connections = 1  # Only one concurrent connection
        self._receive_callback = None
        self._payload = struct.pack("B", len(name)) + name.encode() + bytes(_SERVICE_UUID)
        self._advertise()
    

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            if len(self._connections) < self._max_connections:
                self._connections.add(conn_handle)
                self._ble.gap_advertise(None)  # Stop advertising
            else:
                pass
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            self._advertise()  # Restart advertising
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if self._receive_callback:
                self._receive_callback(value_handle, value)

    def _advertise(self):
        self._ble.gap_advertise(50000, adv_data=self._payload)

    def send(self, handle, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, handle, data)
    
    def set_callback(self, callback):
        self._receive_callback = callback