import time
import tasks
from tasks import Task
from peripherals import Peripherals
from printhandler import PrintHandler as ph
from communication import Communication
import queue as q
import machine
import gc

p = Peripherals()
bt = Communication().ble


# Make new_tasks global so it can be modified by callbacks
new_tasks = []


# Bluetooth callback function to handle the commands

# this is an extension of the BLE IRQ_GATTS_WRITE handler.
# the core handler is independently outlined in the BLE driver (ble_peripheral in this case).
# the handler in the core driver file is meant to only do low-level generic BLE stuff,
# while the high-level part of the interrupt is meant to handle application specific things
# like inserting things into the task queue or reading from different characteristics and
# handling things differently dependent on this.
def ble_receive(handle, data):

    # if handle == characteristic uuid of the handle according to the lookup table only then do the following ? (specific handler for application commands)

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

bt.set_callback(ble_receive)

# Define the timer interrupt callback function
def gc_collect_callback(timer):
    pass
    #ph.print(gc.mem_free()) # print available memory
    #gc.collect()  # Call garbage collection

# Set up the timer for an interrupt every second
timer = machine.Timer(-1)  # -1 means use the next available hardware timer
timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=gc_collect_callback)

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
            #ph.print(task.func.__name__)
            task.func(*task.args, **task.kwargs)  # Execute task with any provided arguments

    except Exception as e:
        ph.print(e)
    
    if time.ticks_ms() - now > 1000:  # notification to debug slow tasks
        ph.print("overtime")
    
    # Idle if there's nothing to do
    #if not new_tasks and not q.task_queue: #and not p.ADC.flag:
        #machine.idle()
    #machine.idle() doesn't seem to be working ...
    #gc.collect()
    time.sleep_ms(1)
