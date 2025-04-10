## Raindex strategies - model validation

This module runs a statistical comparison between actual DSF strategy results and outputs from a modeled DSF strategy using real market data as inputs.

Use main.py as the entrypoint. The required parameters are model_file_path, network, target_order_hash, start_date_str, and end_date_str.

### Validation steps

- Get the order hash of the implemented strategy (e.g., 0xa3ee58f8abfb991496e9fc6b16ada0162a0513429b2061c4073a3a19588ef712)
- Choose a date range for the validation. The start date of the selected date range cannot be before the strategy implementation date
- Using the chosen date range retrieve market data for the strategy token pair (i.e., WFLR/cysFLR pool on Sparkdex; pool contract address: 0x6C58ac774f31aBe010437681C5365fD8d6a43adc)
- Use the market data as inputs to the model, https://docs.google.com/spreadsheets/d/1PCpkmEqENY3cXLrLDO7fVH5YQ5MyRMv7H8ErVcqDnkY/edit?gid=634861611#gid=634861611
  - The market data is input on the "Data" tab.
  - The required columns are block_number, dex_pool_address, tx_hash, token_amount_a, token_amount_b, timestamp
  - The first step should be to clear out any existing data in these columns
  - Note several things: (1) the Data tab is indifferent to which token is labeled as token_a or token_b, (2) the remaining columns cell reference the input data--these fields should not be modified or overwritten; and (3) the 'ABS USD' cell has a #REF error--ignore for now
- Rename the Google sheet to the standard format, {model_name}_{order_hash} e.g. model_1_0xa3ee58f8abfb991496e9fc6b16ada0162a0513429b2061c4073a3a19588ef712
- Navigate to the appropriate tab in the model e.g. 15M, 30M, etc.
- Download the Google sheet tab to your local computer as a *csv*
  - Set the main.py input field, {model_file_path} to the local model file path
     - e.g. {users/shared/downloads/model_1_0xa3ee58f8abfb991496e9fc6b16ada0162a0513429b2061c4073a3a19588ef712  - Test-15M.csv}
     - Note the file name on your local machine. csv file downloads are tab specific. The tab name is appended to the file name.

### Automated data input tests
- Validation will exit if the model file path is incorrect
- Validation will exit if it cannot find the columns "Date/time" and "trade_count_in_reset"
- Check actual market data input date range. Warn the user when:
  -  Market data start date is > start_date_str from main.py
  -  Market data end date is < end_date_str from main.py

### to do
- identify sample of order hashes for analysis
   - needs to be large enough to give us assurance in results
- merge strategy trades with market data in order to count trades between resets
- need testing scripts for basic outliers in this module
- ingestion for modeled outputs (all order hashes in sample)
   - ask Sid of he can help here
- run statistical comparison of trade count between resets actuals to modeled outputs
- explain methodology and results
