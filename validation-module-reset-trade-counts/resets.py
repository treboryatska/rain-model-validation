import pandas as pd

# function to add a column to the dataframe that tracks resets in DSF strategies
def add_resets_column(df):

    # confirm the passed variable is a dataframe
    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed variable is not a dataframe")
    
    # confirm the required columns are present in the dataframe
    required_columns = ["trade_timestamp","input_token", "output_token"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"The required columns are missing from the dataframe: {missing_columns}")
    
    try:
        # ensure the df is sorted descend by trade_timestamp
        df = df.sort_values(by='trade_timestamp', ascending=True, ignore_index=True)

        # Get the 'input_token' from the *previous* row
        df['prev_input_token'] = df['input_token'].shift(1)

        # Get the 'output_token' from the *previous* row
        df['prev_output_token'] = df['output_token'].shift(1)

        # Define the condition for a reset:
        df['resets'] = (df['input_token'] == df['prev_output_token']) & \
                                    (df['output_token'] == df['prev_input_token'])
        
        return df
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    
# function to calculate the number of trades between resets
def calculate_trades_between_resets(df):

    # confirm the passed variable is a dataframe
    if not isinstance(df, pd.DataFrame):
        raise ValueError("The passed variable is not a dataframe")
    
    # confirm the required columns are present in the dataframe
    required_columns = ["trade_timestamp", "resets"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print("Cannot calculate the number of trades between resets.")
        raise ValueError(f"The required columns are missing from the dataframe: {missing_columns}")
    print("The concatenated dataframe is the right object type and has the required columns. Continuing...")
    
    try:
        # ensure the df is sorted by trade_timestamp
        df = df.sort_values(by='trade_timestamp', ascending=True, ignore_index=True)

        # get the index labels where 'resets' is True
        # This tells us how many rows total are between the start of one reset and the start of the next one.
        # Convert to Series to ensure .diff() works robustly
        print("Getting the index labels where 'resets' is True...")
        reset_indices = df.index[df['resets']]

        if not reset_indices.empty:
            print("Reset indices found. Calculating the difference between consecutive reset indices...")
            # Calculate the difference between consecutive reset indices.
            index_diff = reset_indices.to_series().diff()

            # calculate the number of rows between resets
            rows_between_count = index_diff - 1

            # Handle the first reset row specifically
            first_reset_idx = reset_indices[0]

            # The count for the first reset is the number of rows before it,
            # which is simply its index value (due to the 0-based reset index).
            first_reset_count = first_reset_idx

            # Update the count for the first reset index in our results Series
            # Use .loc to ensure assignment happens at the correct index label
            rows_between_count.loc[first_reset_idx] = first_reset_count

            # Create a new column, initializing with a suitable null value (like Pandas' NA)
            print("Creating a new column, initializing with a suitable null value (like Pandas' NA)...")
            df['rows_since_last_reset'] = pd.NA

            # Assign the calculated counts to the corresponding reset rows in the new column.
            # The first reset row will have NA since diff() gives NA for the first element.
            df.loc[reset_indices, 'rows_since_last_reset'] = rows_between_count

            # Convert to nullable integer type for cleaner representation
            print("Converting to nullable integer type for cleaner representation...")
            df['rows_since_last_reset'] = df['rows_since_last_reset'].astype(pd.Int64Dtype())

            return df
        else:
            print("No resets found in the dataframe.")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# function to merge strategy trades with the market trades
def concatenate_strategy_trades_with_market_trades(df_strategy_trades, df_market_trades):
    # this module filters the strategy trades for resets == True
    # then it concatenates the "reset" txs with the market trades dataframes
    # then it orders the concatenated dataframe by trade_timestamp
    # where do we get the actual trade data from? Just manually download it from the csv files sid pulled. Good for a first pass.
    # why do we keep only the reset txs? any txs in the strategy that are not resets are either irrelevant for this analysis or are duplicates of the market trades
    # we only need the reset txs as the "checkpoint" to trigger when we should reset our count of trades between resets

    # confirm the passed variables are dataframes
    if not isinstance(df_strategy_trades, pd.DataFrame):
        raise ValueError("The passed variable is not a dataframe")
    if not isinstance(df_market_trades, pd.DataFrame):
        raise ValueError("The passed variable is not a dataframe")
    
    # filter the strategy trades for resets == True
    df_strategy_trades_resets_only = df_strategy_trades[df_strategy_trades['resets'] == True]
    
    # rename datetime to trade_timestamp
    df_market_trades.rename(columns={'datetime': 'trade_timestamp'}, inplace=True)
    # check column types first
    print(f"Checking column types between strategy trades and market trades...")
    if df_strategy_trades_resets_only[['tx_hash', 'trade_timestamp']].dtypes.equals(df_market_trades[['tx_hash', 'trade_timestamp']].dtypes):
        print("Column types are the same")
    else:
        print("Column types are different")
        print(df_strategy_trades_resets_only[['tx_hash', 'trade_timestamp']].dtypes)
        print(df_market_trades[['tx_hash', 'trade_timestamp']].dtypes)
        
        if df_strategy_trades_resets_only['trade_timestamp'].dtype != df_market_trades['trade_timestamp'].dtype:
            print("trade_timestamp column types are different")
            print("coercing the version that is int64 to datetime")
            if df_strategy_trades_resets_only['trade_timestamp'].dtype == 'int64':
                print("coercing strategy trades trade_timestamp to datetime")
                df_strategy_trades_resets_only['trade_timestamp'] = pd.to_datetime(df_strategy_trades_resets_only['trade_timestamp'], unit='s')
                print("strategy trades trade_timestamp coerced to datetime")
            else:
                print("coercing market trades trade_timestamp to datetime")
                df_market_trades['trade_timestamp'] = pd.to_datetime(df_market_trades['trade_timestamp'], unit='s')
                print("market trades trade_timestamp coerced to datetime")
        else:
            print("tx_hash column types are different")
            print(df_strategy_trades_resets_only['tx_hash'].dtype)
            print(df_market_trades['tx_hash'].dtype)

    # concatenate the two dataframes 
    print("Concatenating the strategy trades and market trades dataframes...")
    df_all_trades = pd.concat([df_strategy_trades_resets_only[['tx_hash', 'trade_timestamp', 'resets']], df_market_trades[['tx_hash', 'trade_timestamp']]], ignore_index=True)
    print("Concatenated the strategy trades and market trades dataframes...")
    print("Filling NaN values in 'resets' column with False...")
    # Fill the NaN values specifically in the 'resets' column with False
    df_all_trades['resets'] = df_all_trades['resets'].fillna(False)
    df_all_trades['resets'] = df_all_trades['resets'].astype(bool)

    # order the df by trade_timestamp
    df_all_trades = df_all_trades.sort_values(by='trade_timestamp', ascending=True, ignore_index=True)

    try:
        # flag and handle duplicate tx_hash values in the concatenated dataframe
        if df_all_trades.duplicated(subset=['tx_hash']).any():
            print("\n*********************************************************************************")
            print("Duplicate tx_hash values in the concatenated dataframe")
            print("*********************************************************************************\n")

            # count the number of duplicates
            num_duplicates = df_all_trades.duplicated(subset=['tx_hash']).sum()
            print(f"Number of duplicate tx_hash values in the concatenated dataframe: {num_duplicates}")
            print(f"Printing first 10 duplicates...")
            print(df_all_trades[df_all_trades.duplicated(subset=['tx_hash'])].head(10))

            # add a duplicate flag column to the concatenated dataframe
            print("\nDropping duplicates, keeping the row where resets == True from the concatenated dataframe...")
            # sort the dataframe by tx_hash and trade_timestamp ascending, then resets descending
            df_all_trades.sort_values(by=['tx_hash', 'trade_timestamp', 'resets'], ascending=[True, True, False], inplace=True)
            # drop duplicates, where resets == False
            df_all_trades.drop_duplicates(subset=['tx_hash'], keep='first', inplace=True)

            # confirm the duplicates have been dropped
            if df_all_trades.duplicated(subset=['tx_hash']).any():
                raise ValueError("Duplicates where resets == False have not been dropped. Exiting...")

            print("*********************************************************************************\n")
        else:
            print("No duplicates found in the concatenated dataframe.")

    except Exception as e:
        print(f"An unexpected error occurred: {type(e).__name__} - {e}")
        raise # program stops

    # count the number of trades between resets
    try:
        print("\nCalculating the number of trades between resets..")
        df_trades_with_reset_counts = calculate_trades_between_resets(df_all_trades)
    except ValueError as ve:
        print(f"Input Data Error for calculate_trades_between_resets function: {ve}")
        raise # program stops
    except Exception as e:
        print(f"An unexpected error occurred: {type(e).__name__} - {e}")
        raise # program stops

    if df_trades_with_reset_counts is not None:

        # print the first 5 rows of the dataframe
        print(f"\nConcatenated dataframe - all trades - with rows since last reset:")
        print(df_trades_with_reset_counts.head(5))
        print(df_trades_with_reset_counts.info())

        # capture the date range of the concatenated trades dataframe
        all_trades_date_begin = df_trades_with_reset_counts['trade_timestamp'].min()
        all_trades_date_end = df_trades_with_reset_counts['trade_timestamp'].max()
        print(f"\nDate range of all trades dataframe: {all_trades_date_begin} to {all_trades_date_end}")

        return df_trades_with_reset_counts

    else:
        print("\nNo resets found in the concatenated trades dataframe.")
        return None