# run statistical tests on trade count between resets
# the main comparison is between the model output and the actual strategy trades

# null hypothesis: the trade count between resets is the same for the model output and the strategy trades
# alternative hypothesis: the trade count between resets is different for the model output and the strategy trades

# tests:
# 1) 

def basic_stats(df_trades_resets, df_all_trades, df_market_trades_clean, df_model_trade_count_in_reset):
    # get the variables, add them to a dictionary, and return the dictionary
    strategy_basic_stats = {
        "model_input_trade_count": df_market_trades_clean['tx_hash'].count(),
        "strategy_trade_count": df_trades_resets['tx_hash'].count(),
        "model_output_reset_count": df_model_trade_count_in_reset['trade_count_in_reset'].count(),
        "actual_reset_count": df_all_trades['resets'].sum(), # sum the number of true values in the resets column
        "model_output_median_trade_count_between_resets": df_model_trade_count_in_reset['trade_count_in_reset'][df_model_trade_count_in_reset['trade_count_in_reset'].isna() == False].median(),
        "actual_median_trade_count_between_resets": df_all_trades['rows_since_last_reset'][df_all_trades['resets'] == True].median(),
        "model_output_average_trade_count_between_resets": df_model_trade_count_in_reset['trade_count_in_reset'][df_model_trade_count_in_reset['trade_count_in_reset'].isna() == False].mean(),
        "actual_average_trade_count_between_resets": df_all_trades['rows_since_last_reset'][df_all_trades['resets'] == True].mean(),
        "median_trade_count_difference_modeled_vs_actual": df_model_trade_count_in_reset['trade_count_in_reset'][df_model_trade_count_in_reset['trade_count_in_reset'].isna() == False].median() - df_all_trades['rows_since_last_reset'][df_all_trades['resets'] == True].median(),
        "average_trade_count_difference_modeled_vs_actual": df_model_trade_count_in_reset['trade_count_in_reset'][df_model_trade_count_in_reset['trade_count_in_reset'].isna() == False].mean() - df_all_trades['rows_since_last_reset'][df_all_trades['resets'] == True].mean(),
    }

    # print the trade count of the model input file
    print(f"\nTrade count of the model input file: {strategy_basic_stats['model_input_trade_count']}")

    # print the count of the strategy trades
    print(f"Trade count in strategy: {strategy_basic_stats['strategy_trade_count']}")

    # print the count of resets from the strategy trades dataframe and the model output file
    print(f"\nNumber of resets:")
    print(f"Number of resets in the strategy trades: {strategy_basic_stats['actual_reset_count']}")
    # count the number of non-null values in the trade_count_in_reset column
    print(f"Number of resets in the model output file: {strategy_basic_stats['model_output_reset_count']}\n")

    # print the average trade count between resets in the model file and the concatenated strategy trades and market trades data
    print(f"\nAverage number of trades between resets in the model file: {strategy_basic_stats['model_output_average_trade_count_between_resets']}")
    print(f"Average number of trades between resets in the concatenated strategy trades and market trades data: {strategy_basic_stats['actual_average_trade_count_between_resets']}")

    # print the median trade count between resets in the model file and the concatenated strategy trades and market trades data
    print(f"\nMedian number of trades between resets in the model file: {strategy_basic_stats['model_output_median_trade_count_between_resets']}")
    print(f"Median number of trades between resets in the concatenated strategy trades and market trades data: {strategy_basic_stats['actual_median_trade_count_between_resets']}")

    # print the difference between modeled and actual trade count between resets
    print(f"\nDifference between modeled and actual average trade count between resets: {strategy_basic_stats['average_trade_count_difference_modeled_vs_actual']}")
    print(f"Difference between modeled and actual median trade count between resets: {strategy_basic_stats['median_trade_count_difference_modeled_vs_actual']}")

    return strategy_basic_stats


