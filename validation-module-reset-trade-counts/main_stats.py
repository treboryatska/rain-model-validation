# main script to run the stats from aggregated results, previously created using main_batch.py
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from batch import get_aggregated_results
from stats import trade_count_between_resets_difference_test
from check import check_aggregated_results
from charts import (
    create_scatter_plot, 
    create_faceted_histogram, 
    create_qq_plot, 
    create_line_chart, 
    create_horizontal_bar_chart,
    create_grouped_bar_chart,
    create_faceted_grouped_bar_chart
)

# get the aggregated results
aggregated_results_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTp30f3WibEMQHOO5SkBDrCjJFTem_0mXgnnTQHWAVZaqmr-S1DnW4Z4GRlBrQxjgZCzMNYscznxKKb/pub?gid=2145683509&single=true&output=csv'

# tell the stats script where to output the stats results
today = datetime.now().strftime("%Y-%m-%d")
output_dir = "~/Downloads"
output_file_path = f"{output_dir}/stats_results_{today}.csv"

# create the string path to the output directory -- required for saving chart pngs
output_dir_str = Path(output_dir).expanduser().resolve()

orders = get_aggregated_results(aggregated_results_url)

if not orders:
    print("No orders found in the aggregated results")
    raise Exception("No orders found in the aggregated results")

# convert the orders to a pandas dataframe
orders_df = pd.DataFrame(orders)

# check if orders_df is empty
if orders_df.empty:
    print("No orders found in the aggregated results")
    raise Exception("No orders found in the aggregated results")

# confirm orders_df is valid: sample columns, sample size, and nulls in actual strategy results
orders_df_validity = check_aggregated_results(orders_df)

if not orders_df_validity:
    print("Orders dataframe is not valid. Exiting...")
    raise Exception("Orders dataframe is not valid. Exiting...")

# run the test
# are differences between modeled and actual trade count between resets 0?
test_results = trade_count_between_resets_difference_test(orders_df)

if not test_results:
    print("Test results are not valid. Exiting...")
    raise Exception("Test results are not valid. Exiting...")

# print the results
print(f"\nTest results: {test_results}\n")

try:

    # convert the test results to a pandas dataframe
    test_results_df = pd.DataFrame.from_dict(test_results, orient='index').reset_index().rename(columns={'index': 'model_version'})

    # print the df info
    print(f"\nTest results dataframe info:\n")
    print(test_results_df.info())
    print(f"\nTest results dataframe:\n")
    print(test_results_df.head())

    # save the results to a csv file
    test_results_df.to_csv(output_file_path, index=False)

    print(f"\nTest results saved to {output_file_path}")
except Exception as e:
    print(f"\nError saving test results to {output_file_path}: {e}")
    raise Exception(f"Error saving test results to {output_file_path}: {e}")

##################################################################################################################################################################
# charts
##################################################################################################################################################################
print("\nGenerating charts...")

# print info about the orders_df
print(f"\nOrders dataframe info:\n")
print(orders_df.info())

# define color map for actual vs modeled
metric_color_map = {
    'Modeled': '#4C72B0',  # Muted blue/teal
    'Actual': '#55A868'   # Medium green
}

# ################################################################ chart: 
# ############# DESCRIPTION: horizontal bar chart of actual_median_minutes_between_executed_auctions by model_version
# ############# X AXIS: actual_median_minutes_between_executed_auctions
# ############# Y AXIS: order_hash
# ############# DF: distinct order_hash and actual_median_minutes_between_executed_auctions
# ################################################################
# prepare the df for the chart; keep only the left 5 characters of the order_hash
minutes_between_resets_chart_df = orders_df[['target_order_hash', 'actual_median_minutes_between_executed_auctions', 'actual_average_minutes_between_executed_auctions']].drop_duplicates()
minutes_between_resets_chart_df['target_order_hash'] = minutes_between_resets_chart_df['target_order_hash'].str[:5]
try:
    g_actual_median_minutes_between_executed_auctions_fig, g_actual_median_minutes_between_executed_auctions_ax = create_horizontal_bar_chart(
        df=minutes_between_resets_chart_df,
        category_column='target_order_hash',
        value_column='actual_median_minutes_between_executed_auctions',
        title='Actual Median Minutes Between Executed Auctions',
    )
    filename = "horizontal_bar_chart_actual_median_minutes_between_executed_auctions.png"
    save_path = output_dir_str / filename
    print(f"Saving horizontal bar chart to: {output_dir}/{filename}")
    # plt.show() # Show plot interactively
    g_actual_median_minutes_between_executed_auctions_fig.savefig(save_path)
