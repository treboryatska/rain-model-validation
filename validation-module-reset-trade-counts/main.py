import pandas as pd
import os
from resources import subgraph_urls
from orders import get_order_info
from trades import get_trades
from resets import (
    add_resets_column, 
    concatenate_strategy_trades_with_market_trades
)
from check import (
    check_model_output_file_columns, 
    check_model_input_file_columns, 
    check_model_file_path, 
    clean_model_input_file, 
    clean_model_output_file
)
from stats import basic_stats

print("\n#################################################################################################################################")
print("#################################################################################################################################")
print("######################################################     starting validation script     #######################################")
print("#################################################################################################################################")
print("#################################################################################################################################\n")

# #####################################################################################
# validation parameters
# #####################################################################################

# define the location of the actual model output file
# connect to google sheets to get the model output file
model_input_file_path = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTzY4ojDhxerTo5bEaShVSXK1bDx-QBx5wwJTI2EQDegjNiE48u-a_XhDUvNHa6x_s-pZ4BMR83k3i3/pub?gid=634861611&single=true&output=csv"
model_output_file_path = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTzY4ojDhxerTo5bEaShVSXK1bDx-QBx5wwJTI2EQDegjNiE48u-a_XhDUvNHa6x_s-pZ4BMR83k3i3/pub?gid=2118869616&single=true&output=csv"

# Define the network
# current options are: flare, base, polygon, arbitrum, bsc, linea, ethereum
# note, this is the network the order was made on
network = "base"

# Define query parameters/variables
target_order_hash = "0xbdffe74d38286fe9182c52e79161ed9d87e71a5133c34c069b2e3e541a74f9df"

# define the start and end timestamps
# format: %Y-%m-%d
start_date_str = "2024-10-31"
end_date_str = "2025-04-17"

# get the Subgraph Endpoint URL
subgraph_url = subgraph_urls[network]

# inform the user that the model output data must start at row 23
rows_to_skip = 22

print("\n--------------------------------\nInput parameters\n--------------------------------\n")
print(f"Model input file path: {model_input_file_path}")
print(f"Model output file path: {model_output_file_path}")
print(f"Network: {network}")
print(f"Target order hash: {target_order_hash}")
print(f"Start date: {start_date_str}")
print(f"End date: {end_date_str}")
print(f"Subgraph URL: {subgraph_url}")
print(f"Rows to skip at the top of the model file: {rows_to_skip}")
print("\nWarning:")
print(f"The model output data must start at row {rows_to_skip + 1} of the model file")
print(f"adjust the rows_to_skip variable to the correct row number for your model file")
print("the validation script will fail if it cannot find the data at the correct row number")
print("\n--------------------------------\n\n")
# #####################################################################################
# end of validation parameters
# #####################################################################################



# #####################################################################################
# get order info and trades
# #####################################################################################
print("\n--------------------------------\nGetting strategy order info and trades\n--------------------------------\n")

order_info = get_order_info(target_order_hash, subgraph_url)
if order_info is None:
    print(f"No order info found for order {target_order_hash}")
    raise ValueError("No order info found for order {target_order_hash}. Exiting...")

print(f"order info: {order_info}")

# capture the strategy start datetime
strategy_start_datetime = pd.to_datetime(int(order_info['timestampAdded']), unit='s')
print(f"strategy start datetime: {strategy_start_datetime}")

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

    # convert token amounts to base and round to 5 decimal places
    df_trades_resets["input_amount_base"] = (df_trades_resets["input_amount"] / 10**df_trades_resets["input_decimals"]).round(5)
    df_trades_resets["output_amount_base"] = (df_trades_resets["output_amount"] / 10**df_trades_resets["output_decimals"]).round(5)

    # drop input_amount, output_amount, input_decimals, output_decimals columns
    df_trades_resets = df_trades_resets.drop(columns=["input_amount", "output_amount", "input_decimals", "output_decimals"])
    
    # Print the first 5 rows of the dataframe
    print(f"\nDataFrame with resets:")
    print(df_trades_resets.head(5))

    # capture the date range of the strategy trades dataframe   
    strategy_trades_date_begin = df_trades_resets['trade_timestamp_human'].min()
    strategy_trades_date_end = df_trades_resets['trade_timestamp_human'].max()
    print(f"\nDate range of strategy trades dataframe: {strategy_trades_date_begin} to {strategy_trades_date_end}")

    # print the count of resets
    print(f"\nNumber of resets in the strategy trades: {df_trades_resets['resets'].sum()}\n")

else:
    print(f"No trades found for order {target_order_hash} between {start_date_str} and {end_date_str}")

