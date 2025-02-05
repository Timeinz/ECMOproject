import time

task_queue = []

def enqueue(task):
    # Inserting into the queue while maintaining priority order
    now = time.ticks_ms()
    task.last_run_time = now  # Update last run time for starvation check
    for i, t in enumerate(task_queue):
        if now - t.last_run_time > 3000: # increase priority if task is older than 3 seconds
            t.priority -= 1
        if task.priority < t.priority:  # Higher priority means lower number
            task_queue.insert(i, task)
    task_queue.append(task)

def dequeue():
    if task_queue:
        return task_queue.pop(0)  # Remove and return the highest priority task
    return None