except Exception as e:
    print(f"\nError plotting horizontal bar chart: {e}")
    raise Exception(f"Error plotting horizontal bar chart: {e}")

# ################################################################ chart: 
# ############# DESCRIPTION: horizontal bar chart of actual_average_minutes_between_executed_auctions by model_version
# ############# X AXIS: actual_average_minutes_between_executed_auctions
# ############# Y AXIS: order_hash
# ############# DF: distinct order_hash and actual_average_minutes_between_executed_auctions
# ################################################################
# prepare the df for the chart; keep only the left 5 characters of the order_hash
try:
    g_actual_average_minutes_between_executed_auctions_fig, g_actual_average_minutes_between_executed_auctions_ax = create_horizontal_bar_chart(
        df=minutes_between_resets_chart_df,
        category_column='target_order_hash',
        value_column='actual_average_minutes_between_executed_auctions',
        title='Actual Average Minutes Between Executed Auctions',
    )
    filename = "horizontal_bar_chart_actual_average_minutes_between_executed_auctions.png"
    save_path = output_dir_str / filename
    print(f"Saving horizontal bar chart to: {output_dir}/{filename}")
    # plt.show() # Show plot interactively
    g_actual_average_minutes_between_executed_auctions_fig.savefig(save_path)
except Exception as e:
    print(f"\nError plotting horizontal bar chart: {e}")
    raise Exception(f"Error plotting horizontal bar chart: {e}")

# ################################################################ chart: 
# ############# DESCRIPTION: grouped vertical bar chart of strategy_trade_count and model_output_auction_count by target_order_hash
# ############# X AXIS: target_order_hash
# ############# Y AXIS: strategy_trade_count and model_output_auction_count
# ############# DF: order_hash and strategy_trade_count and model_output_auction_count
# ################################################################

# prepare the df for the chart; keep only the left 5 characters of the order_hash; df must be in long format
auction_counts_chart_df = orders_df[['target_order_hash', 'model_version', 'strategy_trade_count', 'model_output_auction_count']].copy()
auction_counts_chart_df['target_order_hash'] = auction_counts_chart_df['target_order_hash'].str[:5]

# Use melt to transform from wide to long format
auction_counts_long_chart_df = pd.melt(
    auction_counts_chart_df,
    id_vars=['target_order_hash', 'model_version'],  # Column(s) to keep as identifiers
    value_vars=['strategy_trade_count', 'model_output_auction_count'], # Columns to unpivot
    var_name='metric_type',  # Name of the new column holding 'strategy_trade_count'/'model_output_auction_count'
    value_name='auction_count' # Name of the new column holding the corresponding values
)

# Clean up the 'metric_type' column values
auction_counts_long_chart_df['metric_type'] = auction_counts_long_chart_df['metric_type'].replace({
    'strategy_trade_count': 'Actual',
    'model_output_auction_count': 'Modeled'
})

try:
    facet_grid = create_faceted_grouped_bar_chart(
        df=auction_counts_long_chart_df,
        category_column='target_order_hash',
        value_column='auction_count',
        group_column='metric_type',
        facet_column='model_version', # Create subplots for each model version
        facet_wrap=3, # Arrange facets in 3 columns
        title='Actual vs. Modeled Auction Counts by Model Version',
        sharey=False, # Allow different y-axes (categories) per facet
        palette=metric_color_map
    )
    filename = "grouped_bar_chart_actual_vs_modeled_auction_count.png"
    save_path = output_dir_str / filename
    print(f"Saving grouped bar chart to: {output_dir}/{filename}")
    # plt.show() # Show plot interactively
    facet_grid.savefig(save_path)
except Exception as e:
    print(f"\nError plotting grouped bar chart: {e}")
    raise Exception(f"Error plotting grouped bar chart: {e}")

# ################################################################ chart: 
# ############# DESCRIPTION: grouped vertical bar chart of actual_reset_count and model_output_reset_count by target_order_hash
# ############# X AXIS: target_order_hash
# ############# Y AXIS: actual_reset_count and model_output_reset_count
# ############# DF: order_hash and actual_reset_count and model_output_reset_count
# ################################################################

