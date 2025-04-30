# run statistical tests on trade count between resets
# the main comparison is between the model output and the actual strategy trades
import pandas as pd
from scipy.stats import wilcoxon
# null hypothesis: the trade count between resets is the same for the model output and the strategy trades
# alternative hypothesis: the trade count between resets is different for the model output and the strategy trades

# tests:
# 1) 

def basic_stats(df_trades_resets, df_market_trades_clean, df_model_trade_count_in_reset):
    # get the variables, add them to a dictionary, and return the dictionary
    # set model outputs to zero if null, but not for actuals. Reasoning: we want to know if actuals are returning nulls. 
    # Model outputs are volitile at this stage, and nulls are likely extreme results. 
    # In the case of nulls, the difference between actual and modeled is the value of the actuals.

    # trade counts
    model_input_trade_count = df_market_trades_clean['tx_hash'].count()
    strategy_trade_count = df_trades_resets['tx_hash'].count()
    model_output_auction_count = df_model_trade_count_in_reset.shape[0]
    # reset counts
    model_output_reset_count = df_model_trade_count_in_reset['auction_count_in_reset'].count() # count will result in zero if no resets found
    actual_reset_count = df_trades_resets['resets'].sum()
    # calculate the median, average, and standard deviation of minutes between resets in the actual data
    actual_median_minutes_between_executed_auctions = df_trades_resets['minutes_since_last_executed_auction'].dropna().median()
    actual_average_minutes_between_executed_auctions = df_trades_resets['minutes_since_last_executed_auction'].dropna().mean()
    actual_std_minutes_between_executed_auctions = df_trades_resets['minutes_since_last_executed_auction'].dropna().std()
    # median and average trade count between resets
    model_output_median_trade_count_between_resets = df_model_trade_count_in_reset['auction_count_in_reset'].dropna().median()
    model_output_median_trade_count_between_resets = 0 if pd.isna(model_output_median_trade_count_between_resets) else model_output_median_trade_count_between_resets
    actual_median_trade_count_between_resets = df_trades_resets['rows_since_last_reset'][df_trades_resets['resets'] == True].median()
    model_output_average_trade_count_between_resets = df_model_trade_count_in_reset['auction_count_in_reset'].dropna().mean()
    model_output_average_trade_count_between_resets = 0 if pd.isna(model_output_average_trade_count_between_resets) else model_output_average_trade_count_between_resets
    actual_average_trade_count_between_resets = df_trades_resets['rows_since_last_reset'][df_trades_resets['resets'] == True].mean()
    # standard deviation of trade count between resets
    model_output_std_trade_count_between_resets = df_model_trade_count_in_reset['auction_count_in_reset'].dropna().std()
    model_output_std_trade_count_between_resets = 0 if pd.isna(model_output_std_trade_count_between_resets) else model_output_std_trade_count_between_resets
    actual_std_trade_count_between_resets = df_trades_resets['rows_since_last_reset'][df_trades_resets['resets'] == True].std()
    # difference between modeled auction count and actual auction count
    auction_count_difference_modeled_vs_actual = model_output_auction_count - strategy_trade_count
    # difference between modeled reset count and actual reset count
    reset_count_difference_modeled_vs_actual = model_output_reset_count - actual_reset_count
    # difference between modeled and actual trade count between resets
    median_trade_count_difference_modeled_vs_actual = model_output_median_trade_count_between_resets - actual_median_trade_count_between_resets
    average_trade_count_difference_modeled_vs_actual = model_output_average_trade_count_between_resets - actual_average_trade_count_between_resets
    std_trade_count_difference_modeled_vs_actual = model_output_std_trade_count_between_resets - actual_std_trade_count_between_resets
    # the difference between actual and modeled trade count between resets as a percentage of model_input_trade_count
    if model_input_trade_count != 0:
        median_trade_count_difference_modeled_vs_actual_percentage = median_trade_count_difference_modeled_vs_actual / model_input_trade_count
        average_trade_count_difference_modeled_vs_actual_percentage = average_trade_count_difference_modeled_vs_actual / model_input_trade_count
    else: 
        median_trade_count_difference_modeled_vs_actual_percentage = 0
        average_trade_count_difference_modeled_vs_actual_percentage = 0
    
    # compile the dictionary
    strategy_basic_stats = {
        "model_input_trade_count": model_input_trade_count,
        "strategy_trade_count": strategy_trade_count,
        "model_output_auction_count": model_output_auction_count,
        "model_output_reset_count": model_output_reset_count,
        "actual_reset_count": actual_reset_count,
        "actual_median_minutes_between_executed_auctions": actual_median_minutes_between_executed_auctions,
        "actual_average_minutes_between_executed_auctions": actual_average_minutes_between_executed_auctions,
        "actual_std_minutes_between_executed_auctions": actual_std_minutes_between_executed_auctions,
        "model_output_median_trade_count_between_resets": model_output_median_trade_count_between_resets,
        "actual_median_trade_count_between_resets": actual_median_trade_count_between_resets,
        "model_output_average_trade_count_between_resets": model_output_average_trade_count_between_resets,
        "actual_average_trade_count_between_resets": actual_average_trade_count_between_resets,
        "model_output_std_trade_count_between_resets": model_output_std_trade_count_between_resets,
        "actual_std_trade_count_between_resets": actual_std_trade_count_between_resets,
        "auction_count_difference_modeled_vs_actual": auction_count_difference_modeled_vs_actual,
        "reset_count_difference_modeled_vs_actual": reset_count_difference_modeled_vs_actual,
        "median_trade_count_difference_modeled_vs_actual": median_trade_count_difference_modeled_vs_actual,
        "average_trade_count_difference_modeled_vs_actual": average_trade_count_difference_modeled_vs_actual,
        "std_trade_count_difference_modeled_vs_actual": std_trade_count_difference_modeled_vs_actual,
        "median_trade_count_difference_modeled_vs_actual_percentage": median_trade_count_difference_modeled_vs_actual_percentage,
        "average_trade_count_difference_modeled_vs_actual_percentage": average_trade_count_difference_modeled_vs_actual_percentage,
    }

    # print basic stats
    print("Printing basic stats about the actual strategy data, model input data, and model output data")
    print("\nSummary counts:")
    print(f"Trade count of the model input file: {model_input_trade_count}")
    print(f"Trade count in strategy: {strategy_trade_count}") 
    print(f"Number of auctions in the model output file: {model_output_auction_count}")
    print(f"Number of resets in the strategy trades: {actual_reset_count}")
    print(f"Number of resets in the model output file: {model_output_reset_count}")
    print("\nMinutes between executed auctions:")
    print(f"Average number of minutes between executed auctions in the actual strategy data: {actual_average_minutes_between_executed_auctions}")
    print(f"Median number of minutes between executed auctions in the actual strategy data: {actual_median_minutes_between_executed_auctions}")
    print(f"Standard deviation of minutes between executed auctions in the actual strategy data: {actual_std_minutes_between_executed_auctions}")
    print("\nTrade/auction count between resets mean, median, standard deviation:")
    print(f"Average number of trades between resets in the actual strategy data: {actual_average_trade_count_between_resets}")
    print(f"Average number of auctions between resets in the model output file: {model_output_average_trade_count_between_resets}")
    print(f"Median number of trades between resets in the actual strategy data: {actual_median_trade_count_between_resets}")
    print(f"Median number of auctions between resets in the model output file: {model_output_median_trade_count_between_resets}")
    print(f"Standard deviation of trade count between resets in the actual strategy data: {actual_std_trade_count_between_resets}")
    print(f"Standard deviation of auction count between resets in the model output file: {model_output_std_trade_count_between_resets}")
    print("\nDifference between modeled and actual trade/auction count between resets:")
    print(f"Difference between modeled and actual auction count: {auction_count_difference_modeled_vs_actual}")
    print(f"Difference between modeled and actual reset count: {reset_count_difference_modeled_vs_actual}")
    print(f"Difference between modeled and actual average trade/auction count between resets: {average_trade_count_difference_modeled_vs_actual}")
    print(f"Difference between modeled and actual median trade/auction count between resets: {median_trade_count_difference_modeled_vs_actual}")
    print(f"Difference between modeled and actual standard deviation of trade/auction count between resets: {std_trade_count_difference_modeled_vs_actual}")
    print(f"Difference between modeled and actual average trade/auction count between resets as a percentage of model_input_trade_count: {average_trade_count_difference_modeled_vs_actual_percentage}")
    print(f"Difference between modeled and actual median trade/auction count between resets as a percentage of model_input_trade_count: {median_trade_count_difference_modeled_vs_actual_percentage}")
    return strategy_basic_stats

