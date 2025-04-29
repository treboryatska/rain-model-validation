import os
import pandas as pd
import warnings
# check validation script input files for consistency

# check the model_file path appears valid
def check_model_file_path(model_file_path):
    if not os.path.exists(model_file_path):
        print(f"Error: model_file_path does not exist: {model_file_path}")
        return False
    # check the model_file is a csv file
    if not model_file_path.endswith(".csv"):
        print(f"Error: model_file_path is not a csv file: {model_file_path}")
        return False
    # check the model_file is not empty
    if os.path.getsize(model_file_path) == 0:
        print(f"Error: model_file_path is empty: {model_file_path}")
        return False
    print(f"Model file path appears valid: {model_file_path}")
    return True

# check the model input file contains the tx_hash and timestamp columns
def check_model_input_file_columns(model_input_file_path, df_market_trades):
    tx_hash_column = df_market_trades.columns[df_market_trades.columns.str.contains('tx_hash', case=False)]
    if tx_hash_column.empty:
        print(f"Error: tx_hash column not found in model input file: {model_input_file_path}")
        return False
    timestamp_column = df_market_trades.columns[df_market_trades.columns.str.contains('timestamp', case=False)]
    if timestamp_column.empty:
        print(f"Error: timestamp column not found in model input file: {model_input_file_path}")
        return False
    print(f"Model input file contains the tx_hash and timestamp columns")
    return True

# check the model file contains the date/time and auction_count_in_reset columns
def check_model_output_file_columns(model_output_file_path, df_model):
    # check if the date/time column is in the model file
    date_time_column = df_model.columns[df_model.columns.str.contains('date/time', case=False)]
    if date_time_column.empty:
        print(f"\nError: date/time column not found in model file: {model_output_file_path}")
        return False
    # check if the auction_count_in_reset column is in the model file
    auction_count_in_reset_column = df_model.columns[df_model.columns.str.contains('auction_count_in_reset', case=False)]
    if auction_count_in_reset_column.empty:
        print(f"\nError: auction_count_in_reset column not found in model file: {model_output_file_path}")
        return False
    print(f"Model file contains the date/time and auction_count_in_reset columns")
    return True

# clean the model input file
def clean_model_input_file(df_model):

    # print the column and row count of the model file
    print(f"----- \nInitial model file shape: \nColumn count: {len(df_model.columns)} \nRow count: {len(df_model)} \n-----\n")
    
    # check that tx_hash and timestamp exist in the model file
    if 'tx_hash' not in df_model.columns:
        print(f"Error: tx_hash column not found in model file")
        return False
    if 'timestamp' not in df_model.columns:
        print(f"Error: timestamp column not found in model file")
        return False
    
    # rename timestamp to datetime
    df_model.rename(columns={'timestamp': 'datetime'}, inplace=True)

    # there should only be two columns in the model file: tx_hash and datetime
    if len(df_model.columns) != 2:
        print(f"found {len(df_model.columns)} columns in the model input data file. It should have 2 columns: tx_hash and datetime")
        print(f"dropping all columns except tx_hash and datetime...\n")
        df_model = df_model[['tx_hash', 'datetime']].copy()

    # coerce the datetime column to a datetime object
    if df_model['datetime'].dtype != 'datetime64[ns]':
        # track if null count increases after coercion
        null_count_before_datetime_coercion = df_model['datetime'].isnull().sum()

        print(f"datetime column is not a datetime object. the datetime column is type: {df_model['datetime'].dtype}. Coercing to datetime...\n")

        print(f"----- \nModel input data file shape before coercion: \nColumn count: {len(df_model.columns)} \nRow count: {len(df_model)} \n-----\n")

        # convert to datetime object
        df_model['datetime'] = pd.to_datetime(
            df_model['datetime'], 
            unit='s',
            errors='coerce')

        print(f"----- \nModel input data file shape after coercion: \nColumn count: {len(df_model.columns)} \nRow count: {len(df_model)} \n-----\n")
        null_count_after_datetime_coercion = df_model['datetime'].isnull().sum()
        if null_count_after_datetime_coercion != null_count_before_datetime_coercion:
            print(f"null count after coercion: {null_count_after_datetime_coercion}")
            print(f"{null_count_after_datetime_coercion - null_count_before_datetime_coercion} datetime values could not be parsed. Setting to NaT")
    else:
        print(f"datetime column is a datetime object")

    # print the column and row count of the model file
    print(f"----- \nModel input data file shape after cleaning: \nColumn count: {len(df_model.columns)} \nRow count: {len(df_model)} \n-----\n")

    return df_model

