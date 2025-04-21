import os
import pandas as pd
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

# check the model file contains the date/time and trade_count_in_reset columns
def check_model_output_file_columns(model_output_file_path, df_model):
    # check if the date/time column is in the model file
    date_time_column = df_model.columns[df_model.columns.str.contains('date/time', case=False)]
    if date_time_column.empty:
        print(f"\nError: date/time column not found in model file: {model_output_file_path}")
        return False
    # check if the trade_count_in_reset column is in the model file
    trade_count_in_reset_column = df_model.columns[df_model.columns.str.contains('trade_count_in_reset', case=False)]
    if trade_count_in_reset_column.empty:
        print(f"\nError: trade_count_in_reset column not found in model file: {model_output_file_path}")
        return False
    print(f"Model file contains the date/time and trade_count_in_reset columns")
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
    
    # check that Date/time and trade_count_in_reset exist in the model file
    if 'Date/time' not in df_model.columns:
        print(f"Error: Date/time column not found in model file")
        return False
    if 'trade_count_in_reset' not in df_model.columns:
        print(f"Error: trade_count_in_reset column not found in model output data file")
        return False
    
    # rename Date/time to datetime
    df_model.rename(columns={'Date/time': 'datetime'}, inplace=True)

    # there should only be two columns in the model file: Date/time and trade_count_in_reset
    if len(df_model.columns) != 2:
        print(f"found {len(df_model.columns)} columns in the model output data file. It should have 2 columns: Date/time and trade_count_in_reset")
        print(f"dropping all columns except Date/time and trade_count_in_reset...\n")
        df_model = df_model[['datetime', 'trade_count_in_reset']].copy()

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

    # coerce the trade_count_in_reset column to an integer
    if df_model['trade_count_in_reset'].dtype != 'int64':

        print(f"trade_count_in_reset column is not an integer. Coercing to integer...\n")
        print("First convert the column to str; this allows us to deal with comma separated values")
        df_model['trade_count_in_reset'] = df_model['trade_count_in_reset'].astype(str)
        print("Replacing commas with empty strings...\n")
        df_model['trade_count_in_reset'] = df_model['trade_count_in_reset'].str.replace(',', '', regex=False)
        print("Converting to numeric...\n")

        # coerce the trade_count_in_reset column to numeric; round to handle any decimals since they are irrelevant
        df_model['trade_count_in_reset'] = pd.to_numeric(df_model['trade_count_in_reset'], errors='coerce').round()

        # check if there are null values in the trade_count_in_reset column
        if df_model['trade_count_in_reset'].isnull().any():
            null_count_model_trades = df_model['trade_count_in_reset'].isnull().sum()
            print(f"found {null_count_model_trades} nulls in the trade_count_in_reset column. Leaving nulls.")
        #     df_model['trade_count_in_reset'].fillna(value=0, inplace=True)

        df_model['trade_count_in_reset'] = df_model['trade_count_in_reset'].astype('Int64')

        print(f"trade_count_in_reset column converted to an integer")
    else:
        print(f"trade_count_in_reset column is an integer")

    # print the column and row count of the model file
    print(f"----- \nModel output data file shape after cleaning: \nColumn count: {len(df_model.columns)} \nRow count: {len(df_model)} \n-----\n")

    return df_model


