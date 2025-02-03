# Import necessary modules
import coefficients
import temp_conv
import time
import tasks
from peripherals import Peripherals

p = Peripherals()


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

# enqueuing tasks
def enqueue(task):
    # Inserting into the queue while maintaining priority order
    task.last_run_time = time.ticks_ms()  # Update last run time for starvation check
    for i, t in enumerate(task_queue):
        if task.priority < t.priority:  # Higher priority means lower number
            task_queue.insert(i, task)
            return
    task_queue.append(task)

# pulling the next task from queue
def dequeue():
    if task_queue:
        return task_queue.pop(0)  # Remove and return the highest priority task
    return None


# Bluetooth callback function to handle the commands
def on_rx(data):
    print("Data received: ", data)  # Print the received data
    
    if data == b'toggleafe\r\n': # Enqueue the command
        enqueue(Task(tasks.toggleafe, priority=3))
    
    elif data == b'toggle\r\n':
        enqueue(Task(tasks.toggle, priority=3))
    
    elif data == b'mainstart\r\n':
        enqueue(Task(tasks.mainstart, priority=2))
    
    elif data == b'mainstop\r\n':
        enqueue(Task(tasks.mainstop, priority=2))



'''
    
    #read.extend(raw)                  #add raw data to read
    #csv.write_line(file_name, read)    #write the data (read) to the csv
    print(read) 
next_chan = 1
read = []
def ADS1256_cycle_read(self):
        global next_chan, read
        num_of_chans = 8
        if next_chan == 1:
            read = [time.ticks_ms()]
        #ADC.ADS1256_WaitDRDY()
        if (next_chan == num_of_chans):
            ADC.ADS1256_SetChannel(8, 0)
            next_chan = 0
        else:
            ADC.ADS1256_SetChannel(8, next_chan)
        config.spi_writebyte([ADS1256.CMD['CMD_SYNC'],
                                ADS1256.CMD['CMD_WAKEUP'],
                                ADS1256.CMD['CMD_RDATA']
                                ])
        read.append(chan[next_chan - 1].convert(ADC.ADS1256_Read_ADC_Data()))
        next_chan += 1
        if next_chan == 1:
            print(read)
        return

'''


# Initiate the csv and give the name
#file_name = 'test.csv'
#csv.init_file(file_name)


#setup calibration coefficients for each ADC channel
chan = []
for i in range(0, 8):
    chan.append(temp_conv.channel_cal(coefficients.channel[i][0], coefficients.channel[i][1]))


# set up the bluetooth receive message callback.
p.BLEs.on_write(on_rx)  # Set the callback function for data reception

# Start an infinite loop
while True:
    time.sleep_ms(100) 