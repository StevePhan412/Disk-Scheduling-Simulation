import sys
import argparse
from typing import List, Callable, Optional, Union

##### Made by Trung Phan - 12530351#####

# Define a type alias for the disk scheduling algorithms.
Algorithm = Callable[[List[int], int, Optional[int]], int]

# Constants
NUM_CYLINDERS = 1024
SEEK_START_TIME = 1.0
SEEK_TIME_PER_CYLINDER = 0.15
SEEK_STOP_TIME = 1.0
ROTATIONAL_LATENCY = 4.2

# Define an argument parser to accept command-line parameters (Point 2)
parser = argparse.ArgumentParser(description='Disk Scheduling Simulation')
parser.add_argument('--algorithm', type=str, default=None,
                    help='Algorithm type (C-SCAN, SSTF, or FIFO)')
parser.add_argument('--queue_size', type=int, help='Queue size')
parser.add_argument('--file_name', type=str, help='Name of input file')
args = parser.parse_args()

# Function to calculate seek time based on starting and ending cylinder.


def seek_time(start: int, end: int) -> float:
    distance = abs(start - end)
    time = SEEK_START_TIME + distance * SEEK_TIME_PER_CYLINDER + SEEK_STOP_TIME
    return time + ROTATIONAL_LATENCY

# C-SCAN disk scheduling algorithm implementation.


def c_scan(queue: List[dict], current_cylinder: int, new_request: Optional[dict]) -> Optional[tuple]:
    if new_request is not None:
        queue.append(new_request)
    if not queue:
        return None
    queue.sort(key=lambda x: x['cylinder'])
    idx = 0
    for i, request in enumerate(queue):
        if request['cylinder'] >= current_cylinder:
            idx = i
            break
    else:
        # Include seek time for moving head from the end to the start of the disk.
        seek_to_end = calculate_seek_time(current_cylinder, NUM_CYLINDERS - 1)
        seek_to_start = calculate_seek_time(NUM_CYLINDERS - 1, 0)
        next_cylinder = queue.pop(0)
        next_cylinder['accumulated_time'] += seek_to_end + seek_to_start
        return (next_cylinder, seek_to_end + seek_to_start + calculate_seek_time(0, next_cylinder['cylinder']))
    next_cylinder = queue.pop(idx)
    calculated_seek_time = calculate_seek_time(
        current_cylinder, next_cylinder['cylinder'])
    next_cylinder['accumulated_time'] += calculated_seek_time
    return (next_cylinder, calculated_seek_time)

# SSTF (Shortest Seek Time First) disk scheduling algorithm implementation.


def sstf(queue: List[dict], current_cylinder: int, new_request: Optional[dict]) -> Optional[tuple]:
    if new_request is not None:
        queue.append(new_request)
    if not queue:
        return None
    # Find the request with the shortest seek time from the current cylinder.
    closest = min(queue, key=lambda x: abs(x['cylinder'] - current_cylinder))
    queue.remove(closest)
    calculated_seek_time = calculate_seek_time(
        current_cylinder, closest['cylinder'])
    closest['accumulated_time'] += calculated_seek_time
    return (closest, calculated_seek_time)

# FIFO disk scheduling algorithm implementation.


def fifo(queue: List[dict], current_cylinder: int, new_request: Optional[dict]) -> int:
    if new_request is not None:
        queue.append(new_request)
    next_cylinder = queue.pop(0)  # Dequeue the first request in the queue
    # Extract the cylinder number
    next_cylinder_number = next_cylinder['cylinder']
    calculated_seek_time = calculate_seek_time(
        current_cylinder, next_cylinder_number)
    next_cylinder['accumulated_time'] += calculated_seek_time
    return (next_cylinder, calculated_seek_time)

# Function to read input data from the file and return it as a list of integers.


def read_data(file_name: str) -> List[int]:
    with open(file_name, 'r') as file:
        data = [int(line.strip()) for line in file.readlines()]
    return data

# Function to calculate seek time based on starting and ending cylinder (similar to seek_time).


def calculate_seek_time(start_cylinder: int, end_cylinder: int) -> float:
    distance = abs(start_cylinder - end_cylinder)
    time = 1 + (distance * 0.15) + 1
    latency = 4.2
    total_time = time + latency
    return total_time

# Function to simulate disk scheduling algorithms.


def simulate(algorithm: Algorithm, queue_size: int, data: List[int], current_cylinder: int) -> float:
    total_time = 0
    grand_total = 0
    queue: List[dict] = []
    for i, request in enumerate(data):
        new_request = {'cylinder': request, 'accumulated_time': 0}
        if len(queue) >= queue_size:
            result = algorithm(queue, current_cylinder, None)
            if result is not None:
                next_cylinder, seek_time = result
                total_time += seek_time
                current_cylinder = next_cylinder['cylinder']
                grand_total += next_cylinder['accumulated_time']
        queue.append(new_request)
        for item in queue:
            item['accumulated_time'] += total_time
        if i == len(data) - 1:
            while queue:
                result = algorithm(queue, current_cylinder, None)
                if result is not None:
                    next_cylinder, seek_time = result
                    total_time += seek_time
                    current_cylinder = next_cylinder['cylinder']
                    grand_total += next_cylinder['accumulated_time']
    # Calculate the average time using the grand total divided by the number of requests processed
    average_time = grand_total / len(data)
    return average_time

# Main function to run the disk scheduling simulation.


def main(file_name: str, queue_size: Optional[int] = None, algorithm_name: Optional[str] = None):
    data = read_data(file_name)  # Read input data from the file.
    # Get the initial current cylinder from the input data.
    current_cylinder = data.pop(0)

    # Define the algorithms to be simulated along with their names.
    all_algorithms = [(c_scan, "C-SCAN"), (sstf, "SSTF"), (fifo, "FIFO")]
    # Define the queue sizes to be tested.
    all_queue_sizes = [10, 20, 30, 40, 50]

    # Filter algorithms based on algorithm_name argument if provided
    algorithms_to_run = all_algorithms if algorithm_name is None else [
        algo for algo in all_algorithms if algo[1].upper() == algorithm_name.upper()]

    queue_sizes_to_run = all_queue_sizes if queue_size is None else [
        queue_size]

    for algorithm, algo_name in algorithms_to_run:
        print(f"Algorithm: {algo_name}")
        print("Queue Size, Average Time")
        for q_size in queue_sizes_to_run:
            # Simulate the algorithm for the provided queue size or all queue sizes
            average_time = simulate(
                algorithm, q_size, data, current_cylinder) / len(data)
            print(f" {q_size}, {average_time}")


# Accept an algorithm name or None
algorithm_name = args.algorithm if args.algorithm else None
file_name = args.file_name
# Accept a single queue size or None
queue_size = args.queue_size if args.queue_size else None
main(file_name, queue_size, algorithm_name)  # Updated calling pattern
