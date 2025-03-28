import time
import threading

class DeadlockDetector:
    def __init__(self, num_resources, num_threads):
        self.num_resources = num_resources
        self.num_threads = num_threads
        self.resource_status = [None] * num_resources  # None if resource is free
        self.thread_locks = [None] * num_threads  # Tracks lock each thread is holding
        self.waiting_threads = {i: set() for i in range(num_threads)}  # Threads waiting for a resource

    def request_resource(self, thread_id, resource_id):
        """Request a resource for a thread."""
        if self.resource_status[resource_id] is None:
            self.resource_status[resource_id] = thread_id
            self.thread_locks[thread_id] = resource_id
            print(f"Thread {thread_id} acquired resource {resource_id}.")
        else:
            # The resource is already taken, so wait for it
            self.waiting_threads[thread_id].add(resource_id)
            print(f"Thread {thread_id} is waiting for resource {resource_id}.")

    def release_resource(self, thread_id, resource_id):
        """Release a resource held by a thread."""
        if self.thread_locks[thread_id] == resource_id:
            self.resource_status[resource_id] = None
            self.thread_locks[thread_id] = None
            print(f"Thread {thread_id} released resource {resource_id}.")

    def check_deadlock(self):
        """Check for a cycle in the wait-for graph (deadlock)."""
        visited = [False] * self.num_threads
        rec_stack = [False] * self.num_threads

        def is_deadlock(thread_id):
            visited[thread_id] = True
            rec_stack[thread_id] = True

            # Check all threads waiting on this thread
            for resource in self.waiting_threads[thread_id]:
                for other_thread, other_resource in enumerate(self.thread_locks):
                    if other_thread != thread_id and other_resource == resource:
                        # Thread `other_thread` is holding the resource, so this thread is waiting
                        if not visited[other_thread] and is_deadlock(other_thread):
                            return True
                        elif rec_stack[other_thread]:
                            return True

            rec_stack[thread_id] = False
            return False

        for thread_id in range(self.num_threads):
            if not visited[thread_id] and is_deadlock(thread_id):
                print(f"Deadlock detected in thread {thread_id}.")
                return True
        return False

    def deadlock_prevention(self, timeout=5):
        """Implement deadlock prevention by using timeouts."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_deadlock():
                print("Deadlock detected, attempting to prevent it by terminating a thread.")
                # Here we will simulate the prevention by killing a thread (in real systems, we'd abort the thread or roll back)
                for thread_id in range(self.num_threads):
                    if self.thread_locks[thread_id] is not None:
                        self.release_resource(thread_id, self.thread_locks[thread_id])
                        print(f"Thread {thread_id} terminated to prevent deadlock.")
                        break
                return
            time.sleep(1)  # Sleep to reduce CPU usage

# Example Usage:
def example_thread_work(thread_id, detector):
    """Simulate some work where threads request resources."""
    print(f"Thread {thread_id} started working.")
    detector.request_resource(thread_id, 0)
    time.sleep(2)
    detector.request_resource(thread_id, 1)
    time.sleep(2)
    detector.release_resource(thread_id, 0)
    time.sleep(2)
    detector.release_resource(thread_id, 1)
    print(f"Thread {thread_id} finished work.")

# Creating detector for 3 resources and 3 threads
detector = DeadlockDetector(num_resources=3, num_threads=3)

# Creating threads
threads = []
for i in range(3):
    t = threading.Thread(target=example_thread_work, args=(i, detector))
    threads.append(t)
    t.start()

# Preventing deadlock in the system with a timeout prevention strategy
detector.deadlock_prevention(timeout=10)

# Waiting for threads to finish
for t in threads:
    t.join()
