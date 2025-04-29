import pandas as pd
import numpy as np

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
    print("The dataframe is the right object type and has the required columns. Continuing...")
    
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
    
# function to calculate the number of minutes between resets
def calculate_minutes_between_resets(df):
    """
    Calculates the time difference in minutes between consecutive rows
    where the 'resets' column is True, based on the 'trade_timestamp'.

    Args:
        df (pd.DataFrame): DataFrame containing 'trade_timestamp' and 'resets' columns.
                           'trade_timestamp' can be datetime objects, Unix timestamps (seconds),
                           or datetime strings.

    Returns:
        pd.DataFrame: A new DataFrame with the added 'minutes_since_last_reset' column,
                      or None if an error occurs. The column contains the difference in minutes
                      on rows where resets=True (NaN for the first reset). Other rows have NaN.
                      Returns the DataFrame with just the NaN column if no resets are found.
    """
    # confirm the passed variable is a dataframe
    if not isinstance(df, pd.DataFrame):
        raise ValueError("The input must be a pandas DataFrame")

    # confirm the required columns are present in the dataframe
    required_columns = ["trade_timestamp", "resets"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print("Cannot calculate the number of minutes between resets.")
        raise ValueError(f"The required columns are missing from the dataframe: {missing_columns}")

    print("Input DataFrame is valid and has required columns. Processing...")

    try:
        # Create a copy to avoid modifying the original DataFrame passed to the function
        df_copy = df.copy()

        # --- Step 1: Ensure 'trade_timestamp' is datetime ---
        # Check if the column is already a datetime type
        if not pd.api.types.is_datetime64_any_dtype(df_copy['trade_timestamp']):
            print("Converting 'trade_timestamp' to datetime format...")
            # Attempt conversion, trying numeric (assuming seconds) then standard strings
            try:
                # Try numeric conversion first (e.g., Unix timestamp in seconds)
                df_copy['trade_timestamp'] = pd.to_datetime(df_copy['trade_timestamp'], unit='s', errors='raise')
                print("Successfully converted from Unix timestamp (seconds).")
            except (ValueError, TypeError, OverflowError):
                # If numeric fails, try standard datetime string conversion
                print("Unix timestamp conversion failed or not applicable, trying standard datetime string conversion...")
                try:
                    df_copy['trade_timestamp'] = pd.to_datetime(df_copy['trade_timestamp'], errors='raise')
                    print("Successfully converted from datetime string.")
                except Exception as dt_err:
                    raise ValueError(f"Failed to convert 'trade_timestamp' to datetime. Original error: {dt_err}")

        # Check for NaT (Not a Time) values after conversion
        if df_copy['trade_timestamp'].isnull().any():
            raise ValueError("Found null values in 'trade_timestamp' after conversion. Please check data.")

        # --- Step 2: Sort by trade_timestamp ---
        print("Sorting DataFrame by 'trade_timestamp'...")
        # ignore_index=True resets the index after sorting, which is often cleaner,
        # but we need the original index to map results back, so we keep the original index.
        df_copy = df_copy.sort_values(by='trade_timestamp', ascending=True)

        # --- Step 3: Initialize the new column ---
        df_copy['minutes_since_last_reset'] = np.nan

        # --- Step 4: Filter rows where 'resets' is True ---
        # Ensure 'resets' is boolean, coerce if necessary (e.g., if it's 0/1)
        if not pd.api.types.is_bool_dtype(df_copy['resets']):
             print("Warning: 'resets' column is not boolean. Attempting to coerce.")
             try:
                 df_copy['resets'] = df_copy['resets'].astype(bool)
             except Exception as bool_err:
                 raise TypeError(f"Could not convert 'resets' column to boolean: {bool_err}")

        reset_rows = df_copy[df_copy['resets']].copy() # Use .copy() to avoid potential SettingWithCopyWarning

        # --- Step 5 & 6: Calculate difference and convert to minutes ---
        if not reset_rows.empty:
            print(f"Found {len(reset_rows)} reset points. Calculating time differences...")

            # Calculate the time difference between consecutive reset timestamps in the filtered subset
            # .diff() calculates the difference between the current row and the previous row
            time_diff = reset_rows['trade_timestamp'].diff() # This Series keeps the original index from df_copy

            # Convert the time difference (Timedelta object) to total minutes
            # .dt.total_seconds() gives float seconds, divide by 60 for minutes
            minutes_diff = time_diff.dt.total_seconds() / 60

            # --- Step 7: Assign results back to the original DataFrame copy ---
            # Use .loc with the index from 'minutes_diff' (which matches the reset rows in df_copy)
            # This assigns the calculated minutes to the 'minutes_since_last_reset' column
            # ONLY for the rows where 'resets' was True. The first reset row gets NaN from .diff().
            df_copy.loc[minutes_diff.index, 'minutes_since_last_reset'] = minutes_diff

            print("Finished calculating the number of minutes between resets.")
            return df_copy
        else:
            print("No rows found where 'resets' is True. Returning DataFrame with 'minutes_since_last_reset' column initialized to NaN.")
            # Return the df_copy even if no resets, it will have the NaN column
            return df_copy

    except Exception as e:
        print(f"An error occurred during calculation: {e}")
        # Optionally print traceback for debugging
        # import traceback
        # print(traceback.format_exc())
        return None # Indicate failure