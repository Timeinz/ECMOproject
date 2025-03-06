from communication import Communication

bt = Communication().ble

class PrintHandler:
    _repl_enabled = False  # Class variable to control if printing is active
    _bt_enabled = False


    @classmethod
    def repl_set_enable(cls, state):
        """Enable or disable all console print operations."""
        cls._repl_enabled = state

    @classmethod
    def bt_set_enable(cls, state):
        """Enable or disable all bluetooth print operations."""
        cls._bt_enabled = state

    @classmethod
    def repl_is_enabled(cls):
        """Check if printing is currently enabled."""
        return cls._repl_enabled

    @classmethod
    def bt_is_enabled(cls):
        """Check if printing is currently enabled."""
        return cls._bt_enabled

    @classmethod
    def print(cls, *args, **kwargs):
        """Print if enabled, otherwise do nothing."""
        if cls._repl_enabled:
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
                
            if bt is not None:
                bt.send(message.encode('utf-8'))
