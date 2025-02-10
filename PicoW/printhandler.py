from bluetooth_handler import Bluetooth

bt = Bluetooth()

class PrintHandler:
    _enabled = False  # Class variable to control if printing is active
    _bt_enabled = False

    @classmethod
    def set_console_enable(cls, state):
        """Enable or disable all console print operations."""
        cls._enabled = state

    @classmethod
    def set_bt_enable(cls, state):
        """Enable or disable all bluetooth print operations."""
        cls._bt_enabled = state

    @classmethod
    def is_enabled(cls):
        """Check if printing is currently enabled."""
        return cls._enabled

    @classmethod
    def bt_is_enabled(cls):
        """Check if printing is currently enabled."""
        return cls._bt_enabled

    @classmethod
    def print(cls, *args, **kwargs):
        """Print if enabled, otherwise do nothing."""
        if cls._enabled:
            print(*args, **kwargs)
        if cls._bt_enabled:
            # Convert args to string
            args_str = ' '.join(map(str, args))
            
            # Convert kwargs to string
            if kwargs:
                kwargs_str = ', '.join(f"{key}={value}" for key, value in kwargs.items())
                # Combine args and kwargs
                message = f"{args_str}: {kwargs_str}"
            else:
                message = args_str + '\n'
            bt.send_bt_message(message.encode('utf-8'))
