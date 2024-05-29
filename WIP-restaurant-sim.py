import simpy
import numpy as np
import random
import matplotlib.pyplot as plt

# Parameters
SIMULATION_TIME = 480  # Total simulation time in minutes (e.g., 8 hours)
DINEIN_ARRIVAL_RATE = 1 / 5  # Average arrival rate for dine-in (e.g., 1 customer every 5 minutes)
TAKEOUT_ARRIVAL_RATE = 1 / 8  # Average arrival rate for takeout (e.g., 1 order every 8 minutes)
BASE_SERVICE_RATE = 1 / 4  # Base service rate for dine-in customers (e.g., service time of 4 minutes)
TAKEOUT_SERVICE_RATE = 1 / 3  # Service rate for takeout orders (e.g., service time of 3 minutes)
KITCHEN_COOK_RATE = 1 / 10  # Average time to cook an order (e.g., 10 minutes per order)
NUM_SERVERS = 3  # Number of servers
NUM_COOKS = 2  # Number of cooks in the kitchen
NUM_TABLES = 10  # Number of tables in the restaurant

# Function to generate random party size
def get_party_size():
    return random.randint(1, 6)  # Random party size between 1 and 6

all_party_sizes = []

# Customer process for dine-in
def dinein_customer(env, name, restaurant, kitchen):
    arrival_time = env.now
    party_size = get_party_size()
    all_party_sizes.append(party_size)
    print(f'{name} (party of {party_size}) arrives at the restaurant at {arrival_time:.2f}')
    
    with kitchen.request() as kitchen_request:
        yield kitchen_request
        cook_time = np.random.exponential(KITCHEN_COOK_RATE)
        print(f'{name} starts cooking at {env.now:.2f} (expected cook time {cook_time:.2f} minutes)')
        yield env.timeout(cook_time)
        print(f'{name} finishes cooking at {env.now:.2f}')
    
    with restaurant.request() as request:
        yield request
        wait_time = env.now - arrival_time
        wait_times.append(wait_time)
        
        print(f'{name} (party of {party_size}) starts being served at {env.now:.2f} (waited {wait_time:.2f} minutes)')
        service_time = np.random.exponential(party_size / BASE_SERVICE_RATE)
        yield env.timeout(service_time)
        print(f'{name} (party of {party_size}) leaves the restaurant at {env.now:.2f} after being served for {service_time:.2f} minutes')

# Process for takeout orders
def takeout_order(env, name, kitchen):
    order_time = env.now
    print(f'{name} (takeout) order is placed at {order_time:.2f}')
    
    with kitchen.request() as kitchen_request:
        yield kitchen_request
        cook_time = np.random.exponential(KITCHEN_COOK_RATE)
        print(f'{name} starts cooking at {env.now:.2f} (expected cook time {cook_time:.2f} minutes)')
        yield env.timeout(cook_time)
        print(f'{name} finishes cooking at {env.now:.2f}')
    
    wait_time = env.now - order_time
    wait_times.append(wait_time)
    
    print(f'{name} (takeout) is ready for pickup at {env.now:.2f} (waited {wait_time:.2f} minutes)')

# Dine-in customer generator process
def dinein_customer_generator(env, restaurant, kitchen):
    i = 0
    while True:
        yield env.timeout(np.random.exponential(1 / DINEIN_ARRIVAL_RATE))
        i += 1
        env.process(dinein_customer(env, f'Dine-in Customer {i}', restaurant, kitchen))

# Takeout order generator process
def takeout_order_generator(env, kitchen):
    i = 0
    while True:
        yield env.timeout(np.random.exponential(1 / TAKEOUT_ARRIVAL_RATE))
        i += 1
        env.process(takeout_order(env, f'Takeout Order {i}', kitchen))

# Set up the environment and run the simulation
env = simpy.Environment()
restaurant = simpy.Resource(env, NUM_SERVERS)
kitchen = simpy.Resource(env, NUM_COOKS)
wait_times = []

env.process(dinein_customer_generator(env, restaurant, kitchen))
env.process(takeout_order_generator(env, kitchen))
env.run(until=SIMULATION_TIME)

# Results
average_wait_time = np.mean(wait_times)
max_wait_time = np.max(wait_times)
total_served_customers = len(wait_times)

print(f'Average wait time: {average_wait_time:.2f} minutes')
print(f'Max wait time: {max_wait_time:.2f} minutes')
print(f'Total served customers: {total_served_customers}')

# Plot the results
plt.hist(wait_times, bins=30, edgecolor='black')
plt.title('Histogram of Customer Wait Times')
plt.xlabel('Wait Time (minutes)')
plt.ylabel('Frequency')
plt.show()

# Plot the party sizes
plt.hist(all_party_sizes, bins=6, edgecolor='black')
plt.title('Histogram of Dine-In Party Sizes')
plt.xlabel('Party Size')
plt.ylabel('Frequency')
plt.show()