# clean the model file
def clean_model_output_file(df_model):

    # print the column and row count of the model file
    print(f"----- \nInitial model output data file shape: \nColumn count: {len(df_model.columns)} \nRow count: {len(df_model)} \n-----\n")
    
    # check that Date/time and auction_count_in_reset exist in the model file
    if 'Date/time' not in df_model.columns:
        print(f"Error: Date/time column not found in model file")
        return False
    if 'auction_count_in_reset' not in df_model.columns:
        print(f"Error: auction_count_in_reset column not found in model output data file")
        return False
    
    # rename Date/time to datetime
    df_model.rename(columns={'Date/time': 'datetime'}, inplace=True)

    # there should only be two columns in the model file: Date/time and auction_count_in_reset
    if len(df_model.columns) != 2:
        print(f"found {len(df_model.columns)} columns in the model output data file. It should have 2 columns: Date/time and auction_count_in_reset")
        print(f"dropping all columns except Date/time and auction_count_in_reset...\n")
        df_model = df_model[['datetime', 'auction_count_in_reset']].copy()

    # coerce the datetime column to a datetime object
    if df_model['datetime'].dtype != 'datetime64[ns]':
        # track if null count increases after coercion
        null_count_before_datetime_coercion = df_model['datetime'].isnull().sum()

        print(f"datetime column is not a datetime object. the datetime column is type: {df_model['datetime'].dtype}. Coercing to datetime...\n")

        print(f"----- \nModel output data file shape before coercion: \nColumn count: {len(df_model.columns)} \nRow count: {len(df_model)} \n-----\n")

        # convert to datetime object
        df_model['datetime'] = pd.to_datetime(
            df_model['datetime'], 
            format='%d/%m/%Y %H:%M:%S',
            errors='coerce')

        print(f"----- \nModel output data file shape after coercion: \nColumn count: {len(df_model.columns)} \nRow count: {len(df_model)} \n-----\n")
        null_count_after_datetime_coercion = df_model['datetime'].isnull().sum()
        if null_count_after_datetime_coercion != null_count_before_datetime_coercion:
            print(f"null count after coercion: {null_count_after_datetime_coercion}")
            print(f"{null_count_after_datetime_coercion - null_count_before_datetime_coercion} datetime values could not be parsed. Setting to NaT")
    else:
        print(f"datetime column is a datetime object")

    # coerce the auction_count_in_reset column to an integer
    if df_model['auction_count_in_reset'].dtype != 'int64':

        print(f"auction_count_in_reset column is not an integer. Coercing to integer...\n")
        print("First convert the column to str; this allows us to deal with comma separated values")
        df_model['auction_count_in_reset'] = df_model['auction_count_in_reset'].astype(str)
        print("Replacing commas with empty strings...\n")
        df_model['auction_count_in_reset'] = df_model['auction_count_in_reset'].str.replace(',', '', regex=False)
        print("Converting to numeric...\n")

        # coerce the auction_count_in_reset column to numeric; round to handle any decimals since they are irrelevant
        df_model['auction_count_in_reset'] = pd.to_numeric(df_model['auction_count_in_reset'], errors='coerce').round()

        # check if there are null values in the auction_count_in_reset column
        if df_model['auction_count_in_reset'].isnull().any():
            null_count_model_trades = df_model['auction_count_in_reset'].isnull().sum()
            print(f"found {null_count_model_trades} nulls in the auction_count_in_reset column. Leaving nulls.")
        #     df_model['auction_count_in_reset'].fillna(value=0, inplace=True)

        df_model['auction_count_in_reset'] = df_model['auction_count_in_reset'].astype('Int64')

        print(f"auction_count_in_reset column converted to an integer")
    else:
        print(f"auction_count_in_reset column is an integer")

    # print the column and row count of the model file
    print(f"----- \nModel output data file shape after cleaning: \nColumn count: {len(df_model.columns)} \nRow count: {len(df_model)} \n-----\n")

    return df_model


