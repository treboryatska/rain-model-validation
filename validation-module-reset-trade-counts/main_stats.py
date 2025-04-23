# main script to run the stats from aggregated results, previously created using main_batch.py
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from batch import get_aggregated_results
from stats import trade_count_between_resets_difference_test
from check import check_aggregated_results
from charts import create_scatter_plot, create_faceted_histogram, create_qq_plot

# get the aggregated results
aggregated_results_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRt8SEy6hW4MSoVI4iI8c_dFpiZ4aqklPlBJW7XXn8UHvWEveO5Wt2WxyRlj-DPvWkns1lQ1sYlHDQn/pub?gid=1252902757&single=true&output=csv'

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


# chart 1: faceted histogram of median_trade_count_difference_modeled_vs_actual
# x axis: median_trade_count_difference_modeled_vs_actual
# color: none
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

# chart 2: faceted histogram of average_trade_count_difference_modeled_vs_actual
# x axis: average_trade_count_difference_modeled_vs_actual
# color: none
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

# chart 3: faceted histogram of std_trade_count_difference_modeled_vs_actual
# x axis: std_trade_count_difference_modeled_vs_actual
# color: none
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

# chart 4: faceted histogram of reset_count_difference_modeled_vs_actual
# x axis: reset_count_difference_modeled_vs_actual
# color: none
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

# chart 5: faceted histogram of median_trade_count_difference_modeled_vs_actual_percentage
# x axis: median_trade_count_difference_modeled_vs_actual_percentage
# color: none
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

# chart 6: faceted histogram of average_trade_count_difference_modeled_vs_actual_percentage
# x axis: average_trade_count_difference_modeled_vs_actual_percentage
# color: none
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

print("\nPlotting Q-Q Plot...")
qq_figure = create_qq_plot(orders_df, 'median_trade_count_difference_modeled_vs_actual')
filename = "qq_plot_median_trade_count_difference_modeled_vs_actual.png"
save_path = output_dir_str / filename
print(f"Saving Q-Q Plot to: {output_dir}/{filename}")
# plt.show() # Show plot interactively
qq_figure.savefig(save_path)

# chart 2: one quadrant scatter plot of median_trade_count_between_resets_p_value and median_trade_count_between_resets_statistic 
# x axis: median_trade_count_between_resets_p_value
# y axis: median_trade_count_between_resets_statistic
# color: model_version
# chart_df = test_results_df[['median_trade_count_between_resets_p_value', 'median_trade_count_between_resets_statistic', 'model_version']].copy()
# try:
#     ax = create_scatter_plot(chart_df, 'median_trade_count_between_resets_p_value', 'median_trade_count_between_resets_statistic', 'model_version')
#     plt.show()
# except (TypeError, KeyError, ValueError) as e:
#      print(f"Error creating plot: {e}")
