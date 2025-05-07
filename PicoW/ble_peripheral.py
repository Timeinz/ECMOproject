import bluetooth
import struct
from micropython import const
from ble_advertising import advertising_payload
from ble_constants import Char_UUID_map, NAME, Service_UUID

# we are assuming only one service

# Constants   
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_FLAG_READ = const(0x0002)
_FLAG_WRITE = const(0x0004)
_FLAG_NOTIFY = const(0x0010)


_chars = []
for char in Char_UUID_map:
    char_copy = char.copy()
    # Add flags based on designation
    if char_copy["designation"] == "Send_data":
        char_copy["flags"] = _FLAG_NOTIFY
    elif char_copy["designation"].startswith("Receive_"):
        char_copy["flags"] = _FLAG_WRITE
    else:
        char_copy["flags"] = _FLAG_READ
    _chars.append(char_copy)


# declaring the service.
_BLE_SERVICE = (bluetooth.UUID(Service_UUID), [(bluetooth.UUID(char["uuid"]), char["flags"]) for char in _chars])


class BLEPeripheral:
    def __init__(self, ble, name=NAME):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        self._handles = self._ble.gatts_register_services((_BLE_SERVICE,))[0]  # Get handles for first service
        self._handle_map = {h: {"designation": c["designation"], "uuid": c["uuid"]} for h, c in zip(self._handles, _chars)}
        self._designation_map = {c["designation"]: {"handle": h, "uuid": c["uuid"]} for h, c in zip(self._handles, _chars)}
        self._uuid_map = {c["uuid"]: {"handle": h, "designation": c["designation"]} for h, c in zip(self._handles, _chars)}
        self._connections = set()
        self._max_connections = 1  # Only one concurrent connection
        self._receive_callback = None
        self._payload = advertising_payload(name=name)
        self._advertise()
    

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            if len(self._connections) < self._max_connections:
                self._connections.add(conn_handle)
                #self._ble.gap_advertise(None)  # Stop advertising
            else:
                pass
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            #self._advertise()  # Restart advertising
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if self._receive_callback:
                self._receive_callback(value_handle, value)

    def _advertise(self):
        self._ble.gap_advertise(100000, adv_data=self._payload)

    def send(self, handle, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, handle, data)
    
    def set_callback(self, callback):
        self._receive_callback = callback