# test the hypothesis: mean and median difference between modeled and actual trade count between resets is 0
def trade_count_between_resets_difference_test(orders_df):
    
    # check that orders_df is a dataframe
    if not isinstance(orders_df, pd.DataFrame):
        print("orders_df is not a dataframe")
        raise Exception("orders_df is not a dataframe")
    
    # check if the orders are empty
    if orders_df.empty:
        print("No orders found in the aggregated results")
        raise Exception("No orders found in the aggregated results")
    
    # get the subset of columns for the test
    orders_df_diff_modeled_vs_actual = orders_df[['model_version', 'auction_count_difference_modeled_vs_actual', 'reset_count_difference_modeled_vs_actual', 'median_trade_count_difference_modeled_vs_actual', 'average_trade_count_difference_modeled_vs_actual', 'std_trade_count_difference_modeled_vs_actual', 'median_trade_count_difference_modeled_vs_actual_percentage', 'average_trade_count_difference_modeled_vs_actual_percentage']]

    # create a dictionary to store the results
    stats_results_dict = {}

    # for each model version, run the test
    for model_version in orders_df_diff_modeled_vs_actual['model_version'].unique():
        # get the subset of data for the current model version
        orders_df_diff_modeled_vs_actual_subset = orders_df_diff_modeled_vs_actual[orders_df_diff_modeled_vs_actual['model_version'] == model_version]

        # get the auction count difference
        auction_count_difference_modeled_vs_actual = pd.to_numeric(orders_df_diff_modeled_vs_actual_subset['auction_count_difference_modeled_vs_actual'], errors='coerce').dropna()

        # get the count of resets
        reset_count_difference_modeled_vs_actual = pd.to_numeric(orders_df_diff_modeled_vs_actual_subset['reset_count_difference_modeled_vs_actual'], errors='coerce').dropna()

        # get the median; convert to numeric and drop na
        median_trade_count_between_resets_difference_modeled_vs_actual = pd.to_numeric(orders_df_diff_modeled_vs_actual_subset['median_trade_count_difference_modeled_vs_actual'], errors='coerce').dropna()

        # get the average; convert to numeric and drop na
        average_trade_count_between_resets_difference_modeled_vs_actual = pd.to_numeric(orders_df_diff_modeled_vs_actual_subset['average_trade_count_difference_modeled_vs_actual'], errors='coerce').dropna()

        # get the std; convert to numeric and drop na
        std_trade_count_between_resets_difference_modeled_vs_actual = pd.to_numeric(orders_df_diff_modeled_vs_actual_subset['std_trade_count_difference_modeled_vs_actual'], errors='coerce').dropna()

        # get the median trade count percentage; convert to numeric and drop na
        median_trade_count_between_resets_difference_modeled_vs_actual_percentage = pd.to_numeric(orders_df_diff_modeled_vs_actual_subset['median_trade_count_difference_modeled_vs_actual_percentage'], errors='coerce').dropna()

        # get the average trade count percentage; convert to numeric and drop na
        average_trade_count_between_resets_difference_modeled_vs_actual_percentage = pd.to_numeric(orders_df_diff_modeled_vs_actual_subset['average_trade_count_difference_modeled_vs_actual_percentage'], errors='coerce').dropna()

        # calculate mean, median, skew, and kurtosis for each metric
        # auction count difference
        auction_count_difference_mean = auction_count_difference_modeled_vs_actual.mean()
        auction_count_difference_median = auction_count_difference_modeled_vs_actual.median()
        # auction_count_difference_skew = auction_count_difference_modeled_vs_actual.skew()
        # auction_count_difference_kurtosis = auction_count_difference_modeled_vs_actual.kurtosis()

        # reset count difference
        reset_count_difference_mean = reset_count_difference_modeled_vs_actual.mean()
        reset_count_difference_median = reset_count_difference_modeled_vs_actual.median()
        # reset_count_difference_skew = reset_count_difference_modeled_vs_actual.skew()
        # reset_count_difference_kurtosis = reset_count_difference_modeled_vs_actual.kurtosis()

        # median trade count between resets difference
        median_difference_trade_count_between_resets_mean = median_trade_count_between_resets_difference_modeled_vs_actual.mean()
        median_difference_trade_count_between_resets_median = median_trade_count_between_resets_difference_modeled_vs_actual.median()
        # median_difference_trade_count_between_resets_skew = median_trade_count_between_resets_difference_modeled_vs_actual.skew()
        # median_difference_trade_count_between_resets_kurtosis = median_trade_count_between_resets_difference_modeled_vs_actual.kurtosis()

        # average trade count between resets difference
        average_difference_trade_count_between_resets_mean = average_trade_count_between_resets_difference_modeled_vs_actual.mean()
        average_difference_trade_count_between_resets_median = average_trade_count_between_resets_difference_modeled_vs_actual.median()
        # average_difference_trade_count_between_resets_skew = average_trade_count_between_resets_difference_modeled_vs_actual.skew()
        # average_difference_trade_count_between_resets_kurtosis = average_trade_count_between_resets_difference_modeled_vs_actual.kurtosis()

        # std trade count between resets difference
        std_difference_trade_count_between_resets_mean = std_trade_count_between_resets_difference_modeled_vs_actual.mean()
        std_difference_trade_count_between_resets_median = std_trade_count_between_resets_difference_modeled_vs_actual.median()
        # std_difference_trade_count_between_resets_skew = std_trade_count_between_resets_difference_modeled_vs_actual.skew()
        # std_difference_trade_count_between_resets_kurtosis = std_trade_count_between_resets_difference_modeled_vs_actual.kurtosis()

        # median trade count between resets difference percentage
        median_difference_trade_count_between_resets_percentage_mean = median_trade_count_between_resets_difference_modeled_vs_actual_percentage.mean()
        median_difference_trade_count_between_resets_percentage_median = median_trade_count_between_resets_difference_modeled_vs_actual_percentage.median()
        # median_difference_trade_count_between_resets_percentage_skew = median_trade_count_between_resets_difference_modeled_vs_actual_percentage.skew()
        # median_difference_trade_count_between_resets_percentage_kurtosis = median_trade_count_between_resets_difference_modeled_vs_actual_percentage.kurtosis()

        # average trade count between resets difference percentage
        average_difference_trade_count_between_resets_percentage_mean = average_trade_count_between_resets_difference_modeled_vs_actual_percentage.mean()
        average_difference_trade_count_between_resets_percentage_median = average_trade_count_between_resets_difference_modeled_vs_actual_percentage.median()
        # average_difference_trade_count_between_resets_percentage_skew = average_trade_count_between_resets_difference_modeled_vs_actual_percentage.skew()
        # average_difference_trade_count_between_resets_percentage_kurtosis = average_trade_count_between_resets_difference_modeled_vs_actual_percentage.kurtosis()

        # print the results
        print(f"\n{model_version} model type:")
        print(f"Auction Count Difference Mean: {auction_count_difference_mean}")
        print(f"Auction Count Difference Median: {auction_count_difference_median}")
        # print(f"Auction Count Difference Skew: {auction_count_difference_skew}")
        # print(f"Auction Count Difference Kurtosis: {auction_count_difference_kurtosis}")
        print(f"Reset Count Difference Mean: {reset_count_difference_mean}")
        print(f"Reset Count Difference Median: {reset_count_difference_median}")
        # print(f"Reset Count Difference Skew: {reset_count_difference_skew}")
        # print(f"Reset Count Difference Kurtosis: {reset_count_difference_kurtosis}")
        print(f"Median Trade Count Between Resets Difference Mean: {median_difference_trade_count_between_resets_mean}")
        print(f"Median Trade Count Between Resets Difference Median: {median_difference_trade_count_between_resets_median}")
        # print(f"Median Trade Count Between Resets Difference Skew: {median_difference_trade_count_between_resets_skew}")
        # print(f"Median Trade Count Between Resets Difference Kurtosis: {median_difference_trade_count_between_resets_kurtosis}")
        print(f"Average Trade Count Between Resets Difference Mean: {average_difference_trade_count_between_resets_mean}")
        print(f"Average Trade Count Between Resets Difference Median: {average_difference_trade_count_between_resets_median}")
        # print(f"Average Trade Count Between Resets Difference Skew: {average_difference_trade_count_between_resets_skew}")
        # print(f"Average Trade Count Between Resets Difference Kurtosis: {average_difference_trade_count_between_resets_kurtosis}")
        print(f"Std Trade Count Between Resets Difference Mean: {std_difference_trade_count_between_resets_mean}")
        print(f"Std Trade Count Between Resets Difference Median: {std_difference_trade_count_between_resets_median}")
        # print(f"Std Trade Count Between Resets Difference Skew: {std_difference_trade_count_between_resets_skew}")
        # print(f"Std Trade Count Between Resets Difference Kurtosis: {std_difference_trade_count_between_resets_kurtosis}")
        print(f"Median Trade Count Between Resets Difference Percentage Mean: {median_difference_trade_count_between_resets_percentage_mean}")
        print(f"Median Trade Count Between Resets Difference Percentage Median: {median_difference_trade_count_between_resets_percentage_median}")
        # print(f"Median Trade Count Between Resets Difference Percentage Skew: {median_difference_trade_count_between_resets_percentage_skew}")
        # print(f"Median Trade Count Between Resets Difference Percentage Kurtosis: {median_difference_trade_count_between_resets_percentage_kurtosis}")
        print(f"Average Trade Count Between Resets Difference Percentage Mean: {average_difference_trade_count_between_resets_percentage_mean}")
        print(f"Average Trade Count Between Resets Difference Percentage Median: {average_difference_trade_count_between_resets_percentage_median}")
        # print(f"Average Trade Count Between Resets Difference Percentage Skew: {average_difference_trade_count_between_resets_percentage_skew}")
        # print(f"Average Trade Count Between Resets Difference Percentage Kurtosis: {average_difference_trade_count_between_resets_percentage_kurtosis}")

        # --- Define Hypothesis ---
        # H0: The median of the differences is 0.
        # Ha: The median of the differences is not 0. (two-sided test)

        # --- Perform the Wilcoxon Signed-Rank Test ---
        # Pass the cleaned data series directly.
        # By default, it tests against a median of 0.
        # 'alternative='two-sided'' is the default, explicitly stated here for clarity.
        # Consider adding correction=True if you have a small sample size or many ties
        # run the test against difference in auction count
        auction_count_difference_statistic, auction_count_difference_p_value = wilcoxon(auction_count_difference_modeled_vs_actual, alternative='two-sided', correction=True)

        # run the test against difference in reset count
        reset_count_difference_statistic, reset_count_difference_p_value = wilcoxon(reset_count_difference_modeled_vs_actual, alternative='two-sided', correction=True)

        # run the test against difference in median trade count between resets
        median_trade_count_between_resets_statistic, median_trade_count_between_resets_p_value = wilcoxon(median_trade_count_between_resets_difference_modeled_vs_actual, alternative='two-sided', correction=True)

        # run the test against difference in average trade count between resets
        average_trade_count_between_resets_statistic, average_trade_count_between_resets_p_value = wilcoxon(average_trade_count_between_resets_difference_modeled_vs_actual, alternative='two-sided', correction=True)

        # run the test against difference in std trade count between resets
        std_trade_count_between_resets_statistic, std_trade_count_between_resets_p_value = wilcoxon(std_trade_count_between_resets_difference_modeled_vs_actual, alternative='two-sided', correction=True)

        # run the test against difference in median trade count between resets percentage
        median_trade_count_between_resets_difference_percentage_statistic, median_trade_count_between_resets_difference_percentage_p_value = wilcoxon(median_trade_count_between_resets_difference_modeled_vs_actual_percentage, alternative='two-sided', correction=True)

        # run the test against difference in average trade count between resets percentage
        average_trade_count_between_resets_difference_percentage_statistic, average_trade_count_between_resets_difference_percentage_p_value = wilcoxon(average_trade_count_between_resets_difference_modeled_vs_actual_percentage, alternative='two-sided', correction=True)

        # print the results
        print(f"\nWilcoxon Signed-Rank Test Results for {model_version} model type:")
        print(f"Auction Count Statistic: {auction_count_difference_statistic}")
        print(f"Auction Count P-value: {auction_count_difference_p_value}")
        print(f"Reset Count Statistic: {reset_count_difference_statistic}")
        print(f"Reset Count P-value: {reset_count_difference_p_value}")
        print(f"Median Statistic: {median_trade_count_between_resets_statistic}")
        print(f"Median P-value: {median_trade_count_between_resets_p_value}")
        print(f"Average Statistic: {average_trade_count_between_resets_statistic}")
        print(f"Average P-value: {average_trade_count_between_resets_p_value}")
        print(f"Std Statistic: {std_trade_count_between_resets_statistic}")
        print(f"Std P-value: {std_trade_count_between_resets_p_value}")
        print(f"Median Trade Count Between Resets Difference Percentage Statistic: {median_trade_count_between_resets_difference_percentage_statistic}")
        print(f"Median Trade Count Between Resets Difference Percentage P-value: {median_trade_count_between_resets_difference_percentage_p_value}")
        print(f"Average Trade Count Between Resets Difference Percentage Statistic: {average_trade_count_between_resets_difference_percentage_statistic}")
        print(f"Average Trade Count Between Resets Difference Percentage P-value: {average_trade_count_between_resets_difference_percentage_p_value}")

        # store the results in the dictionary
        stats_results_dict[model_version] = {
            "auction_count_difference_mean": auction_count_difference_mean,
            "auction_count_difference_median": auction_count_difference_median,
            # "auction_count_difference_skew": auction_count_difference_skew,
            # "auction_count_difference_kurtosis": auction_count_difference_kurtosis, 
            "reset_count_difference_mean": reset_count_difference_mean,
            "reset_count_difference_median": reset_count_difference_median,
            # "reset_count_difference_skew": reset_count_difference_skew,
            # "reset_count_difference_kurtosis": reset_count_difference_kurtosis, 
            "median_difference_trade_count_between_resets_mean": median_difference_trade_count_between_resets_mean,
            "median_difference_trade_count_between_resets_median": median_difference_trade_count_between_resets_median,
            # "median_difference_trade_count_between_resets_skew": median_difference_trade_count_between_resets_skew,
            # "median_difference_trade_count_between_resets_kurtosis": median_difference_trade_count_between_resets_kurtosis,
            "average_difference_trade_count_between_resets_mean": average_difference_trade_count_between_resets_mean,
            "average_difference_trade_count_between_resets_median": average_difference_trade_count_between_resets_median,
            # "average_difference_trade_count_between_resets_skew": average_difference_trade_count_between_resets_skew,
            # "average_difference_trade_count_between_resets_kurtosis": average_difference_trade_count_between_resets_kurtosis,
            "std_difference_trade_count_between_resets_mean": std_difference_trade_count_between_resets_mean,
            "std_difference_trade_count_between_resets_median": std_difference_trade_count_between_resets_median,
            # "std_difference_trade_count_between_resets_skew": std_difference_trade_count_between_resets_skew,
            # "std_difference_trade_count_between_resets_kurtosis": std_difference_trade_count_between_resets_kurtosis,
            "median_difference_trade_count_between_resets_percentage_mean": median_difference_trade_count_between_resets_percentage_mean,
            "median_difference_trade_count_between_resets_percentage_median": median_difference_trade_count_between_resets_percentage_median,
            # "median_difference_trade_count_between_resets_percentage_skew": median_difference_trade_count_between_resets_percentage_skew,
            # "median_difference_trade_count_between_resets_percentage_kurtosis": median_difference_trade_count_between_resets_percentage_kurtosis,
            "average_difference_trade_count_between_resets_percentage_mean": average_difference_trade_count_between_resets_percentage_mean,
            "average_difference_trade_count_between_resets_percentage_median": average_difference_trade_count_between_resets_percentage_median,
            # "average_difference_trade_count_between_resets_percentage_skew": average_difference_trade_count_between_resets_percentage_skew,
            # "average_difference_trade_count_between_resets_percentage_kurtosis": average_difference_trade_count_between_resets_percentage_kurtosis,
            "auction_count_difference_statistic": auction_count_difference_statistic,
            "auction_count_difference_p_value": auction_count_difference_p_value,
            "reset_count_difference_statistic": reset_count_difference_statistic,
            "reset_count_difference_p_value": reset_count_difference_p_value,
            "median_trade_count_between_resets_statistic": median_trade_count_between_resets_statistic,
            "median_trade_count_between_resets_p_value": median_trade_count_between_resets_p_value,
            "average_trade_count_between_resets_statistic": average_trade_count_between_resets_statistic,
            "average_trade_count_between_resets_p_value": average_trade_count_between_resets_p_value,
            "std_trade_count_between_resets_statistic": std_trade_count_between_resets_statistic,
            "std_trade_count_between_resets_p_value": std_trade_count_between_resets_p_value,
            "median_trade_count_between_resets_difference_percentage_statistic": median_trade_count_between_resets_difference_percentage_statistic,
            "median_trade_count_between_resets_difference_percentage_p_value": median_trade_count_between_resets_difference_percentage_p_value,
            "average_trade_count_between_resets_difference_percentage_statistic": average_trade_count_between_resets_difference_percentage_statistic,
            "average_trade_count_between_resets_difference_percentage_p_value": average_trade_count_between_resets_difference_percentage_p_value,
        }
    
    # check if the dictionary is empty
    if not stats_results_dict:
        print("No results found in the stats dictionary")
        raise Exception("No results found in the stats dictionary")

    # return the results in a dictionary
    return stats_results_dict

    # run a test on m15_test model type
    
