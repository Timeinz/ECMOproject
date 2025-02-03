import time

task_queue = []

def enqueue(task):
    # Inserting into the queue while maintaining priority order
    task.last_run_time = time.ticks_ms()  # Update last run time for starvation check
    for i, t in enumerate(task_queue):
        if task.priority < t.priority:  # Higher priority means lower number
            task_queue.insert(i, task)
            return
    task_queue.append(task)

def dequeue():
    if task_queue:
        return task_queue.pop(0)  # Remove and return the highest priority task
    return None