print("\n--------------------------------\nFinished getting order info and trades\n--------------------------------\n\n")
# #####################################################################################
# end of get order info and trades
# #####################################################################################

# #####################################################################################
# get model input data
# #####################################################################################
print("\n--------------------------------\nGetting model input data\n--------------------------------\n")

# check the model file path appears valid
# if not check_model_file_path(model_input_file_path):
#     raise ValueError("Model input file path is not valid")

# get the model file and check it is valid
# the model input data starts at row 1
# if the model file does not contain the tx_hash and timestamp columns, raise an error
df_market_trades = pd.read_csv(model_input_file_path)
if df_market_trades is None:
    raise ValueError("Model input file is not valid")

# check the model file contains the tx_hash and timestamp columns
if not check_model_input_file_columns(model_input_file_path, df_market_trades):
    raise ValueError("Model input file does not contain the tx_hash and timestamp columns")

# get the tx_hash and timestamp columns from the model file
try: 
    # clean the model file
    print(f"cleaning model input data file...")
    df_market_trades_clean = clean_model_input_file(df_market_trades)
    print(f"model input data file cleaned...")

    # check that the trade count between resets is not None
    if df_market_trades_clean is None:
        raise ValueError("No market trade data found in the model input data file")
    
    # confirm the object is a dataframe
    if not isinstance(df_market_trades_clean, pd.DataFrame):
        raise ValueError("market trade data object is not a dataframe")
    
    # print intermediate results for user
    print(f"\nSuccessfully imported model input data from {model_input_file_path}")
    # print info
    print("\nModel input data dataframe info:")
    print(df_market_trades_clean.info())
    print(df_market_trades_clean.head())
    print("\n\n")

except KeyError as ke:
    raise ValueError(f"KeyError: Column {ke} not found in model input data file")

# filter the values to match the strategy date range
try:

    # check the date range of the model input file is valid
    print(f"checking date range of model input data file...")

    # get the start date of the model input file
    model_input_file_start_date = df_market_trades_clean['datetime'].min()
    if abs(model_input_file_start_date - strategy_trades_date_begin) > pd.Timedelta(minutes=15):
        print("Date range of model input data file is not valid.")
        print(f"model input data file start date: {model_input_file_start_date}")
        print(f"strategy trades start date: {strategy_trades_date_begin}")
        print("These dates must be within 15 minutes of each other.")
        raise ValueError("Exiting...")
    print(f"date range of model input data file is valid...")

    print(f"\nfiltering model input data to match the strategy end date...")
    df_market_trades_clean = df_market_trades_clean[df_market_trades_clean['datetime'] <= strategy_trades_date_end]

    # print intermediate results for user
    print(f"\nSuccessfully filtered model input data to match the strategy date range")
    print("checking model input data datetime values after filtering")
    print(f"first datetime value: {df_market_trades_clean['datetime'].iloc[0]}")
    print(f"last datetime value: {df_market_trades_clean['datetime'].iloc[-1]}")

    print("\nThe final model input data dataframe is:")
    print(df_market_trades_clean.info())
    print(df_market_trades_clean)

    print(f"\nThe total number of trades in the model input data file: {len(df_market_trades_clean)}\n")

except Exception as e:
    print(f"An unexpected error occurred: {type(e).__name__} - {e}")
    raise # program stops

print("\n--------------------------------\nFinished getting model input data\n--------------------------------\n\n")
# #####################################################################################
# end of get model input data
# #####################################################################################



# #####################################################################################
# get model output data
# #####################################################################################
print("\n--------------------------------\nGetting model output data\n--------------------------------\n")

# check the model file path appears valid
# if not check_model_file_path(model_output_file_path):
#     raise ValueError("Model outputfile path is not valid")

# get the model output file and check it is valid
# the model output data must start at row 23
# if the model output file does not contain the date/time and trade_count_in_reset columns, raise an error
df_model = pd.read_csv(model_output_file_path, skiprows=rows_to_skip)
if df_model is None:
    raise ValueError("Model output file is not valid")

# check the model output file contains the date/time and trade_count_in_reset columns
if not check_model_output_file_columns(model_output_file_path, df_model):
    raise ValueError("Model output file does not contain the date/time and trade_count_in_reset columns")

