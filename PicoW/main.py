import coefficients
import time
import tasks
from peripherals import Peripherals
from printhandler import PrintHandler
import queue as q
import machine

p = Peripherals()
ph = PrintHandler()


# Defining the task class which will be used to queue them
class Task:
    def __init__(self, func, priority, *args, **kwargs):
        self.func = func
        self.priority = priority
        self.args = args
        self.kwargs = kwargs
        self.last_run_time = 0  # For starvation prevention

# Bluetooth callback function to handle the commands
def on_rx(data):
    # Decode bytes to string and strip any leading/trailing whitespace or newlines
    data = data.decode().strip()

    # Split the string into function name and optionally priority
    parts = data.split()
    func_name = parts[0]
    priority = 3  # Default priority

    # If there's a second part, assume it's the priority
    if len(parts) > 1:
        try:
            priority = int(parts[1])
        except ValueError:
            # If conversion to int fails, keep the default priority
            ph.print(f"Warning: Invalid priority format. Using default priority.")

    try:
        # Get the function from the tasks module by its name
        func = getattr(tasks, func_name)
        
        # Print the received data with the priority
        ph.print(f"Data received: {func_name} (Priority: {priority})")
        
        # Enqueue a task with the function to call and the determined priority
        new_tasks.append(Task(func, priority=priority))
    except AttributeError:
        ph.print(f"Error: Function '{func_name}' not found in tasks module.")

# Make new_tasks global so it can be modified by callbacks
new_tasks = []

# set up the bluetooth receive message callback.
p.BLEs.on_write(on_rx)  # Set the callback function for data reception

# Start an infinite loop
while True:
    if p.ADC.flag:
        p.ADC.flag = False
        new_tasks.append(Task(tasks.read_adc_callback, priority=1))
       
    now = time.ticks_ms()

    try:
        # Create new_tasks list here, so it captures all tasks from interrupts
        current_tasks = new_tasks[:]  # Copy the current tasks to process
        new_tasks.clear()  # Clear the global list for the next cycle

        if current_tasks:  # Only manage if there are new tasks
            q.manage_queue(current_tasks)
        
        task = q.dequeue()
        if task is not None:
            ph.print(task.func.__name__)
            task.func(*task.args, **task.kwargs)  # Execute task with any provided arguments

    except Exception as e:
        ph.print(e)
    
    if time.ticks_ms() - now > 1000:  # notification to debug slow tasks
        ph.print("timeout")

    # Idle if there's nothing to do
    if not new_tasks and not q.task_queue and not p.ADC.flag:
        machine.idle()