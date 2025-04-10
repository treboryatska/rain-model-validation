import pandas as pd

from resources import subgraph_urls
from orders import get_order_info
from trades import get_trades
from resets import add_resets_column, calculate_trades_between_resets
from check import check_model_file_path, check_date_range, check_model_file_columns

# define the location of the actual model output file
# connect to google sheets to get the model output file
model_file_path = "/Users/trevorjacka/Downloads/model_1_0xa3ee58f8abfb991496e9fc6b16ada0162a0513429b2061c4073a3a19588ef712  - Test-15M 2.csv"

# Define the network
# current options are: flare, base, polygon, arbitrum, bsc, linea, ethereum
# note, this is the network the order was made on
network = "flare"

# Define query parameters/variables
target_order_hash = "0xa3ee58f8abfb991496e9fc6b16ada0162a0513429b2061c4073a3a19588ef712"

# define the start and end timestamps
# format: %Y-%m-%d
start_date_str = "2025-01-01"
end_date_str = "2025-04-08"

# get the Subgraph Endpoint URL
subgraph_url = subgraph_urls[network]

# inform the user that the model output data must start at row 23
rows_to_skip = 22
print(f"The model output data must start at row {rows_to_skip + 1} of the model file")
print(f"adjust the rows_to_skip variable to the correct row number for your model file")
print("the validation script will fail if it cannot find the data at the correct row number")

# check the model file path appears valid
if not check_model_file_path(model_file_path):
    raise ValueError("Model file path is not valid")

# get the model file and check it is valid
# the model output data must start at row 23
# if the model file does not contain the date/time and trade_count_btwn_resets columns, raise an error
df_model = pd.read_csv(model_file_path, skiprows=rows_to_skip)
if df_model is None:
    raise ValueError("Model file is not valid")

# check the model file contains the date/time and trade_count_btwn_resets columns
if not check_model_file_columns(model_file_path, df_model):
    raise ValueError("Model file does not contain the date/time and trade_count_btwn_resets columns")

# check the date range of the model file is valid
if not check_date_range(start_date_str, end_date_str, model_file_path, df_model):
    raise ValueError("Date range of model file is not valid. Exiting...")

# get the trade count between resets from the model file
trade_count_btwn_resets_modeled = df_model['trade_count_btwn_resets'].iloc[0]

# check that the trade count between resets is not None
if trade_count_btwn_resets_modeled is None:
    raise ValueError("No trade count between resets found in the model file")

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


# #####################################################################################
# run tests on modeled trade count between resets and actual trade count between resets
# #####################################################################################

# test 1: modeled trade count between resets is equal to actual trade count between resets
if trade_count_btwn_resets_modeled == df_trades_resets['rows_since_last_reset'].sum():
    print("Test 1 passed: modeled trade count between resets is equal to actual trade count between resets")
else:
    print("Test 1 failed: modeled trade count between resets is not equal to actual trade count between resets")