# prepare the df for the chart; keep only the left 5 characters of the order_hash; df must be in long format
reset_counts_chart_df = orders_df[['target_order_hash', 'model_version', 'actual_reset_count', 'model_output_reset_count']].copy()
reset_counts_chart_df['target_order_hash'] = reset_counts_chart_df['target_order_hash'].str[:5]

# Use melt to transform from wide to long format
reset_counts_long_chart_df = pd.melt(
    reset_counts_chart_df,
    id_vars=['target_order_hash', 'model_version'],  # Column(s) to keep as identifiers
    value_vars=['actual_reset_count', 'model_output_reset_count'], # Columns to unpivot
    var_name='metric_type',  # Name of the new column holding 'actual_reset_count'/'model_output_reset_count'
    value_name='reset_count' # Name of the new column holding the corresponding values
)

# Clean up the 'metric_type' column values
reset_counts_long_chart_df['metric_type'] = reset_counts_long_chart_df['metric_type'].replace({
    'actual_reset_count': 'Actual',
    'model_output_reset_count': 'Modeled'
})

try:
    facet_grid = create_faceted_grouped_bar_chart(
        df=reset_counts_long_chart_df,
        category_column='target_order_hash',
        value_column='reset_count',
        group_column='metric_type',
        facet_column='model_version', # Create subplots for each model version
        facet_wrap=3, # Arrange facets in 3 columns
        title='Actual vs. Modeled Reset Counts by Model Version',
        sharey=False, # Allow different y-axes (categories) per facet
        palette=metric_color_map
    )
    filename = "grouped_bar_chart_actual_vs_modeled_reset_count.png"
    save_path = output_dir_str / filename
    print(f"Saving grouped bar chart to: {output_dir}/{filename}")
    # plt.show() # Show plot interactively
    facet_grid.savefig(save_path)
except Exception as e:
    print(f"\nError plotting grouped bar chart: {e}")
    raise Exception(f"Error plotting grouped bar chart: {e}")

# ################################################################ chart: 
# ############# DESCRIPTION: grouped vertical bar chart of actual_median_trade_count_between_resets and model_output_median_trade_count_between_resets by target_order_hash
# ############# X AXIS: target_order_hash
# ############# Y AXIS: actual_median_trade_count_between_resets and model_output_median_trade_count_between_resets
# ############# DF: order_hash and actual_median_trade_count_between_resets and model_output_median_trade_count_between_resets
# ################################################################
# prepare the df for the chart; keep only the left 5 characters of the order_hash; df must be in long format
reset_counts_chart_df = orders_df[['target_order_hash', 'model_version', 'actual_median_trade_count_between_resets', 'model_output_median_trade_count_between_resets','model_output_average_trade_count_between_resets','actual_average_trade_count_between_resets']].copy()
reset_counts_chart_df['target_order_hash'] = reset_counts_chart_df['target_order_hash'].str[:5]

# Use melt to transform from wide to long format
reset_counts_median_long_chart_df = pd.melt(
    reset_counts_chart_df,
    id_vars=['target_order_hash', 'model_version'],  # Column(s) to keep as identifiers
    value_vars=['actual_median_trade_count_between_resets', 'model_output_median_trade_count_between_resets'], # Columns to unpivot
    var_name='metric_type',  # Name of the new column holding 'actual_median_trade_count_between_resets'/'model_output_median_trade_count_between_resets'
    value_name='median_auction_count_between_resets' # Name of the new column holding the corresponding values
)

# Clean up the 'metric_type' column values
reset_counts_median_long_chart_df['metric_type'] = reset_counts_median_long_chart_df['metric_type'].replace({
    'actual_median_trade_count_between_resets': 'Actual',
    'model_output_median_trade_count_between_resets': 'Modeled'
})

try:
    facet_grid = create_faceted_grouped_bar_chart(
        df=reset_counts_median_long_chart_df,
        category_column='target_order_hash',
        value_column='median_auction_count_between_resets',
        group_column='metric_type',
        facet_column='model_version', # Create subplots for each model version
        facet_wrap=3, # Arrange facets in 3 columns
        title='Actual vs. Modeled Median Auction Count Between Resets by Model Version',
        sharey=False, # Allow different y-axes (categories) per facet
        palette=metric_color_map
    )
    filename = "grouped_bar_chart_actual_vs_modeled_median_auction_count_between_resets.png"
    save_path = output_dir_str / filename
    print(f"Saving grouped bar chart to: {output_dir}/{filename}")
    # plt.show() # Show plot interactively
    facet_grid.savefig(save_path)
