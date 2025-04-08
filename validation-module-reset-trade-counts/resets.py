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
    required_columns = ["trade_timestamp","input_token", "output_token", "resets"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"The required columns are missing from the dataframe: {missing_columns}")
    
    try:
        # ensure the df is sorted descend by trade_timestamp
        df = df.sort_values(by='trade_timestamp', ascending=True, ignore_index=True)

        # get the index labels where 'resets' is True
        # This tells us how many rows total are between the start of one reset and the start of the next one.
        # Convert to Series to ensure .diff() works robustly
        reset_indices = df.index[df['resets']]

        if not reset_indices.empty:
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
            df['rows_since_last_reset'] = pd.NA

            # Assign the calculated counts to the corresponding reset rows in the new column.
            # The first reset row will have NA since diff() gives NA for the first element.
            df.loc[reset_indices, 'rows_since_last_reset'] = rows_between_count

            # Convert to nullable integer type for cleaner representation
            df['rows_since_last_reset'] = df['rows_since_last_reset'].astype(pd.Int64Dtype())

            return df
        
    except Exception as e:
        print(f"Error: {e}")
        return None
    