# get the datetime and trade_count_in_reset between resets from the model file
try: 
    # clean the model file
    print(f"cleaning model output data file...")
    df_model_trade_count_in_reset = clean_model_output_file(df_model)
    print(f"model output data file cleaned...")

    # check that the trade count between resets is not None
    if df_model_trade_count_in_reset is None:
        raise ValueError("No trade count between resets found in the model file")
    
    # confirm the object is a dataframe
    if not isinstance(df_model_trade_count_in_reset, pd.DataFrame):
        raise ValueError("Model output trade counts between resets object is not a dataframe")
    
    # print intermediate results for user
    print(f"\nSuccessfully imported model output data from {model_output_file_path}")
    # print info
    print("\nModel output dataframe info:")
    print(df_model_trade_count_in_reset.info())
    print(df_model_trade_count_in_reset.head())
    print("\n\n")

except KeyError as ke:
    raise ValueError(f"KeyError: Column {ke} not found in model output data file")

# filter the values to match the strategy date range
try:

    # check the date range of the model output data file is valid
    # compare date ranges specified in start_date_obj to the start date of the model input file
    # these dates should be within 90 minutes of each other
    # note this is more lenient than the model input data file due to the floor function used in the model outputs
    print(f"checking date range of model output data file...")
    model_output_file_start_date = df_model_trade_count_in_reset['datetime'].min()
    if abs(model_output_file_start_date - strategy_trades_date_begin) > pd.Timedelta(minutes=95):
        print("Date range of model output data file is not valid.")
        print(f"model output data file start date: {model_output_file_start_date}")
        print(f"strategy trades start date: {strategy_trades_date_begin}")
        print("These dates must be within 15 minutes of each other.")
        raise ValueError("Exiting...")
    print(f"date range of model output data file is valid...")


    print(f"\nfiltering model output data to match the strategy end date...")
    df_model_trade_count_in_reset = df_model_trade_count_in_reset[df_model_trade_count_in_reset['datetime'] <= strategy_trades_date_end]

    # print intermediate results for user
    print(f"\nSuccessfully filtered model output data to match the strategy date range")
    print("checking model output datetime values after filtering")
    print(f"first datetime value: {df_model_trade_count_in_reset['datetime'].iloc[0]}")
    print(f"last datetime value: {df_model_trade_count_in_reset['datetime'].iloc[-1]}")

    print("\nThe final model output dataframe is:")
    print(df_model_trade_count_in_reset.info())
    print(df_model_trade_count_in_reset.head())

except Exception as e:
    print(f"An unexpected error occurred: {type(e).__name__} - {e}")
    raise # program stops

print("\n--------------------------------\nFinished getting model output data\n--------------------------------\n\n")
# #####################################################################################
# end of get model output data
# #####################################################################################

# #####################################################################################
# concatenate model input data with strategy trades
# #####################################################################################
print("\n--------------------------------\nConcatenating model input data with strategy trades\n--------------------------------\n")

# concatenate the two dataframes - keep only the tx_hash and trade_count_in_reset columns
df_all_trades = concatenate_strategy_trades_with_market_trades(df_trades_resets, df_market_trades_clean)

if df_all_trades is None:
    raise ValueError("df_all_trades is None. Exiting...")

# print info about df_all_trades
print("\ndf_all_trades")
print(df_all_trades.info())
print(df_all_trades.head())

print("\n--------------------------------\nFinished concatenating model input data with strategy trades\n--------------------------------\n\n")
# #####################################################################################
# end of concatenate model input data with strategy trades
# #####################################################################################


# #####################################################################################
# run tests on modeled trade count between resets and actual trade count between resets
# #####################################################################################
print("\n--------------------------------\nRunning tests on modeled trade count between resets and actual trade count between resets\n--------------------------------\n")

# confirm dates in both dataframes
# check if both dataframes exist 
if df_model_trade_count_in_reset is None:
    raise ValueError("df_model_trade_count_in_reset is None. Exiting...")
if df_all_trades is None:
    raise ValueError("df_all_trades is None. Exiting...")

# print the start date of the strategy, and thedate range of both dataframes
print(f"strategy start datetime: {strategy_start_datetime}")
print(f"the date of the first trade in the strategy: {strategy_trades_date_begin}")
print(f"the date of the last trade in the strategy: {strategy_trades_date_end}")
print(f"Date range of modeled outputs data: {df_model_trade_count_in_reset['datetime'].min()} to {df_model_trade_count_in_reset['datetime'].max()}")
print(f"Date range of the concatenated strategy trades and market trades data: {df_all_trades['trade_timestamp'].min()} to {df_all_trades['trade_timestamp'].max()}")

# get the basic stats
strategy_basic_stats = basic_stats(df_trades_resets, df_all_trades, df_market_trades_clean, df_model_trade_count_in_reset)

print("\n--------------------------------\nFinished running tests on modeled trade count between resets and actual trade count between resets\n--------------------------------\n")
# #####################################################################################
# end of run tests on modeled trade count between resets and actual trade count between resets
# #####################################################################################