except Exception as e:
    print(f"\nError plotting grouped bar chart: {e}")
    raise Exception(f"Error plotting grouped bar chart: {e}")

# ################################################################ chart: 
# ############# DESCRIPTION: grouped vertical bar chart of actual_average_trade_count_between_resets and model_output_average_trade_count_between_resets by target_order_hash
# ############# X AXIS: target_order_hash
# ############# Y AXIS: actual_average_trade_count_between_resets and model_output_average_trade_count_between_resets
# ############# DF: order_hash and actual_average_trade_count_between_resets and model_output_average_trade_count_between_resets
# ################################################################
# prepare the df for the chart; df must be in long format
# Use melt to transform from wide to long format
reset_counts_average_long_chart_df = pd.melt(
    reset_counts_chart_df,
    id_vars=['target_order_hash', 'model_version'],  # Column(s) to keep as identifiers
    value_vars=['model_output_average_trade_count_between_resets', 'actual_average_trade_count_between_resets'], # Columns to unpivot
    var_name='metric_type',  # Name of the new column holding 'actual_median_trade_count_between_resets'/'model_output_median_trade_count_between_resets'
    value_name='average_auction_count_between_resets' # Name of the new column holding the corresponding values
)

# Clean up the 'metric_type' column values
reset_counts_average_long_chart_df['metric_type'] = reset_counts_average_long_chart_df['metric_type'].replace({
    'model_output_average_trade_count_between_resets': 'Modeled',
    'actual_average_trade_count_between_resets': 'Actual'
})

try:
    facet_grid = create_faceted_grouped_bar_chart(
        df=reset_counts_average_long_chart_df,
        category_column='target_order_hash',
        value_column='average_auction_count_between_resets',
        group_column='metric_type',
        facet_column='model_version', # Create subplots for each model version
        facet_wrap=3, # Arrange facets in 3 columns
        title='Actual vs. Modeled Average Auction Count Between Resets by Model Version',
        sharey=False, # Allow different y-axes (categories) per facet
        palette=metric_color_map
    )
    filename = "grouped_bar_chart_actual_vs_modeled_average_auction_count_between_resets.png"
    save_path = output_dir_str / filename
    print(f"Saving grouped bar chart to: {output_dir}/{filename}")
    # plt.show() # Show plot interactively
    facet_grid.savefig(save_path)
except Exception as e:
    print(f"\nError plotting grouped bar chart: {e}")
    raise Exception(f"Error plotting grouped bar chart: {e}")

# ################################################################ chart: 
# ############# DESCRIPTION: faceted histogram of median_trade_count_difference_modeled_vs_actual
# ############# X AXIS: median_trade_count_difference_modeled_vs_actual
# ############# COLOR: none
# ################################################################
try: 
    print("\nPlotting Median Differences...")
    g_median = create_faceted_histogram(
        orders_df,
        value_column='median_trade_count_difference_modeled_vs_actual',
        category_column='model_version',
        bins='auto',
        col_wrap=3
    )
    filename = "histogram_faceted_median_diff.png"
    save_path = output_dir_str / filename
    print(f"Saving histogram to: {output_dir}/{filename}")
    # plt.show() # Show plot interactively
    g_median.savefig(save_path)
except Exception as e:
    print(f"\nError plotting median histogram: {e}")
    raise Exception(f"Error plotting median histogram: {e}")

# ################################################################ chart: 
# ############# DESCRIPTION: faceted histogram of average_trade_count_difference_modeled_vs_actual
# ############# X AXIS: average_trade_count_difference_modeled_vs_actual
# ############# COLOR: none
# ################################################################
try: 
    print("\nPlotting Average Differences...")
    g_average = create_faceted_histogram(
        orders_df,
        value_column='average_trade_count_difference_modeled_vs_actual',
        category_column='model_version',
        bins='auto',
        col_wrap=3
    )
    filename = "histogram_faceted_average_diff.png"
    save_path = output_dir_str / filename
    print(f"Saving histogram to: {output_dir}/{filename}")
    # plt.show() # Show plot interactively
    g_average.savefig(save_path)
except Exception as e:
    print(f"\nError plotting avg histogram: {e}")
    raise Exception(f"Error plotting avg histogram: {e}")

