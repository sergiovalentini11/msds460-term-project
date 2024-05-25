"""
Created on Sat May 11 20:55:30 2024

@author: nikitasharma
"""

from simpy import *

# Define customer class with attributes
class Customer:
  def __init__(self, arrival_time, order_size, is_takeout):
    self.arrival_time = arrival_time
    self.order_size = order_size
    self.is_takeout = is_takeout
    self.wait_start = None  # Initialize wait start time

# Define events for simulation flow
def arrival(env, customers, queue, order_point, kitchen, tables):
  while True:
    yield arrival_time(env)  # Generate inter-arrival time
    customer = Customer(env.now, random.randint(1, 3), random.choice([True, False]))  # Decide on dine-in/takeout
    customers.append(customer)
    if customer.is_takeout:
      queue.append(customer)  # Takeout orders go straight to kitchen queue
      yield env.process(order(env, customer, order_point))
    else:
      # Dine-in: Check for available table
      if len(tables) < 200:  # Maximum capacity (50 tables * 4 chairs)
        tables.append(customer)
        customer.wait_start = env.now  # Start wait time for dine-in
        yield env.process(order(env, customer, order_point))
      else:
        # Table full, customer leaves
        print(f"Customer arrived at {env.now:.2f} (dine-in) but left due to no tables")

def order(env, customer, order_point):
  yield env.timeout(random.expovariate(1/service_rate))  # Simulate ordering time
  yield order_point.put(customer)  # Add customer to order queue for kitchen

def kitchen(env, order_point, cook_time, stations):
  while True:
    customer = yield order_point.get()
    available_stations = stations - len(env.process(kitchen))  # Check available cooking stations
    if available_stations > 0:
      yield env.timeout(cook_time * customer.order_size)  # Simulate cook time based on order size
      if not customer.is_takeout:
        tables.remove(customer)  # Free table for dine-in customer
      # Customer is served, update statistics and wait time
      customer.wait_time = env.now - customer.wait_start if customer.wait_start else 0
    else:
      # No stations available, wait for one to free up
      yield kitchen(env, order_point, cook_time, stations)

def run_simulation(env, duration, arrival_rate, service_rate, cook_time):
  customers = []
  queue = Queue(env)
  order_point = Buffer(env, capacity=10)  # Buffer for orders waiting for kitchen
  tables = []  # List to track occupied tables (max 200)
  kitchen_stations = 15  # Number of cooking stations
  env.process(arrival(env, customers, queue, order_point, kitchen(env, order_point, cook_time, kitchen_stations), tables))
  env.run(duration)

  # Analyze results from customers list and tables (average wait time, etc.)
  total_wait_time = 0
  for customer in customers:
    if customer.wait_time:
      total_wait_time += customer.wait_time
  average_wait_time = total_wait_time / len(customers) if customers else 0
  print(f"Average wait time for dine-in customers: {average_wait_time:.2f}")
  print(f"Number of customers who left due to full tables: {len([c for c in customers if c.is_dine_in and not c.wait_start])}")

# Set parameters and run simulation
env = Environment()
run_simulation(env, 120, 2, 5, 2)  # Simulate for 2 hours with specific arrival/service rates and cook time

# Customer Class Variables:

# arrival_time: Stores the time the customer arrived at the restaurant.
# order_size: Represents the number of dishes the customer orders.
# is_takeout: Boolean variable indicating whether the order is take-out (True) or dine-in (False).
# wait_start: This variable is only used for dine-in customers and stores the time they started waiting for a table (initially None).
# wait_time: This variable is calculated after the customer is served and stores the total wait time for dine-in customers (0 for take-out).

# Event Function Variables:

# env: This variable represents the simulation environment object from the SimPy library.
# customers: This list stores information about all the customers who arrive at the restaurant.
# queue: This is a SimPy Queue object that holds customers waiting to place their order (used for take-out orders).
# order_point: This is a SimPy Buffer object that acts as a queue for customers waiting for a cooking station in the kitchen.
# kitchen: This refers to the kitchen function itself, which is a process in the simulation.
# tables: This list keeps track of currently occupied tables (maximum of 200).

# Other Variables:

# arrival_rate: This variable defines the average rate of customer arrivals (customers per unit time).
# service_rate: This variable represents the average rate at which orders are taken (orders per unit time).
# cook_time: This variable defines the base cooking time per dish in the order.
# stations: This variable specifies the total number of cooking stations available in the kitchen (15 in this example).
# duration: This variable defines the total simulation time (2 hours in this example)
