class PrintHandler:
    _enabled = False  # Class variable to control if printing is active

    @classmethod
    def set_enable(cls, state):
        """Enable or disable all print operations."""
        cls._enabled = state

    @classmethod
    def is_enabled(cls):
        """Check if printing is currently enabled."""
        return cls._enabled

    @classmethod
    def print(cls, *args, **kwargs):
        """Print if enabled, otherwise do nothing."""
        if cls._enabled:
            print(*args, **kwargs)