# ################################################################ chart: 
# ############# DESCRIPTION: faceted histogram of std_trade_count_difference_modeled_vs_actual
# ############# X AXIS: std_trade_count_difference_modeled_vs_actual
# ############# COLOR: none
# ################################################################
try: 
    print("\nPlotting Standard Deviation Differences...")
    g_std = create_faceted_histogram(
        orders_df,
        value_column='std_trade_count_difference_modeled_vs_actual',
        category_column='model_version',
        bins='auto',
        col_wrap=3
    )
    filename = "histogram_faceted_std_diff.png"
    save_path = output_dir_str / filename
    print(f"Saving histogram to: {output_dir}/{filename}")
    # plt.show() # Show plot interactively
    g_std.savefig(save_path)
except Exception as e:
    print(f"\nError plotting std histogram: {e}")
    raise Exception(f"Error plotting std histogram: {e}")

# ################################################################ chart: 
# ############# DESCRIPTION: faceted histogram of reset_count_difference_modeled_vs_actual
# ############# X AXIS: reset_count_difference_modeled_vs_actual
# ############# COLOR: none
# ################################################################
try: 
    print("\nPlotting Reset Count Differences...")
    g_reset_count = create_faceted_histogram(
        orders_df,
        value_column='reset_count_difference_modeled_vs_actual',
        category_column='model_version',
        bins='auto',
        col_wrap=3
    )
    filename = "histogram_faceted_reset_count_diff.png"
    save_path = output_dir_str / filename
    print(f"Saving histogram to: {output_dir}/{filename}")
    # plt.show() # Show plot interactively
    g_reset_count.savefig(save_path)
except Exception as e:
    print(f"\nError plotting reset count histogram: {e}")
    raise Exception(f"Error plotting reset count histogram: {e}")

# ################################################################ chart: 
# ############# DESCRIPTION: faceted histogram of median_trade_count_difference_modeled_vs_actual_percentage
# ############# X AXIS: median_trade_count_difference_modeled_vs_actual_percentage
# ############# COLOR: none
# ################################################################
try: 
    print("\nPlotting Median Trade Count Percentage Differences...")
    g_median_trade_count_percentage = create_faceted_histogram(
        orders_df,
        value_column='median_trade_count_difference_modeled_vs_actual_percentage',
        category_column='model_version',
        bins='auto',
        col_wrap=3,
        x_formatter='percent_formatter'
    )
    filename = "histogram_faceted_median_trade_count_percentage_diff.png"
    save_path = output_dir_str / filename
    print(f"Saving histogram to: {output_dir}/{filename}")
    # plt.show() # Show plot interactively
    g_median_trade_count_percentage.savefig(save_path)
except Exception as e:
    print(f"\nError plotting median trade count percentage histogram: {e}")
    raise Exception(f"Error plotting median trade count percentage histogram: {e}")

# ################################################################ chart: 
# ############# DESCRIPTION: faceted histogram of average_trade_count_difference_modeled_vs_actual_percentage
# ############# X AXIS: average_trade_count_difference_modeled_vs_actual_percentage
# ############# COLOR: none
# ################################################################
try: 
    print("\nPlotting Average Trade Count Percentage Differences...")
    g_avg_trade_count_percentage = create_faceted_histogram(
        orders_df,
        value_column='average_trade_count_difference_modeled_vs_actual_percentage',
        category_column='model_version',
        bins='auto',
        col_wrap=3,
        x_formatter='percent_formatter'
    )
    filename = "histogram_faceted_avg_trade_count_percentage_diff.png"
    save_path = output_dir_str / filename
    print(f"Saving histogram to: {output_dir}/{filename}")
    # plt.show() # Show plot interactively
    g_avg_trade_count_percentage.savefig(save_path)
except Exception as e:
    print(f"\nError plotting avg trade count percentage histogram: {e}")
    raise Exception(f"Error plotting avg trade count percentage histogram: {e}")

# ################################################################ chart: 
# ############# DESCRIPTION: Q-Q Plot of median_trade_count_difference_modeled_vs_actual
# ############# X AXIS: median_trade_count_difference_modeled_vs_actual
# ############# COLOR: none
# ################################################################
print("\nPlotting Q-Q Plot...")
qq_figure = create_qq_plot(orders_df, 'median_trade_count_difference_modeled_vs_actual')
filename = "qq_plot_median_trade_count_difference_modeled_vs_actual.png"
save_path = output_dir_str / filename
print(f"Saving Q-Q Plot to: {output_dir}/{filename}")
# plt.show() # Show plot interactively
qq_figure.savefig(save_path)

print("\nCharts generated successfully")
