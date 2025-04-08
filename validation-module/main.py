import pandas as pd

from resources import subgraph_urls
from orders import get_order_info
from trades import get_trades
from resets import add_resets_column, calculate_trades_between_resets
# Define the Subgraph Endpoint URL
subgraph_url = subgraph_urls["flare"]

# Define query parameters/variables
target_order_hash = "0xa3ee58f8abfb991496e9fc6b16ada0162a0513429b2061c4073a3a19588ef712"

# define the start and end timestamps
start_date_str = "2025-01-01"
end_date_str = "2025-04-08"

# get the order info
order_info = get_order_info(target_order_hash, subgraph_url)
if order_info is not None:
    print(f"order info: {order_info}")
else:
    print(f"No order info found for order {target_order_hash}")

# get the trades
df_trades = get_trades(target_order_hash, subgraph_url, start_date_str, end_date_str)

# if trades is not None, construct column that tracks resets
if df_trades is not None:

    try:
        # get a slice of the df
        df_input_slice = df_trades[["order_hash", "tx_hash", "block_number", "trade_timestamp","input_token", "input_amount", "input_decimals", "output_token", "output_amount", "output_decimals"]].copy()

        # add the resets column to the df
        df_trades_resets = add_resets_column(df_input_slice)

        if df_trades_resets is None:
            print("Warning: df_trades_resets is None")
        
    except ValueError as ve:
        # Catch the specific input validation errors from add_resets_column
        print(f"Input Data Error for add_resets_column: {ve}")
        raise # program stops
    except KeyError as ke:
        # Catch errors if columns are missing during the initial slice operation
        print(f"Error preparing input: Column {ke} not found in original df_trades.")
        raise # program stops
    except Exception as e:
        # Catch any other unexpected errors (MemoryError, TypeError during processing etc.)
        print(f"An unexpected error occurred: {type(e).__name__} - {e}")
        raise # program stops

    # add a human readable timestamp column
    df_trades_resets['trade_timestamp_human'] = pd.to_datetime(df_trades_resets['trade_timestamp'], unit='s')

    # convert token amounts to gwei and round to 5 decimal places
    df_trades_resets["input_amount_base"] = (df_trades_resets["input_amount"] / 10**df_trades_resets["input_decimals"]).round(5)
    df_trades_resets["output_amount_base"] = (df_trades_resets["output_amount"] / 10**df_trades_resets["output_decimals"]).round(5)

    # drop input_amount, output_amount, input_decimals, output_decimals columns
    df_trades_resets = df_trades_resets.drop(columns=["input_amount", "output_amount", "input_decimals", "output_decimals"])
    
    # Print the first 5 rows of the dataframe
    print(f"\nDataFrame with resets:")
    print(df_trades_resets.head(5))

    # print the count of resets
    print(f"\nNumber of resets: {df_trades_resets['resets'].sum()}\n")

    # count the number of trades between resets
    try:
        df_trades_resets = calculate_trades_between_resets(df_trades_resets)
    except ValueError as ve:
        print(f"Input Data Error for calculate_trades_between_resets: {ve}")
        raise # program stops
    except Exception as e:
        print(f"An unexpected error occurred: {type(e).__name__} - {e}")
        raise # program stops

    if df_trades_resets is not None:

        # print the first 5 rows of the dataframe
        print(f"\nDataFrame with rows since last reset:")
        print(df_trades_resets.head(5))

        # print the number of trades between resets
        print(f"Average number of trades between resets: {df_trades_resets['rows_since_last_reset'].mean()}")

    else:
        # If no resets were found, just create the column with NA values
        df_trades_resets['rows_since_last_reset'] = pd.NA
        df_trades_resets['rows_since_last_reset'] = df_trades_resets['rows_since_last_reset'].astype(pd.Int64Dtype())
        print("\nNo resets found in the data.")
        # print the first 5 rows of the dataframe
        print(f"\nDataFrame structure:")
        print(df_trades_resets.head(5))

else:
    print(f"No trades found for order {target_order_hash} between {start_date_str} and {end_date_str}")