import datetime

from resources import subgraph_urls
from orders import get_order_info
from trades import get_trades

# Define the Subgraph Endpoint URL
subgraph_url = subgraph_urls["flare"]

# Define query parameters/variables
target_order_hash = "0xa3ee58f8abfb991496e9fc6b16ada0162a0513429b2061c4073a3a19588ef712"

# get the order info
order_info = get_order_info(target_order_hash, subgraph_url)
print(f"Order info: {order_info}")

# define the start and end timestamps
start_date_str = "2025-01-01"
end_date_str = "2025-04-08"

# get the trades
df_trades = get_trades(target_order_hash, subgraph_url, start_date_str, end_date_str)

# if trades is not None, construct column that tracks resets
if df_trades is not None:
    df_trades_resets = df_trades[["order_hash", "tx_hash", "input_token", "input_amount", "input_decimals", "output_token", "output_amount", "output_decimals"]].copy()

    # convert token amounts to gwei and round to 5 decimal places
    df_trades_resets["input_amount_base"] = (df_trades_resets["input_amount"] / 10**df_trades_resets["input_decimals"]).round(5)
    df_trades_resets["output_amount_base"] = (df_trades_resets["output_amount"] / 10**df_trades_resets["output_decimals"]).round(5)

    # drop input_amount, output_amount, input_decimals, output_decimals columns
    df_trades_resets = df_trades_resets.drop(columns=["input_amount", "output_amount", "input_decimals", "output_decimals"])

    # Get the 'input_token' from the *previous* row
    df_trades_resets['prev_input_token'] = df_trades_resets['input_token'].shift(1)

    # Get the 'output_token' from the *previous* row
    df_trades_resets['prev_output_token'] = df_trades_resets['output_token'].shift(1)

    # Define the condition for a reset:
    df_trades_resets['resets'] = (df_trades_resets['input_token'] == df_trades_resets['prev_output_token']) & \
                                (df_trades_resets['output_token'] == df_trades_resets['prev_input_token'])
    
    # Print the first 5 rows of the dataframe
    print(df_trades_resets.head(5))

    # print the count of resets
    print(f"\nNumber of resets: {df_trades_resets['resets'].sum()}")

else:
    print(f"No trades found for order {target_order_hash} between {start_date_str} and {end_date_str}")