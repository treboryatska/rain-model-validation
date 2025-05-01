# this module takes as an input a subset of the orders from the output of main_batch.py
# the headers must be the same as the headers in the output of main_batch.py

import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from batch import get_aggregated_results
from check import check_aggregated_results
from stats import trade_count_between_resets_difference_test_subset
from charts import create_grouped_bar_chart

# get the aggregated results
subset_results_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTp30f3WibEMQHOO5SkBDrCjJFTem_0mXgnnTQHWAVZaqmr-S1DnW4Z4GRlBrQxjgZCzMNYscznxKKb/pub?gid=473707041&single=true&output=csv'

# tell the stats script where to output the stats results
today = datetime.now().strftime("%Y-%m-%d")
output_dir = "~/Downloads"
output_file_path = f"{output_dir}/subset_stats_results_{today}.csv"

# create the string path to the output directory -- required for saving chart pngs
output_dir_str = Path(output_dir).expanduser().resolve()

# we can use the same function to get the orders 
# url should point to the subset of the orders
orders = get_aggregated_results(subset_results_url)

if not orders:
    print("No orders found in the subset results")
    raise Exception("No orders found in the subset results")

# convert the orders to a pandas dataframe
subset_orders_df = pd.DataFrame(orders)

# check if orders_df is empty
if subset_orders_df.empty:
    print("No orders found in the subset results")
    raise Exception("No orders found in the subset results")

# confirm orders_df is valid: sample columns, sample size, and nulls in actual strategy results
# a warning about insufficient sample size is non-sensical for the subset run. Ignore. 
subset_orders_df_validity = check_aggregated_results(subset_orders_df)
print("Warnings about insufficient sample size are non-sensical for the subset run. Ignoring...")

if not subset_orders_df_validity:
    print("Orders dataframe is not valid. Exiting...")
    raise Exception("Orders dataframe is not valid. Exiting...")

# run the test
# are differences between modeled and actual trade count between resets 0?
subset_test_results = trade_count_between_resets_difference_test_subset(subset_orders_df)

if not subset_test_results:
    print("Test results are not valid. Exiting...")
    raise Exception("Test results are not valid. Exiting...")

# print the results
print(f"\nTest results for order subset: {subset_test_results}\n")

try:

    # convert the test results to a pandas dataframe
    subset_test_results_df = pd.DataFrame([subset_test_results])

    # print the df info
    print(f"\nTest results dataframe info:\n")
    print(subset_test_results_df.info())
    print(f"\nTest results dataframe:\n")
    print(subset_test_results_df.head())

    # save the results to a csv file
    subset_test_results_df.to_csv(output_file_path, index=False)

    print(f"\nSubset test results saved to {output_file_path}")
except Exception as e:
    print(f"\nError saving subset test results to {output_file_path}: {e}")
    raise Exception(f"Error saving subset test results to {output_file_path}: {e}")

##################################################################################################################################################################
# charts
##################################################################################################################################################################

# prepare the df for the chart; keep only the left 5 characters of the order_hash; df must be in long format
subset_chart_df = subset_orders_df[['target_order_hash', 'strategy_trade_count', 'model_output_auction_count', 'actual_reset_count', 'model_output_reset_count', 'actual_median_trade_count_between_resets', 'model_output_median_trade_count_between_resets', 'actual_average_trade_count_between_resets', 'model_output_average_trade_count_between_resets']].copy()
subset_chart_df['target_order_hash'] = subset_chart_df['target_order_hash'].str[:5]

# ################################################################ chart: 
# ############# DESCRIPTION: grouped vertical bar chart of strategy_trade_count and model_output_auction_count by target_order_hash
# ############# X AXIS: target_order_hash
# ############# Y AXIS: strategy_trade_count and model_output_auction_count
# ############# DF: order_hash and strategy_trade_count and model_output_auction_count
# ################################################################

# Use melt to transform from wide to long format
auction_counts_long_chart_df = pd.melt(
    subset_chart_df,
    id_vars=['target_order_hash'],  # Column(s) to keep as identifiers
    value_vars=['strategy_trade_count', 'model_output_auction_count'], # Columns to unpivot
    var_name='metric_type',  # Name of the new column holding 'strategy_trade_count'/'model_output_auction_count'
    value_name='auction_count' # Name of the new column holding the corresponding values
)

# Clean up the 'metric_type' column values
auction_counts_long_chart_df['metric_type'] = auction_counts_long_chart_df['metric_type'].replace({
    'strategy_trade_count': 'Actual',
    'model_output_auction_count': 'Modeled'
})

fig, ax = create_grouped_bar_chart(
    df=auction_counts_long_chart_df,
    category_column='target_order_hash',
    value_column='auction_count',
    group_column='metric_type',
    title='Auction Counts by Target Order Hash',
    xlabel='Target Order Hash',
    ylabel='Auction Count',
    figsize=(10, 6)
)

# save the chart
filename = "grouped_bar_chart_actual_vs_modeled_auction_count_subset.png"
save_path = output_dir_str / filename
print(f"Saving grouped bar chart to: {output_dir}/{filename}")
# plt.show() # Show plot interactively
fig.savefig(save_path)

# ################################################################ chart: 
# ############# DESCRIPTION: grouped vertical bar chart of actual_reset_count and model_output_reset_count by target_order_hash
# ############# X AXIS: target_order_hash
# ############# Y AXIS: actual_reset_count and model_output_reset_count
# ############# DF: order_hash and actual_reset_count and model_output_reset_count
# ################################################################

