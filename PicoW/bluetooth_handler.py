import bluetooth
from ble_simple_peripheral import BLESimplePeripheral

class Bluetooth:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Bluetooth, cls).__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def __init__(self):
        # Check if initialization has already been done to prevent reinitialization
        if not hasattr(self, 'BLEs'):
            self.BLEs       = BLESimplePeripheral(bluetooth.BLE())

    def send_bt_message(self, *args, **kwargs):
        self.BLEs.send(*args, **kwargs)

    def on_write(self, callback):
        self._write_callback = callback