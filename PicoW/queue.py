import time

task_queue = []

def manage_queue(tasks):
    """
    Adjust priority of existing tasks for starvation, add new tasks, and sort by priority.
    """
    now = time.ticks_ms()
    
    # Check starvation for existing tasks in the queue
    for task in task_queue:
        if now - task.last_run_time > 3000:  # Increase priority if task is older than 3 seconds
            task.priority -= 1
    
    # Add new tasks to the queue
    for task in tasks:
        task.last_run_time = now  # Set initial last run time for new tasks
    task_queue.extend(tasks)
    
    # Sort all tasks by priority (lower number means higher priority)
    task_queue.sort(key=lambda x: x.priority)

def dequeue():
    if task_queue:
        return task_queue.pop(0)  # Remove and return the highest priority task
    return None