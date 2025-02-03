class Task:
    def __init__(self, func, priority, *args, **kwargs):
        self.func = func
        self.priority = priority
        self.args = args
        self.kwargs = kwargs
        self.last_run_time = 0  # For starvation prevention