# fail main_stats.py if columns are missing from the aggregated results
# warn if record counts are less than 15 for each model version
# fail if nulls in actual strategy results
def check_aggregated_results(orders_df):

    # check that orders_df is a dataframe
    if not isinstance(orders_df, pd.DataFrame):
        print("orders_df is not a dataframe")
        raise Exception("orders_df is not a dataframe")
    
    # check if the orders are empty
    if orders_df.empty:
        print("No orders found in the aggregated results")
        raise Exception("No orders found in the aggregated results")
    
    # check if a sample of the columns are present
    print(f"\nChecking a sample of columns are present in aggregated result file to confirm we have the correct file...")
    column_list = ["model_view_url",    
                "target_order_hash",
                "model_version",
                "network",
                "start_date_str",
                "end_date_str",
                "model_input_trade_count",
                "strategy_trade_count",
                "actual_reset_count", 
                "actual_median_trade_count_between_resets", 
                "actual_average_trade_count_between_resets", 
                "actual_std_trade_count_between_resets",
                "median_trade_count_difference_modeled_vs_actual",   
                "average_trade_count_difference_modeled_vs_actual",
                "std_trade_count_difference_modeled_vs_actual",
                "reset_count_difference_modeled_vs_actual",
                ]

    # Convert column_list and the DataFrame columns to sets
    required_columns = set(column_list)
    actual_columns = set(orders_df.columns)

    # Check if all required columns are present in the actual columns
    if not required_columns.issubset(actual_columns):
        # Find which columns are missing for a more informative error message
        missing_columns = required_columns - actual_columns # Set difference
        print(f"Error: The following required columns are missing from the DataFrame: {list(missing_columns)}")
        # raise an error
        raise Exception(f"The following required columns are missing from the DataFrame: {list(missing_columns)}")
    else:
        print("All required columns are present. Appears to be a valid aggregated results file.")

    # check if the record count is less than 15 for each model version
    print(f"\nChecking if the record count is less than 15 for each model version...")
    print(f"Model versions found in aggregated results: {orders_df['model_version'].unique()}")
    sample_size = True
    for model_version in orders_df['model_version'].unique():
        model_version_orders = orders_df[orders_df['model_version'] == model_version]
        if len(model_version_orders) < 15:
            warning_message = (f"Warning: The number of records for model version {model_version} is {len(model_version_orders)}. "
                            f"This may be too low for meaningful conclusions.")
            print(warning_message) 
            warnings.warn(warning_message, UserWarning) # Use warnings.warn()
            sample_size = False
    if sample_size:
        print(f"All model versions have more than 15 records.")

    # check if nulls in actual strategy results
    print(f"\nChecking if there are nulls in the actual strategy results...")
    strategy_columns = ["actual_reset_count", "actual_median_trade_count_between_resets", "actual_average_trade_count_between_resets", "actual_std_trade_count_between_resets"]
    for strategy_column in strategy_columns:
        if orders_df[strategy_column].isnull().any():
            # fail if nulls in actual strategy results
            raise Exception(f"There are nulls in the {strategy_column} column.")
    print(f"No nulls in the actual strategy results.\n")
    
    return True