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

# check the model file contains the date/time and trade_count_btwn_resets columns
def check_model_file_columns(model_file_path, df_model):
    if 'date/time' not in df_model.columns:
        print(f"Error: date/time column not found in model file: {model_file_path}")
        return False
    if 'trade_count_btwn_resets' not in df_model.columns:
        print(f"Error: trade_count_btwn_resets column not found in model file: {model_file_path}")
        return False
    print(f"Model file contains the date/time and trade_count_btwn_resets columns")
    return True

# compare date ranges specified in start_date_str and end_date_str to the date range of the model file
def check_date_range(start_date_str, end_date_str, model_file_path, df_model):
    # find the date column in the model file
    date_column = df_model.columns[df_model.columns.str.contains('date/time', case=False)]
    print(f"date/time column found in model file {model_file_path}: {date_column}")

    # sort the df by the date column ascending
    df_model = df_model.sort_values(by=date_column, ascending=True)

    # get the date range of the model file
    date_range = df_model[date_column].iloc[0], df_model[date_column].iloc[-1]
    if not date_range:
        print(f"Error: date range of model file is not valid: {date_range}")
        return False
    
    # check if date_range is inside the start_date_str and end_date_str range
    # these are warnings; program will continue
    if date_range[0] > start_date_str:
        print(f"Warning: the date specified in start_date_str is before the model file data start date")
        print(f"The model file data start date {date_range[0]} is before the date specified in start_date_str {start_date_str}")
        print(f"Set the start_date_str to a date that is either the same as or after the model file data start date")
        return True
    if date_range[1] < end_date_str:
        print(f"Warning: the date specified in end_date_str is after the model file data end date")
        print(f"The model file data end date {date_range[1]} is after the date specified in end_date_str {end_date_str}")
        print(f"Set the end_date_str to a date that is either the same as or before the model file data end date")
        return True

    print(f"Date range of model file: {date_range}")
    return True