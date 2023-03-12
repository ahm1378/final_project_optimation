import dask.dataframe as dd
from dask.distributed import Client, wait

# Create Dask client
client = Client("tcp://127.0.0.1:8786")

# Define the function to compute on the first part of the list
def compute_func_1(data):
    # Perform computation here
    result = sum(data)
    return result

# Load data into Dask dataframe
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
df = dd.from_array(data, 5)

# Send first partition to Computer 1
partition_1 = df.get_partition(0)
future_1 = client.submit(partition_1.compute, workers=["127.0.0.1"])

# Send second partition to Computer 2
partition_2 = df.get_partition(1)
future_2 = client.submit(partition_2.compute, workers=["127.0.0.2"])

# Send third partition to Computer 3
partition_3 = df.get_partition(2)
future_3 = client.submit(partition_3.compute, workers=["127.0.0.3"])

# Send fourth partition to Computer 4
partition_4 = df.get_partition(3)
future_4 = client.submit(partition_4.compute, workers=["127.0.0.4"])

# Wait for results from other computers
results = wait([future_2, future_3, future_4])

# Get the result from Computer 1
result_1 = compute_func_1(future_1.result())

# Get the results from other computers
result_2 = results[0].result()
result_3 = results[1].result()
result_4 = results[2].result()

# Merge results and compute final result
final_result = result_1 + result_2 + result_3 + result_4

# Print final result
print("Final result:", final_result)
