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
    
# function to calculate the number of minutes between executed auctions
def calculate_minutes_between_executed_auctions(timestamp_series):
    """
    Calculates the time difference in minutes between consecutive timestamps in a Series.

    Args:
        timestamp_series (pd.Series): Series containing datetime-like values.

    Returns:
        pd.Series: A Series containing the difference in minutes between consecutive
                   timestamps (aligned to the original index of the later timestamp).
                   Returns None if an error occurs.
    """
    if not isinstance(timestamp_series, pd.Series):
        raise TypeError("The input must be a pandas Series")

    print("Input Series is valid. Processing...")

    try:
        # Create a copy to avoid modifying the original series passed in
        series_copy = timestamp_series.copy()

        # --- Step 1: Ensure series values are datetime ---
        if not pd.api.types.is_datetime64_any_dtype(series_copy):
            print("Converting Series to datetime format...")
            try:
                series_copy = pd.to_datetime(series_copy, unit='s', errors='raise')
                print("Successfully converted from Unix timestamp (seconds).")
            except (ValueError, TypeError, OverflowError):
                print("Unix timestamp conversion failed or not applicable, trying standard datetime string conversion...")
                try:
                    series_copy = pd.to_datetime(series_copy, errors='raise')
                    print("Successfully converted from datetime string.")
                except Exception as dt_err:
                    raise ValueError(f"Failed to convert Series to datetime. Original error: {dt_err}")

        if series_copy.isnull().any():
            raise ValueError("Found null values in Series after conversion. Please check data.")

        # --- Step 2: Sort by timestamp value ---
        print("Sorting Series by timestamp...")
        series_sorted = series_copy.sort_values(ascending=True) # Sort the values

        # --- Step 3: Calculate difference ---
        # .diff() calculates difference from the PREVIOUS row in the sorted series
        time_diff = series_sorted.diff() # This Series keeps the original index

        # --- Step 4: Convert to minutes ---
        minutes_diff = time_diff.dt.total_seconds() / 60
        minutes_diff.name = 'minutes_since_last_executed_auction' # Give the result series a name

        print("finished calculating the number of minutes between executed auctions")
        return minutes_diff # Return the Series of differences (with original index)

    except Exception as e:
        print(f"An error occurred during calculation: {e}")
        import traceback
        print(traceback.format_exc())
        return None