# this module takes a list of order hashes as input
# there are many different outputs that can be generated from this module
import pandas as pd
import requests
import csv
import io

from trades import get_trades
from resets import add_resets_column
from resources import subgraph_urls

# get the sample dataset
def get_sample_dataset(batch_sample_url):
    try:
        # 1. Fetch the data from the URL
        response = requests.get(batch_sample_url)
        response.raise_for_status() # Raise an exception for bad status codes (like 404 or 500)

        # 2. Read the CSV data
        # Use io.StringIO to handle the CSV data directly from the response text
        csv_data = io.StringIO(response.text)

        # Create a CSV reader object
        # Assuming the first row contains headers
        reader = csv.reader(csv_data)

        # Read the header row (A1:J1)
        headers = next(reader)

        # 3. Create a list of dictionaries
        orders = []
        for row in reader:
            # Create a dictionary for each row, mapping headers to row values
            row_dict = {header: value for header, value in zip(headers, row)}
            orders.append(row_dict)

        # check if orders is empty
        if len(orders) == 0:
            print("No orders found in the sample dataset")
            raise Exception("No orders found in the sample dataset")

        # Now `orders` contains your data as a list of dictionaries
        print(f"Successfully retrieved and parsed {len(orders)} rows.")

        return orders

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from URL: {e}")
        raise Exception(f"Error fetching data from URL: {e}")
    except StopIteration:
        print("Error: CSV file seems to be empty or couldn't read the header row.")
        raise Exception("Error: CSV file seems to be empty or couldn't read the header row.")
    except Exception as e:
        print(f"An error occurred during CSV processing: {e}")
        raise Exception(f"An error occurred during CSV processing: {e}")
    
# get aggregated results
# user must have created outputs using main_batch.py
def get_aggregated_results(aggregated_results_url):
    try:
        # 1. Fetch the data from the URL
        response = requests.get(aggregated_results_url)
        response.raise_for_status() # Raise an exception for bad status codes (like 404 or 500)

        # 2. Read the CSV data
        # Use io.StringIO to handle the CSV data directly from the response text
        csv_data = io.StringIO(response.text)

        # Create a CSV reader object
        # Assuming the first row contains headers   
        reader = csv.reader(csv_data)

        # Read the header row (A1:J1)
        headers = next(reader)

        # 3. Create a list of dictionaries
        orders = []
        for row in reader:
            # Create a dictionary for each row, mapping headers to row values
            row_dict = {header: value for header, value in zip(headers, row)}
            orders.append(row_dict)

        # check if orders is empty
        if len(orders) == 0:
            print("No orders found in the aggregated results")
            raise Exception("No orders found in the aggregated results")

        # Now `orders` contains your data as a list of dictionaries
        print(f"Successfully retrieved and parsed {len(orders)} rows.")

        return orders

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from URL: {e}")
        raise Exception(f"Error fetching data from URL: {e}")


# create a function that gets the strategy trades for each order, generates the reset events, and then counts the number of resets for each order hash
def get_reset_counts(order):

    order_hash = order['order_hash']

    if not order_hash:
        print(f"Order hash not found for order: {order}")
        raise Exception(f"Order hash not found for order: {order}")

    # get the subgraph url using the network
    subgraph_url = subgraph_urls[order['network']]

    if not subgraph_url:
        print(f"Subgraph URL not found for network: {order['network']}")
        raise Exception(f"Subgraph URL not found for network: {order['network']}")

    # get the strategy trades for the order
    strategy_trades = get_trades(order_hash, subgraph_url, '2024-01-01', '2025-04-17')

    # generate the reset events for the order
    reset_events = add_resets_column(strategy_trades)

    # cehck if reset_events is none or is not a dataframe
    if reset_events is None:
        print(f"Error getting reset events for order: {order['order_hash']}")
        raise Exception(f"Error getting reset events for order: {order['order_hash']}")
    elif not isinstance(reset_events, pd.DataFrame):
        print(f"Reset events is not a dataframe for order: {order['order_hash']}")
        raise Exception(f"Reset events is not a dataframe for order: {order['order_hash']}")

    # count the number of resets for the order
    reset_count = reset_events['resets'].sum()

    # check if reset_count is none
    if reset_count is None:
        print(f"Reset count is none for order: {order['order_hash']}")
        raise Exception(f"Reset count is none for order: {order['order_hash']}")

    # check if reset_count is not an integer
    if not isinstance(reset_count, int):
        print(f"Reset count is not an integer for order: {order['order_hash']}")
        print("Coercing reset count to an integer...")
        reset_count = int(reset_count)

    # return the reset count for the order
    return reset_count

# get the reset counts for the order hashes
# reset_counts = []
# for order in orders:
#     reset_count = get_reset_counts(order)

#     if reset_count is None:
#         print(f"Error getting reset counts for order: {order['order_hash']}")
#         raise Exception(f"Error getting reset counts for order: {order['order_hash']}")

#     print(f"\nNumber of resets in strategy {order['order_hash']}: {reset_count}\n")
#     reset_counts.append({"order_hash": order['order_hash'], "reset_count": reset_count})

# # check if reset_counts len is 0
# if len(reset_counts) == 0:
#     print("No reset counts found")
#     raise Exception("No reset counts found")


# # convert to a dataframe and export to csv
# try:
#     df_reset_counts = pd.DataFrame(reset_counts)
#     df_reset_counts.to_csv("/Users/Shared/rain/reset_counts.csv", index=False)
# except Exception as e:
#     print(f"Error exporting reset count df to csv: {e}")
#     raise Exception(f"Error exporting reset count df to csv: {e}")