# Use melt to transform from wide to long format
reset_counts_long_chart_df = pd.melt(
    subset_chart_df,
    id_vars=['target_order_hash'],  # Column(s) to keep as identifiers
    value_vars=['actual_reset_count', 'model_output_reset_count'], # Columns to unpivot
    var_name='metric_type',  # Name of the new column holding 'actual_reset_count'/'model_output_reset_count'
    value_name='reset_count' # Name of the new column holding the corresponding values
)

# Clean up the 'metric_type' column values
reset_counts_long_chart_df['metric_type'] = reset_counts_long_chart_df['metric_type'].replace({
    'actual_reset_count': 'Actual',
    'model_output_reset_count': 'Modeled'
})

fig, ax = create_grouped_bar_chart(
    df=reset_counts_long_chart_df,
    category_column='target_order_hash',
    value_column='reset_count',
    group_column='metric_type',
    title='Reset Counts by Target Order Hash',
    xlabel='Target Order Hash',
    ylabel='Reset Count',
    figsize=(10, 6)
)

# save the chart
filename = "grouped_bar_chart_actual_vs_modeled_reset_count_subset.png"
save_path = output_dir_str / filename
print(f"Saving grouped bar chart to: {output_dir}/{filename}")
# plt.show() # Show plot interactively
fig.savefig(save_path)

# ################################################################ chart: 
# ############# DESCRIPTION: grouped vertical bar chart of actual_median_trade_count_between_resets and model_output_median_trade_count_between_resets by target_order_hash
# ############# X AXIS: target_order_hash
# ############# Y AXIS: actual_median_trade_count_between_resets and model_output_median_trade_count_between_resets
# ############# DF: order_hash and actual_median_trade_count_between_resets and model_output_median_trade_count_between_resets
# ################################################################

# Use melt to transform from wide to long format
reset_counts_long_chart_df = pd.melt(
    subset_chart_df,
    id_vars=['target_order_hash'],  # Column(s) to keep as identifiers
    value_vars=['actual_median_trade_count_between_resets', 'model_output_median_trade_count_between_resets'], # Columns to unpivot
    var_name='metric_type',  # Name of the new column holding 'actual_median_trade_count_between_resets'/'model_output_median_trade_count_between_resets'
    value_name='median_trade_count_between_resets' # Name of the new column holding the corresponding values
)

# Clean up the 'metric_type' column values
reset_counts_long_chart_df['metric_type'] = reset_counts_long_chart_df['metric_type'].replace({
    'actual_median_trade_count_between_resets': 'Actual',
    'model_output_median_trade_count_between_resets': 'Modeled'
})

fig, ax = create_grouped_bar_chart(
    df=reset_counts_long_chart_df,
    category_column='target_order_hash',
    value_column='median_trade_count_between_resets',
    group_column='metric_type',
    title='Median Trade Count Between Resets by Target Order Hash',
    xlabel='Target Order Hash',
    ylabel='Median Trade Count Between Resets',
    figsize=(10, 6)
)

# save the chart
filename = "grouped_bar_chart_actual_vs_modeled_median_trade_count_between_resets_subset.png"
save_path = output_dir_str / filename
print(f"Saving grouped bar chart to: {output_dir}/{filename}")
# plt.show() # Show plot interactively
fig.savefig(save_path)

# ################################################################ chart: 
# ############# DESCRIPTION: grouped vertical bar chart of actual_average_trade_count_between_resets and model_output_average_trade_count_between_resets by target_order_hash
# ############# X AXIS: target_order_hash
# ############# Y AXIS: actual_average_trade_count_between_resets and model_output_average_trade_count_between_resets
# ############# DF: order_hash and actual_average_trade_count_between_resets and model_output_average_trade_count_between_resets
# ################################################################

# Use melt to transform from wide to long format
reset_counts_long_chart_df = pd.melt(
    subset_chart_df,
    id_vars=['target_order_hash'],  # Column(s) to keep as identifiers
    value_vars=['actual_average_trade_count_between_resets', 'model_output_average_trade_count_between_resets'], # Columns to unpivot
    var_name='metric_type',  # Name of the new column holding 'actual_average_trade_count_between_resets'/'model_output_average_trade_count_between_resets'
    value_name='average_trade_count_between_resets' # Name of the new column holding the corresponding values
)

# Clean up the 'metric_type' column values
reset_counts_long_chart_df['metric_type'] = reset_counts_long_chart_df['metric_type'].replace({
    'actual_average_trade_count_between_resets': 'Actual',
    'model_output_average_trade_count_between_resets': 'Modeled'
})

fig, ax = create_grouped_bar_chart(
    df=reset_counts_long_chart_df,
    category_column='target_order_hash',
    value_column='average_trade_count_between_resets',
    group_column='metric_type',
    title='Average Trade Count Between Resets by Target Order Hash',
    xlabel='Target Order Hash',
    ylabel='Average Trade Count Between Resets',
    figsize=(10, 6)
)

# save the chart
filename = "grouped_bar_chart_actual_vs_modeled_average_trade_count_between_resets_subset.png"
save_path = output_dir_str / filename
print(f"Saving grouped bar chart to: {output_dir}/{filename}")
# plt.show() # Show plot interactively
fig.savefig(save_path)