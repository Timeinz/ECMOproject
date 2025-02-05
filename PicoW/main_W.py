import coefficients
import temp_conv
import time
import tasks
from peripherals import Peripherals
from printhandler import PrintHandler
import queue as q

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

# initializing the task queue
task_queue = []

# Bluetooth callback function to handle the commands
def on_rx(data):
    ph.print("Data received: ", data)  # Print the received data
    
    if data == b'toggleafe\r\n': # Enqueue the command
        q.enqueue(Task(tasks.toggleafe, priority=3))
    
    elif data == b'toggle\r\n':
        q.enqueue(Task(tasks.toggle, priority=3))
    
    elif data == b'mainstart\r\n':
        q.enqueue(Task(tasks.mainstart, priority=2))
    
    elif data == b'mainstop\r\n':
        q.enqueue(Task(tasks.mainstop, priority=2))


#setup calibration coefficients for each ADC channel
chan = []
for i in range(0, 8):
    chan.append(temp_conv.channel_cal(coefficients.channel[i][0], coefficients.channel[i][1]))


# set up the bluetooth receive message callback.
p.BLEs.on_write(on_rx)  # Set the callback function for data reception

# Start an infinite loop
while True:
    if p.ADC.flag:
        p.ADC.flag = False
        q.enqueue(Task(tasks.readADC, priority=1))
       
    now = time.ticks_ms()    
    try:
        task = q.dequeue()
        ph.print(task.func.__name__)
        task.func()
    except Exception as e:
        ph.print(e)
    if time.ticks_ms() - now > 1000: # notification to debug slow tasks
        ph.print("timeout\n")
