
import dask.distributed as dd
def compute_function(df):
    # Define your function here
    return df['column_name'].sum()

if __name__ == "__main__":
    client = dd.Client("tcp://127.0.0.1:8786")
    print('44444')
    print(dd.get_worker())
    # Receive the data from the master
    df = dd.get_worker().get_data(1)

    # Compute the function on the received data
    result = compute_function(df)

    # Send the result back to the master
    client.submit(lambda x: x, result, workers="tcp://127.0.0.1:8786")