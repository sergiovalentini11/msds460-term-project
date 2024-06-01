from simpy import *
from functools import partial
import numpy as np
import random
import time
from queue import * # add FIFO queue data structure


# Define customer class with attributes
class Customer:
    def __init__(self, arrival_time, order_size, is_takeout):
        self.arrival_time = arrival_time
        self.order_size = order_size
        self.is_takeout = is_takeout
        self.wait_start = None  # Initialize wait start time

# Define events for simulation flow
def arrival(env, customers, queue, order_point, kitchen, tables, arrival_rate):
    while True:
        yield env.timeout(random.expovariate(arrival_rate))
        customer = Customer(env.now, random.randint(1, 3), random.choice([True, False]))
        customers.append(customer)
        if customer.is_takeout:
            queue.append(customer)
            yield env.process(order(env, customer, order_point))
        else:
            if len(tables) < 200:
                tables.append(customer)
                customer.wait_start = env.now
                yield env.process(order(env, customer, order_point))
            else:
                print(f"Customer arrived at {env.now:.2f} (dine-in) but left due to no tables")

def order(env, customer, order_point):
    yield env.timeout(random.expovariate(1/service_rate))
    yield order_point.put(customer)

def kitchen(env, order_point, cook_time, stations):
    while True:
        customer = yield order_point.get()
        available_stations = stations - len(env.process(kitchen))
        if available_stations > 0:
            yield env.timeout(cook_time * customer.order_size)
            if not customer.is_takeout:
                tables.remove(customer)
            customer.wait_time = env.now - customer.wait_start if customer.wait_start else 0
        else:
            yield kitchen(env, order_point, cook_time, stations)

def run_simulation(env, duration, arrival_rate, service_rate, cook_time):
    customers = []
    queue = Queue(env)
    order_point = Buffer(env, capacity=10)
    tables = []
    kitchen_stations = 15
    env.process(arrival(env, customers, queue, order_point, partial(kitchen, cook_time=cook_time, stations=kitchen_stations), tables, arrival_rate))
    start_time = time.time()
    env.run(duration)
    end_time = time.time()
    total_wait_time = sum(customer.wait_time for customer in customers if customer.wait_time)
    average_wait_time = total_wait_time / len(customers) if customers else 0
    return average_wait_time, len([c for c in customers if not c.is_takeout and not c.wait_start]), end_time - start_time

# Set parameters for benchmarking
num_simulations = 100
arrival_rate = 2
service_rate = 5
cook_time = 2
duration = 120


# Perform benchmarking
python_execution_times = []
for _ in range(num_simulations):
    env = Environment()
    _, _, execution_time = run_simulation(env, duration, arrival_rate, service_rate, cook_time)
    python_execution_times.append(execution_time)

# Calculate average execution time
average_python_execution_time = sum(python_execution_times) / len(python_execution_times)
print(f"Average execution time for Python simulation (over {num_simulations} simulations): {average_python_execution_time:.4f} seconds")