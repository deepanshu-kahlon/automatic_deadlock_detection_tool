import time
import threading

class BankersAlgorithm:
    def __init__(self, num_resources, num_threads):
        self.num_resources = num_resources
        self.num_threads = num_threads
        self.available = [3] * num_resources  # Available resources
        self.max = [[7, 5, 3], [3, 2, 2], [9, 0, 2]]  # Maximum resources needed by each thread
        self.allocation = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]  # Resources currently allocated
        self.need = self.calculate_need()  # Remaining needs of resources

    def calculate_need(self):
        """Calculate remaining resource needs (Max - Allocation)."""
        need = []
        for i in range(self.num_threads):
            row = [self.max[i][j] - self.allocation[i][j] for j in range(self.num_resources)]
            need.append(row)
        return need

    def is_safe(self):
        """Check if the system is in a safe state using the Banker's Algorithm."""
        work = self.available[:]  # Work is a copy of available resources
        finish = [False] * self.num_threads  # Track finished threads
        safe_sequence = []

        while len(safe_sequence) < self.num_threads:
            progress = False
            for i in range(self.num_threads):
                if not finish[i] and all(self.need[i][j] <= work[j] for j in range(self.num_resources)):
                    # This thread can finish because its needs are less than or equal to available resources
                    safe_sequence.append(i)
                    finish[i] = True
                    # Simulate the thread releasing its resources
                    for j in range(self.num_resources):
                        work[j] += self.allocation[i][j]
                    progress = True
                    break

            if not progress:
                # If no thread can progress, then the system is not in a safe state
                return False, safe_sequence

        return True, safe_sequence

    def request_resources(self, thread_id, request):
        """Request resources for a thread."""
        # Check if the request is valid (i.e., not exceeding the need)
        if any(request[i] > self.need[thread_id][i] for i in range(self.num_resources)):
            print(f"Thread {thread_id} made an invalid request.")
            return False

        # Check if resources are available
        if any(request[i] > self.available[i] for i in range(self.num_resources)):
            print(f"Thread {thread_id} is waiting for resources.")
            return False

        # Pretend to allocate resources and check if the system remains in a safe state
        original_available = self.available[:]
        original_allocation = self.allocation[:]
        original_need = self.need[:]

        # Allocate resources
        for i in range(self.num_resources):
            self.available[i] -= request[i]
            self.allocation[thread_id][i] += request[i]
            self.need[thread_id][i] -= request[i]

        safe, safe_sequence = self.is_safe()

        if not safe:
            # Rollback allocation since it leads to an unsafe state
            self.available = original_available
            self.allocation = original_allocation
            self.need = original_need
            print(f"Thread {thread_id}'s request leads to an unsafe state, denied.")
            return False

        print(f"Thread {thread_id}'s request granted. Safe sequence: {safe_sequence}")
        return True

    def release_resources(self, thread_id, release):
        """Release resources held by a thread."""
        for i in range(self.num_resources):
            self.available[i] += release[i]
            self.allocation[thread_id][i] -= release[i]
            self.need[thread_id][i] += release[i]
        print(f"Thread {thread_id} released resources: {release}.")

# Example Usage:
def example_thread_work(thread_id, banker):
    """Simulate some work where threads request resources."""
    print(f"Thread {thread_id} started working.")
    
    # Request resources for this thread
    request = [1, 0, 2]  # Example request (can be changed based on resources)
    if banker.request_resources(thread_id, request):
        time.sleep(2)
        # After doing some work, release resources
        banker.release_resources(thread_id, request)
    else:
        print(f"Thread {thread_id} could not get resources.")

# Create Banker's Algorithm for 3 resources and 3 threads
banker = BankersAlgorithm(num_resources=3, num_threads=3)

# Creating threads
threads = []
for i in range(3):
    t = threading.Thread(target=example_thread_work, args=(i, banker))
    threads.append(t)
    t.start()

# Wait for threads to finish
for t in threads:
    t.join()
